"""The 13-stage NDIM journey (capture -> analysis -> digital twin -> strategy -> export) as an engine API.

The workbench runs these stages in the browser. This module gives outside tools (the DeerFlow chat via ndim-mcp) the
same journey, server-side and checkpointed per workspace, so a researcher can be guided through it in conversation.
It reuses the engine's deterministic methods (rule-based encoder and diagnosis, run_digital_twin, the evidence grade)
and ports the workbench's browser-only stages (regional analysis, knowledge graph, inoculation drafts) to Python.

Deliberate differences from the workbench, all in the direction of not inventing evidence:
- Field feedback (stage 7) has no defaults; the workbench pre-fills an observed adoption of 0.48.
- The Bayesian stage (8) never treats model output as observations. Without an observed adoption series from the
  researcher it updates only the signal priors and says so.
- The RL stage (9) ranks actions by the tool's fixed assumed effects, deterministically, and discloses them.
- Only the rule-based encoder runs here: no remote model sees the evidence.
- Evidence review (3), field feedback (7) and the policy export (13) need the researcher's own words.
"""
import hashlib
import json
import re
from typing import Literal
from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from . import engine_store as store
from .encoding import encode_rule_based
from .engine_tools import LIMITS, fingerprint, scientific_checks
from .inoculation import aggregate_inoculation_parameters, diagnose_inoculation_rule_based
from .journey_text import INTRO, presentation
from .modelling import model_assumptions, run_digital_twin
from .pipeline import evidence_grade
from .schemas import EncodedNarrative, EncodingMode, InoculationEncoding, ModelMode, NarrativeMetadata, NarrativeRecord

router = APIRouter(prefix='/engine', tags=['scientific-engine'])

STAGES = [
    {'id': 'intake', 'number': 1, 'phase': 'Evidence', 'title': 'Narrative intake',
     'does': 'Collects the stories or field notes, each with its place, source, period, language and consent.',
     'needs': [], 'researcher_decision': False},
    {'id': 'gate', 'number': 2, 'phase': 'Evidence', 'title': 'SDMX gate',
     'does': 'Checks each record against the input contract: required metadata, English text, personal-data and '
             'prompt-injection patterns, duplicates. Runs automatically on intake.',
     'needs': ['intake'], 'researcher_decision': False},
    {'id': 'repository', 'number': 3, 'phase': 'Evidence', 'title': 'Repository',
     'does': 'The researcher accepts or rejects each record. Only accepted records reach any model.',
     'needs': ['gate'], 'researcher_decision': True},
    {'id': 'encoding', 'number': 4, 'phase': 'Encode', 'title': 'Encoding',
     'does': 'Scores each accepted record for trust, adoption barrier, themes and misinformation risk with the '
             'English keyword encoder.',
     'needs': ['repository'], 'researcher_decision': False},
    {'id': 'compartmental', 'number': 5, 'phase': 'Model', 'title': 'Compartmental model',
     'does': 'Population-level adoption over time (S, M, T, I, R compartments) from the encoded signals.',
     'needs': ['encoding'], 'researcher_decision': False},
    {'id': 'agents', 'number': 6, 'phase': 'Model', 'title': 'Agent-based model',
     'does': 'Household-level proxy with peer and media effects, as a second view of the same signals.',
     'needs': ['encoding'], 'researcher_decision': False},
    {'id': 'digital', 'number': 7, 'phase': 'Twin', 'title': 'Digital twin',
     'does': 'Feeds the researcher\'s field observations (observed adoption, trust and barrier shifts) back into a '
             'hybrid re-run. Needs real observations; there are no defaults.',
     'needs': ['compartmental'], 'researcher_decision': True},
    {'id': 'bayes', 'number': 8, 'phase': 'Twin', 'title': 'Bayesian update',
     'does': 'Updates the trust and barrier priors with the encoded signals; with an observed adoption series it '
             'also fits the adoption curve to those observations.',
     'needs': ['digital'], 'researcher_decision': False},
    {'id': 'rl', 'number': 9, 'phase': 'Twin', 'title': 'RL optimizer',
     'does': 'Ranks four candidate actions by the tool\'s fixed assumed effects under the updated signals. The '
             'effects are assumptions set in the tool, not estimates.',
     'needs': ['bayes'], 'researcher_decision': False},
    {'id': 'regional', 'number': 10, 'phase': 'Strategy', 'title': 'Regional analysis',
     'does': 'Groups the encoded evidence by place, or pools it. Optional.',
     'needs': ['encoding'], 'researcher_decision': False, 'optional': True},
    {'id': 'graph', 'number': 11, 'phase': 'Strategy', 'title': 'Knowledge graph',
     'does': 'Connects places, themes and trust/barrier signals as nodes and edges.',
     'needs': ['encoding'], 'researcher_decision': False},
    {'id': 'inoculation', 'number': 12, 'phase': 'Strategy', 'title': 'Inoculation lab',
     'does': 'Drafts pre-bunking, refutation and short counter-messages from the diagnosis, and shows the tool\'s '
             'illustrative before/during/after adoption curves. Drafts need human review before any use.',
     'needs': ['encoding', 'compartmental', 'agents'], 'researcher_decision': False},
    {'id': 'policy', 'number': 13, 'phase': 'Export', 'title': 'Policy output',
     'does': 'Assembles the evidence grade, policy readiness, model summary and the audit trail into a draft for '
             'human review.',
     'needs': ['encoding', 'compartmental', 'agents', 'digital', 'bayes', 'rl', 'graph', 'inoculation'],
     'researcher_decision': True},
]
BY_ID = {stage['id']: stage for stage in STAGES}


def dependents(stage_id):
    """Stages that read stage_id directly or through another stage, in journey order."""
    found = {stage_id}
    for stage in STAGES:  # needs always point backwards, so one ordered pass is enough
        if found & set(stage['needs']):
            found.add(stage['id'])
    return [stage['id'] for stage in STAGES if stage['id'] in found - {stage_id}]


RUNNABLE = ('encoding', 'compartmental', 'agents', 'digital', 'bayes', 'rl', 'regional', 'graph', 'inoculation', 'policy')
PRIORS = {'trust_a': 6.0, 'trust_b': 4.0, 'barrier_a': 4.0, 'barrier_b': 6.0}
# The workbench's fallback optimizer: fixed assumed lifts and costs per action (api_routes._fallback_rl).
RL_ACTIONS = {'none': (0.0, 0.0), 'demand_generation': (0.12, 0.08), 'consumer_subsidy': (0.16, 0.18),
              'supply_chain': (0.13, 0.14)}
INJECTION = ('ignore previous', 'ignore all previous', 'system prompt', 'developer message', 'reveal your prompt',
             'jailbreak', 'override instructions', 'you are now', 'do not follow', 'delete the rules', '<script', 'base64')


class EvidenceItem(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
    text: str = Field(min_length=1, max_length=20000)
    admin_unit: str = Field(min_length=1, max_length=240, description='Place, e.g. "Kicukiro / Niboye".')
    source_name: str = Field(min_length=1, max_length=240)
    period: str = Field(min_length=1, max_length=60, description='When the evidence was collected, e.g. "2026-Q2".')
    source_type: Literal['field_note', 'interview', 'focus_group', 'survey_open_text', 'citizen_report', 'document'] = 'field_note'
    language: Literal['en', 'rw', 'fr', 'other'] = 'en'
    consent: Literal['synthetic', 'research_use', 'unconfirmed'] = 'unconfirmed'


class JourneyCreate(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
    question: str = Field(min_length=8, max_length=1000)
    country: str = Field(default='Rwanda', min_length=2, max_length=80)


class EvidenceRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    records: list[EvidenceItem] = Field(min_length=1, max_length=50)


class Decision(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
    record_id: str
    decision: Literal['accept', 'reject']
    reason: str | None = Field(default=None, max_length=400)


class ReviewRequest(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
    decisions: list[Decision] = Field(min_length=1, max_length=50)
    # Verbatim and possibly short ("Yes."): a 12-character minimum pushed a live agent to compose a longer approval.
    approval_statement: str = Field(min_length=2, max_length=1000)


class StageRequest(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True, allow_inf_nan=False)
    horizon_days: int = Field(default=180, ge=7, le=365)
    peer_effect: float = Field(default=0.08, ge=0, le=1)
    media_effect: float = Field(default=0.05, ge=0, le=1)
    observed_adoption: float | None = Field(default=None, ge=0, le=1)
    trust_shift: float | None = Field(default=None, ge=-1, le=1)
    barrier_shift: float | None = Field(default=None, ge=-1, le=1)
    observed_series: list[float] | None = Field(default=None, min_length=3, max_length=365)
    feedback_note: str | None = Field(default=None, max_length=1000)
    priors: dict[str, float] | None = None
    regional_mode: Literal['isolated', 'grouped'] = 'isolated'
    regional_target: Literal['barrier', 'trust', 'diffusion'] = 'barrier'
    audience: Literal['households', 'health_workers', 'community_leaders', 'policy_makers'] = 'households'
    tone: Literal['clear', 'warm', 'formal'] = 'clear'
    apply_to_twin: bool = False
    approval_statement: str | None = Field(default=None, min_length=2, max_length=1000)


def avg(values, fallback):
    values = [value for value in values if isinstance(value, (int, float))]
    return sum(values) / len(values) if values else fallback


def clamp01(value):
    return min(1.0, max(0.0, value))


def top_items(items, limit):
    counts = {}
    for item in items:
        if item:
            counts[item] = counts.get(item, 0) + 1
    return [name for name, _ in sorted(counts.items(), key=lambda pair: -pair[1])[:limit]]


def folder(workspace):
    return store.folder(workspace).parent / 'engine-journeys'


def path(workspace, journey_id):
    try:
        if str(UUID(journey_id)) != journey_id:
            raise ValueError()
    except ValueError:
        raise HTTPException(404, 'Journey not found')
    return folder(workspace) / (journey_id + '.json')


def load(workspace, journey_id):
    try:
        journey = json.loads(path(workspace, journey_id).read_text(encoding='utf-8'))
    except FileNotFoundError:
        raise HTTPException(404, 'Journey not found')
    except (ValueError, OSError):
        raise HTTPException(500, 'Journey checkpoint could not be read')
    journey['workspace_id'] = workspace
    return journey


def save(journey):
    journey['updated_at'] = store.now()
    store.atomic_write(path(journey['workspace_id'], journey['journey_id']), journey)


def log(journey, kind, message, **extra):
    journey['events'].append({'sequence': len(journey['events']) + 1, 'at': store.now(), 'type': kind,
                              'message': message, **extra})


def scan(item, others):
    """Port of the workbench's scanNarrative: flags for review, never silent edits."""
    text, lower = item.text, item.text.lower()
    injection = [pattern for pattern in INJECTION if pattern in lower]
    pii = []
    if re.search(r'[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}', text, re.I):
        pii.append('email-like text')
    if re.search(r'(?:\+?\d[\s-]?){8,}', text):
        pii.append('phone-or-id-like number')
    if re.search(r'\b(?:national id|passport|id number|birth certificate)\b', text, re.I):
        pii.append('identity document mention')
    quality = []
    if len(text.strip()) < 80:
        quality.append('short narrative')
    if re.search(r'(.)\1{12,}', text):
        quality.append('repeated-character anomaly')
    normalized = ' '.join(lower.split())
    if normalized in others:
        quality.append('exact duplicate of an earlier record')
    risk = min(1.0, len(injection) * 0.28 + len(pii) * 0.18 + len(quality) * 0.08)
    blockers = []
    if not any(character.isalnum() for character in text):
        blockers.append('no readable words')
    if item.language != 'en':
        blockers.append('not English: the encoder reads English keywords only; supply a translation the researcher has checked')
    warnings = []
    if item.consent == 'unconfirmed':
        warnings.append('consent unconfirmed: confirm research use before accepting')
    if injection:
        warnings.append('instruction-like text: review before accepting')
    return {'risk': round(risk, 2), 'injection_flags': injection, 'pii_flags': pii, 'quality_flags': quality,
            'blockers': blockers, 'warnings': warnings,
            'gate': 'blocked' if blockers else 'review_before_accepting' if risk >= 0.35 or warnings else 'eligible'}


def accepted(journey):
    return [record for record in journey['records'] if record['review'] and record['review']['decision'] == 'accept']


def narrative(record, country):
    return NarrativeRecord(narrative_id=record['record_id'], text=record['text'], metadata=NarrativeMetadata(
        source_type=record['source_type'], source_name=record['source_name'], country=country,
        admin_unit=record['admin_unit'], language=record['language'],
        provenance={'declared_by': 'researcher', 'consent': record['consent'], 'period': record['period']}))


def output(journey, stage):
    entry = journey['stages'].get(stage)
    return entry['output'] if entry else None


def inoculation_signal(journey):
    diagnoses = [InoculationEncoding.model_validate(item) for item in (output(journey, 'encoding') or {}).get('diagnoses', [])]
    if not diagnoses:
        return {key: 0.0 for key in ('inoculation_strength', 'misinformation_risk', 'reactance_penalty', 'trusted_messenger_fit',
                                     'misinformation_decay', 'resistance_growth', 'trust_shift', 'barrier_shift')}
    return aggregate_inoculation_parameters(diagnoses)


def model_params(journey, **extra):
    """Port of the workbench's modelParams(): every later stage reads the stages before it."""
    encoded = (output(journey, 'encoding') or {}).get('encoded', [])
    digital, bayes, rl = output(journey, 'digital'), output(journey, 'bayes'), output(journey, 'rl')
    applied = (output(journey, 'inoculation') or {}).get('applied_strength', 0.0)
    signal = inoculation_signal(journey)
    feedback = digital['feedback'] if digital else {'trust_shift': 0.0, 'barrier_shift': 0.0}
    trust = bayes['trust_mean'] if bayes else avg([e['trust_score'] for e in encoded], 0.6) + feedback['trust_shift']
    barrier = bayes['barrier_mean'] if bayes else avg([e['adoption_barrier_score'] for e in encoded], 0.35) + feedback['barrier_shift']
    trust = clamp01(trust + applied * 0.08 + signal['trust_shift'] * 0.25)
    barrier = clamp01(barrier - applied * 0.07 + signal['barrier_shift'] * 0.25)
    confidence = avg([e['confidence'] for e in encoded], 0.5)
    rl_bonus = rl['intervention_bonus'] if rl else 0.0
    return {'trust_score': trust, 'barrier_score': barrier,
            'narrative_influence': min(0.9, 0.2 + 0.35 * confidence + applied * 0.12),
            'intervention_strength': min(0.9, 0.1 + 0.2 * trust + rl_bonus + applied * 0.28),
            'inoculation_strength': applied, 'recommended_inoculation_strength': signal['inoculation_strength'],
            'misinformation_risk': signal['misinformation_risk'],
            'misinformation_decay': max(signal['misinformation_decay'], applied * 0.6) if applied else signal['misinformation_decay'] * 0.25,
            'resistance_growth': max(signal['resistance_growth'], applied * 0.55) if applied else signal['resistance_growth'] * 0.2,
            'reactance_penalty': signal['reactance_penalty'], 'trusted_messenger_fit': signal['trusted_messenger_fit'], **extra}


def simulate(mode, horizon, params):
    return {'model': mode.value, 'horizon_days': horizon, 'parameters': params,
            'trajectory': run_digital_twin(mode, horizon, params), 'assumptions': model_assumptions(mode, params),
            'method_status': 'illustrative_uncalibrated'}


def regional_rows(journey):
    encoded = {item['narrative_id']: item for item in (output(journey, 'encoding') or {}).get('encoded', [])}
    groups = {}
    for record in accepted(journey):
        row = groups.setdefault(record['admin_unit'], {'region': record['admin_unit'], 'count': 0, 'trust': [], 'barrier': [],
                                                        'confidence': [], 'themes': []})
        item = encoded.get(record['record_id'], {})
        row['count'] += 1
        row['trust'].append(item.get('trust_score'))
        row['barrier'].append(item.get('adoption_barrier_score'))
        row['confidence'].append(item.get('confidence'))
        row['themes'] += item.get('themes') or ['general']
    return [{**row, 'trust': round(avg(row['trust'], 0.6), 4), 'barrier': round(avg(row['barrier'], 0.35), 4),
             'confidence': round(avg(row['confidence'], 0.5), 4), 'themes': top_items(row['themes'], 4)}
            for row in groups.values()]


def rule_of_thumb(row, target):
    """The workbench's threshold rule, returned with its thresholds so nobody mistakes it for a model result."""
    if target == 'trust' or row['trust'] < 0.52:
        return 'trusted messengers lead (rule: target=trust or trust < 0.52)'
    if target == 'diffusion' or (row['trust'] > 0.62 and row['barrier'] < 0.45):
        return 'peer diffusion (rule: target=diffusion or trust > 0.62 with barrier < 0.45)'
    if row['barrier'] > 0.48:
        return 'reduce practical friction first (rule: barrier > 0.48)'
    return 'balanced mix (no threshold met)'


def vaccine_curve(base, strength, phase, agent):
    lift = strength * (0.115 if agent else 0.095) * (1.45 if phase == 'after' else 1)
    rows = []
    for index, point in enumerate(base):
        progress = index / max(1, len(base) - 1)
        onset = clamp01((progress - 0.18) / 0.55) if phase == 'during' else clamp01((progress - 0.08) / 0.65)
        protection = 0.72 + 0.28 * progress if phase == 'after' else 1
        rows.append({**point, 'adoption': clamp01(point['adoption'] + lift * onset * protection * (1 - point['adoption']))})
    return rows


def run_stage(journey, stage, req):
    encoded_out = output(journey, 'encoding')
    if stage == 'encoding':
        records = [narrative(record, journey['country']) for record in accepted(journey)]
        encoded = [encode_rule_based(record, EncodingMode.manual, 'journey: deterministic English keyword encoder') for record in records]
        diagnoses = [diagnose_inoculation_rule_based(record, item) for record, item in zip(records, encoded)]
        return {'encoded': [item.model_dump(mode='json') for item in encoded],
                'diagnoses': [item.model_dump(mode='json') for item in diagnoses],
                'mean': {'trust': avg([e.trust_score for e in encoded], None), 'barrier': avg([e.adoption_barrier_score for e in encoded], None),
                         'confidence': avg([e.confidence for e in encoded], None)},
                'themes': top_items([theme for e in encoded for theme in e.themes], 6),
                'inoculation_signal': aggregate_inoculation_parameters(diagnoses),
                'method': 'English keyword heuristics; interpretations, not measurements.'}
    if stage == 'compartmental':
        return simulate(ModelMode.compartmental, req.horizon_days, model_params(journey))
    if stage == 'agents':
        return simulate(ModelMode.agent_based, req.horizon_days,
                        model_params(journey, peer_effect=req.peer_effect, media_effect=req.media_effect))
    if stage == 'digital':
        missing = [name for name in ('observed_adoption', 'trust_shift', 'barrier_shift') if getattr(req, name) is None]
        if missing:
            raise HTTPException(422, 'The digital twin needs the researcher\'s field observations; there are no defaults. '
                                     f'Missing: {", ".join(missing)}. Ask the researcher; use 0 for a shift they did not observe.')
        feedback = {'observed_adoption': req.observed_adoption, 'trust_shift': req.trust_shift, 'barrier_shift': req.barrier_shift,
                    'observed_series': req.observed_series, 'note': req.feedback_note}
        base = model_params(journey, initial_adoption=req.observed_adoption)
        params = {**base, 'trust_score': clamp01(base['trust_score'] + req.trust_shift),
                  'barrier_score': clamp01(base['barrier_score'] + req.barrier_shift),
                  'observed_adoption': req.observed_adoption, 'scenario_type': 'observed_feedback_hybrid_rerun'}
        return {**simulate(ModelMode.hybrid, req.horizon_days, params), 'feedback': feedback}
    if stage == 'bayes':
        priors = {**PRIORS, **(req.priors or {})}
        if set(priors) != set(PRIORS) or any(value <= 0 for value in priors.values()):
            raise HTTPException(422, 'priors takes trust_a, trust_b, barrier_a, barrier_b, all positive.')
        encoded = encoded_out['encoded']
        feedback = output(journey, 'digital')['feedback']
        trials = max(10, len(accepted(journey)) * 12)
        trust_obs = clamp01(avg([e['trust_score'] for e in encoded], 0.6) + feedback['trust_shift'])
        barrier_obs = clamp01(avg([e['adoption_barrier_score'] for e in encoded], 0.35) + feedback['barrier_shift'])
        ta, tb = priors['trust_a'] + round(trust_obs * trials), priors['trust_b'] + trials - round(trust_obs * trials)
        ba, bb = priors['barrier_a'] + round(barrier_obs * trials), priors['barrier_b'] + trials - round(barrier_obs * trials)
        result = {'priors': priors, 'pseudo_trials': trials, 'trust_alpha': ta, 'trust_beta': tb, 'barrier_alpha': ba,
                  'barrier_beta': bb, 'trust_mean': ta / (ta + tb), 'barrier_mean': ba / (ba + bb),
                  'signal_update_note': f'Beta update treating the mean keyword score as {trials} pseudo-trials '
                                        f'({len(accepted(journey))} records x 12). The pseudo-trial count is a tool '
                                        'convention; it controls how far the prior moves.'}
        series = feedback.get('observed_series')
        if series:
            from .api_routes import _fallback_bayesian
            fit = _fallback_bayesian(series)
            result['adoption_fit'] = {'parameters': fit['parameters'], 'trajectory': fit['trajectory'],
                                      'method': 'deterministic moment approximation on the researcher\'s observed series; '
                                                'the band is a fixed heuristic width, not a posterior interval'}
        else:
            result['adoption_fit'] = None
            result['adoption_fit_note'] = ('No observed adoption series was given at the digital twin stage, so the adoption '
                                           'curve was not fitted. Model output is never used as observations.')
        return result
    if stage == 'rl':
        bayes = output(journey, 'bayes')
        trust, barrier = bayes['trust_mean'], bayes['barrier_mean']
        scores = {action: round(lift + trust * 0.30 - barrier * 0.22 - cost, 6) for action, (lift, cost) in RL_ACTIONS.items()}
        ranking = sorted(scores, key=lambda action: (-scores[action], action))
        return {'ranking': [{'action': action, 'score': scores[action], 'assumed_lift': RL_ACTIONS[action][0],
                             'assumed_cost': RL_ACTIONS[action][1]} for action in ranking],
                'top_action': ranking[0], 'trust_used': trust, 'barrier_used': barrier,
                'intervention_bonus': max(0.0, scores[ranking[0]]) * 0.025,
                'formula': 'score = assumed_lift + 0.30 x trust - 0.22 x barrier - assumed_cost',
                'method': 'Deterministic ranking under the tool\'s fixed assumed lifts and costs (the workbench\'s fallback '
                          'optimizer, without its random exploration). The lifts and costs are not estimated from any data, '
                          'so the ranking restates those assumptions.'}
    if stage == 'regional':
        rows = regional_rows(journey)
        if req.regional_mode == 'grouped':
            rows = [{'region': 'Grouped evidence', 'count': sum(row['count'] for row in rows),
                     'trust': round(avg([row['trust'] for row in rows], 0.6), 4), 'barrier': round(avg([row['barrier'] for row in rows], 0.35), 4),
                     'confidence': round(avg([row['confidence'] for row in rows], 0.5), 4),
                     'themes': top_items([theme for row in rows for theme in row['themes']], 5)}]
        return {'mode': req.regional_mode, 'target': req.regional_target,
                'rows': [{**row, 'rule_of_thumb': rule_of_thumb(row, req.regional_target)} for row in rows],
                'note': 'Averages of keyword scores per place. Places with one or two records say little about the place.'}
    if stage == 'graph':
        nodes, edges = {}, []
        for row in regional_rows(journey):
            region = f"region:{row['region']}"
            nodes.setdefault(region, {'id': region, 'label': row['region'].split(' / ')[-1], 'kind': 'location'})
            links = [(f'theme:{theme}', theme, 'theme', 'theme') for theme in row['themes']]
            links.append(('signal:high trust', 'high trust', 'signal', 'trust') if row['trust'] >= 0.6 else ('signal:trust risk', 'trust risk', 'signal', 'trust'))
            links.append(('signal:barrier risk', 'barrier risk', 'signal', 'barrier') if row['barrier'] >= 0.45 else ('signal:low barrier', 'low barrier', 'signal', 'barrier'))
            for node_id, label, kind, edge in links:
                nodes.setdefault(node_id, {'id': node_id, 'label': label, 'kind': kind})
                edges.append({'from': region, 'to': node_id, 'label': edge})
        for node in nodes.values():
            node['degree'] = sum(node['id'] in (edge['from'], edge['to']) for edge in edges)
        return {'nodes': list(nodes.values()), 'edges': edges,
                'note': 'Co-occurrence of places, keyword themes and thresholded signals (trust >= 0.6, barrier >= 0.45). '
                        'Edges are not causal links.'}
    if stage == 'inoculation':
        diagnoses = encoded_out['diagnoses']
        top = max(diagnoses, key=lambda d: d['misinformation_risk_score'] + d['reactance_risk_score'] + d['threat_recognition_score'], default=None)
        rows = regional_rows(journey)
        risk_row = max(rows, key=lambda row: row['barrier']) if rows else {'region': journey['country']}
        region = risk_row['region'].split(' / ')[-1]
        themes = ', '.join(encoded_out['themes'][:4]) or 'cost, trust, access'
        messenger = (top or {}).get('trusted_messenger') or {'health_workers': 'a local health worker', 'community_leaders': 'a community leader',
                                                             'policy_makers': 'a district policy team'}.get(req.audience, 'a neighbour who has already adopted')
        signal = encoded_out['inoculation_signal']
        encoded = encoded_out['encoded']
        theme_density = sum(any(re.search('inoculation|safety|trust|social', t, re.I) for t in e['themes']) for e in encoded) / len(encoded)
        strength = clamp01(0.10 + avg([e['adoption_barrier_score'] for e in encoded], 0.35) * 0.14 + avg([e['trust_score'] for e in encoded], 0.6) * 0.12
                           + avg([e['confidence'] for e in encoded], 0.5) * 0.10 + theme_density * 0.12
                           + signal.get('inoculation_strength', 0) * 0.38 + signal.get('misinformation_risk', 0) * 0.12)
        weak = (top or {}).get('weak_dose_claim') or 'Some messages may claim the change is only for wealthier families or cannot be sustained.'
        refute = (top or {}).get('refutational_preemption') or 'Before accepting that claim, compare it with local households already using it, verified costs and available support.'
        counter = (top or {}).get('counter_narrative') or 'Do not decide from a rumour alone: visit a local demonstration and ask about costs and support.'
        booster = (top or {}).get('booster_strategy') or 'Repeat the correction through trusted local messengers after the first demonstration.'
        drafts = [
            {'type': 'pre-bunk', 'title': f'Before the rumour spreads in {region}', 'text': f'{weak} {refute} {messenger} can show the practical evidence in context.'},
            {'type': 'refutation', 'title': 'Refutational preemption', 'text': f'{refute} The correction should be specific, respectful, and paired with a practical next step rather than a generic denial.'},
            {'type': 'counter-feed', 'title': 'Short social counter-message', 'text': f'{counter} {booster}'},
        ]
        curves = {}
        for key, agent in (('compartmental', False), ('agents', True)):
            base = output(journey, key)['trajectory']
            curves[key] = {phase: vaccine_curve(base, strength, phase, agent) for phase in ('during', 'after')} | {'before': base}
        result = {'audience': req.audience, 'tone': req.tone, 'themes_used': themes, 'messenger': messenger, 'drafts': drafts,
                  'estimated_strength': strength, 'curves': curves, 'applied_strength': 0.0,
                  'review_status': 'draft: requires human review before any use with people',
                  'curve_method': 'Illustrative lift formula from the workbench applied to the stage 5 and 6 curves; it is not '
                                  'a model of message effects and has not been tested against field data.'}
        if req.apply_to_twin:
            if not output(journey, 'digital'):
                raise HTTPException(409, 'Apply to the twin only after the digital twin stage has run.')
            result['applied_strength'] = strength
            journey['stages']['inoculation'] = {'output': result}  # model_params reads the applied strength
            result['twin'] = simulate(ModelMode.hybrid, req.horizon_days,
                                      model_params(journey, scenario_type='inoculation_vaccine_digital_twin'))
        return result
    if stage == 'policy':
        records = [narrative(record, journey['country']) for record in accepted(journey)]
        grade = evidence_grade(records, [EncodedNarrative.model_validate(item) for item in encoded_out['encoded']])
        params = model_params(journey)
        twin = (output(journey, 'inoculation') or {}).get('twin') or output(journey, 'digital')
        rl = output(journey, 'rl')
        return {'evidence_grade': grade, 'parameters': params,
                'summary': {'accepted_records': len(records), 'rejected_records': sum(1 for r in journey['records'] if r['review'] and r['review']['decision'] == 'reject'),
                            'final_twin_adoption': twin['trajectory'][-1]['adoption'], 'twin_model': twin['model'],
                            'mean_trust': params['trust_score'], 'mean_barrier': params['barrier_score'],
                            'top_ranked_action_under_assumptions': rl['top_action'],
                            'inoculation_applied': bool((output(journey, 'inoculation') or {}).get('applied_strength'))},
                'checks': scientific_checks({key: output(journey, key) for key in ('compartmental', 'agents', 'digital') if output(journey, key)}),
                'code_version': fingerprint(), 'limits': LIMITS,
                'status': 'draft for human review; options for discussion, not recommendations'}
    raise HTTPException(404, f'Unknown stage {stage}')


def progress(journey):
    rows, next_stage = [], None
    for stage in STAGES:
        entry = journey['stages'].get(stage['id'])
        done = bool(entry)
        missing = [need for need in stage['needs'] if need not in journey['stages']]
        status = 'done' if done else 'ready' if not missing else 'waiting'
        rows.append({'number': stage['number'], 'id': stage['id'], 'title': stage['title'], 'phase': stage['phase'],
                     'status': status, 'needs': missing, 'optional': stage.get('optional', False),
                     'researcher_decision': stage['researcher_decision'], 'at': entry.get('at') if entry else None})
        if next_stage is None and status == 'ready' and not stage.get('optional'):
            next_stage = stage['id']
    return rows, next_stage


def public(journey, full=False):
    rows, next_stage = progress(journey)
    body = {key: journey[key] for key in ('journey_id', 'workspace_id', 'question', 'country', 'created_at', 'updated_at')}
    body['records'] = [{key: record[key] for key in ('record_id', 'admin_unit', 'source_name', 'source_type', 'period', 'language',
                                                     'consent', 'content_sha256', 'gate', 'review')} | {'excerpt': record['text'][:160]}
                       for record in journey['records']]
    body['stages'] = rows
    body['next_stage'] = next_stage
    body['presentation'] = presentation(journey)
    if full:
        body['outputs'] = {key: value['output'] for key, value in journey['stages'].items()}
        body['events'] = journey['events']
    return body


@router.get('/journey/stages')
def stage_guide():
    return {'stages': STAGES, 'runnable': list(RUNNABLE), 'intro': INTRO,
            'principles': ['Only records the researcher accepted reach a model.',
                           'Field feedback, evidence decisions and the export need the researcher\'s own words.',
                           'All scores are keyword heuristics and all curves are illustrative and uncalibrated.']}


@router.post('/workspaces/{workspace}/journeys', status_code=201)
def create(workspace: str, req: JourneyCreate):
    store.folder(workspace)  # 404 for an unknown workspace
    journey = {'journey_id': str(uuid4()), 'workspace_id': workspace, 'question': req.question, 'country': req.country,
               'created_at': store.now(), 'records': [], 'stages': {}, 'events': []}
    log(journey, 'created', 'Journey created', code_version=fingerprint())
    save(journey)
    return public(journey)


@router.get('/workspaces/{workspace}/journeys')
def listing(workspace: str):
    rows = []
    for file in folder(workspace).glob('*.json'):
        try:
            journey = load(workspace, file.stem)
        except HTTPException:
            continue
        rows.append({'journey_id': journey['journey_id'], 'question': journey['question'], 'created_at': journey['created_at'],
                     'updated_at': journey['updated_at'], 'stages_done': len(journey['stages'])})
    return {'journeys': sorted(rows, key=lambda row: row['created_at'], reverse=True)}


@router.get('/workspaces/{workspace}/journeys/{journey_id}')
def get(workspace: str, journey_id: str, full: bool = False):
    return public(load(workspace, journey_id), full)


@router.post('/workspaces/{workspace}/journeys/{journey_id}/evidence')
def add_evidence(workspace: str, journey_id: str, req: EvidenceRequest):
    journey = load(workspace, journey_id)
    if 'encoding' in journey['stages']:
        raise HTTPException(409, 'Evidence is frozen once encoding has run; start a new journey to add records.')
    seen = {' '.join(record['text'].lower().split()) for record in journey['records']}
    added = []
    for item in req.records:
        gate = scan(item, seen)
        seen.add(' '.join(item.text.lower().split()))
        record = {'record_id': str(uuid4()), **item.model_dump(), 'content_sha256': hashlib.sha256(item.text.encode()).hexdigest(),
                  'gate': gate, 'review': None, 'added_at': store.now()}
        journey['records'].append(record)
        added.append(record['record_id'])
    journey['stages']['intake'] = {'at': store.now(), 'output': {'records': len(journey['records'])}}
    journey['stages']['gate'] = {'at': store.now(), 'output': {
        'eligible': sum(r['gate']['gate'] == 'eligible' for r in journey['records']),
        'review_before_accepting': sum(r['gate']['gate'] == 'review_before_accepting' for r in journey['records']),
        'blocked': sum(r['gate']['gate'] == 'blocked' for r in journey['records'])}}
    journey['stages'].pop('repository', None)  # new records need a decision before the repository is complete
    log(journey, 'intake', f'{len(added)} record(s) added and gate-checked', record_ids=added)
    save(journey)
    return public(journey)


@router.post('/workspaces/{workspace}/journeys/{journey_id}/review')
def review(workspace: str, journey_id: str, req: ReviewRequest):
    journey = load(workspace, journey_id)
    if 'encoding' in journey['stages']:
        raise HTTPException(409, 'Decisions are frozen once encoding has run; start a new journey to change them.')
    records = {record['record_id']: record for record in journey['records']}
    for decision in req.decisions:
        record = records.get(decision.record_id)
        if not record:
            raise HTTPException(404, f'Record {decision.record_id} is not in this journey')
        if decision.decision == 'accept' and record['gate']['gate'] == 'blocked':
            raise HTTPException(422, f"Record {decision.record_id} is blocked at the gate ({'; '.join(record['gate']['blockers'])}) and cannot be accepted.")
    for decision in req.decisions:
        records[decision.record_id]['review'] = {'decision': decision.decision, 'reason': decision.reason, 'at': store.now()}
    log(journey, 'review', f'{len(req.decisions)} decision(s) recorded', approval_statement=req.approval_statement,
        decisions=[decision.model_dump() for decision in req.decisions])
    undecided = [record['record_id'] for record in journey['records'] if not record['review']]
    if accepted(journey) and not undecided:
        journey['stages']['repository'] = {'at': store.now(), 'output': {'accepted': len(accepted(journey)),
                                                                          'rejected': len(journey['records']) - len(accepted(journey))}}
    save(journey)
    return public(journey) | {'undecided': undecided}


@router.post('/workspaces/{workspace}/journeys/{journey_id}/stages/{stage}')
def run(workspace: str, journey_id: str, stage: str, req: StageRequest):
    journey = load(workspace, journey_id)
    if stage not in RUNNABLE:
        raise HTTPException(404, f'Stage {stage!r} is not run this way. Runnable stages: {", ".join(RUNNABLE)}.')
    missing = [need for need in BY_ID[stage]['needs'] if need not in journey['stages']]
    if missing:
        raise HTTPException(409, f"{BY_ID[stage]['title']} needs these stages first: {', '.join(BY_ID[n]['title'] for n in missing)}.")
    if BY_ID[stage]['researcher_decision'] and not req.approval_statement:
        raise HTTPException(422, f"{BY_ID[stage]['title']} is a researcher decision: pass their own words as approval_statement.")
    # A re-run replaces this stage and everything that read it. Clear them before computing, because later stages
    # feed model_params (the workbench adds the field shifts twice when the twin is re-run).
    stale = [later for later in dependents(stage) if later in journey['stages']]
    for key in [stage, *stale]:
        journey['stages'].pop(key, None)
    result = run_stage(journey, stage, req)
    journey['stages'][stage] = {'at': store.now(), 'output': result}
    log(journey, 'stage', f"{BY_ID[stage]['title']} ran", stage=stage, approval_statement=req.approval_statement,
        settings=req.model_dump(exclude_none=True, exclude={'approval_statement'}), cleared=stale)
    save(journey)
    return public(journey) | {'stage': stage, 'output': result, 'cleared_later_stages': stale}

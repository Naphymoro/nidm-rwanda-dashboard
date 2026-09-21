"""Scientific tool registry. The harness owns execution; these tools own methods."""
import hashlib
import importlib
import importlib.metadata
import marshal
import math
from pathlib import Path

from .encoding import encode_rule_based
from .inoculation import diagnose_inoculation_rule_based
from .modelling import run_digital_twin, model_assumptions
from .schemas import NarrativeRecord, NarrativeMetadata, EncodedNarrative, ModelMode

LIMITS = ('English keyword encodings are interpretations, not validated measurements. '
          'One narrative does not establish prevalence, causality or truth. '
          'Simulations are illustrative, not calibrated forecasts. Bands are heuristic envelopes, '
          'not statistical confidence intervals. Numerical checks do not establish scientific validity.')


def fingerprint():
    digest = hashlib.sha256()
    for name in ('engine_tools', 'engine_harness', 'engine_resources', 'engine_lessons', 'engine_store',
                 'modelling', 'encoding', 'inoculation', 'schemas'):
        module = importlib.import_module(f'{__package__}.{name}')
        source = Path(module.__file__)
        digest.update(name.encode())
        digest.update(source.read_bytes() if source.is_file() else marshal.dumps(module.__loader__.get_code(module.__name__)))
    return 'sha256:' + digest.hexdigest()


def record_for(run):
    context = run['context']
    return NarrativeRecord(narrative_id=run['run_id'], text=run['evidence'], metadata=NarrativeMetadata(
        source_type='field_note', source_name=context['source_name'], country=context['country'],
        language=context['language'], provenance={'declared_by': 'researcher', 'domain': context['domain'], 'consent': context['consent']}))


def parameters(run):
    encoded = run['outputs']['encode']
    return {'trust_score': encoded['trust_score'], 'barrier_score': encoded['adoption_barrier_score'],
            'confidence': encoded['confidence'], 'misinformation_risk': run['outputs']['diagnose']['misinformation_risk_score'],
            'narrative_influence': run['request']['narrative_influence'],
            'initial_adoption': run['request']['initial_adoption'], 'intervention_strength': 0.0}


def scientific_checks(outputs):
    rows = []
    for key, output in outputs.items():
        if 'trajectory' not in output:
            continue
        trajectory = output['trajectory']
        finite = all(math.isfinite(value) for row in trajectory for value in row.values() if isinstance(value, (float, int)))
        bounded = all(0 <= row['adoption'] <= 1 for row in trajectory)
        conservation = all(abs(sum(row[c] for c in 'SMTIR') - 1) < 1e-9 for row in trajectory) if trajectory and 'S' in trajectory[0] else None
        rows.append({'tool': key, 'finite': finite, 'bounded_adoption': bounded, 'normalized_compartment_sum': conservation,
                     'note': 'The engine normalizes compartments after each step; this is a post-normalization check, not raw ODE conservation.'})
    return {'checks': rows, 'passed': all(row['finite'] and row['bounded_adoption'] and row['normalized_compartment_sum'] is not False for row in rows),
            'interpretation': 'Numerical consistency only. No empirical calibration or validation is performed.'}


def execute_tool(step, run):
    tool = step['tool']
    if tool == 'encode':
        return encode_rule_based(record_for(run)).model_dump(mode='json')
    if tool == 'diagnose':
        encoded = EncodedNarrative.model_validate(run['outputs']['encode'])
        return diagnose_inoculation_rule_based(record_for(run), encoded).model_dump(mode='json')
    if tool == 'simulate':
        params = {**parameters(run), 'intervention_strength': step['strength']}
        mode = ModelMode(run['request']['model'])
        return {'parameters': params, 'model': mode.value,
                'trajectory': run_digital_twin(mode, run['request']['horizon_days'], params),
                'assumptions': model_assumptions(mode, params), 'method_status': 'illustrative_uncalibrated'}
    if tool == 'check':
        checks = scientific_checks(run['outputs'])
        if not checks['passed']:
            raise ValueError('Numerical checks failed')
        return checks
    if tool == 'brief':
        signals = run['outputs']['encode']
        lines = ['# NIDM research brief', '', 'Status: exploratory draft requiring researcher review', '',
                 f"Research question: {run['title']}", f"Run: {run['run_id']}", f"Workspace: {run['workspace_id']}",
                 f"Code: {run['provenance']['code_version']}", '', '## Source evidence', run['evidence'], '',
                 '## Interpretation', f"Trust heuristic: {signals['trust_score']:.3f}; barrier heuristic: {signals['adoption_barrier_score']:.3f}."]
        for key, output in run['outputs'].items():
            if 'trajectory' in output:
                lines.append(f"{key}: intervention={output['parameters']['intervention_strength']:.3f}; final illustrative adoption={output['trajectory'][-1]['adoption']:.4f}.")
        lines += ['', '## Assumptions and limitations', LIMITS, '', '## Review next',
                  'Check source consent, translation, keyword interpretations, parameter choices and calibration against independent field evidence.',
                  'The audit JSON includes the full plan, context, inputs, tool outputs, execution events and environment.']
        return {'markdown': '\n'.join(lines)}
    raise ValueError('Tool is not in the scientific allowlist')

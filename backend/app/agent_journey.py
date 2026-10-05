"""The 13-stage journey inside the research assistant, with every researcher decision behind a control in the chat.

Small local models invent the researcher's answers: in benchmarks qwen3:8b and llama3.2:3b started a journey with a
confirmation ("Yes, that is my question.") the researcher never gave. Instructions in a prompt cannot stop that, so
here the model only proposes and explains:

- It may propose a question or records (nothing is written) and run the stages that only compute.
- Starting the journey, adding records, accepting or rejecting them, entering field observations and approving the
  export happen only through the journey card's buttons and forms, which call the engine directly. No tool exists for
  them, so no model can do them.
- The engine owns the key sentences and limits (journey_text); the card shows them as written and the model is told
  not to restate them.
"""
from fastapi import HTTPException

from . import journey as engine_journey
from .journey import BY_ID, JourneyCreate, StageRequest

# Stages the model may run when the researcher says to continue: they compute, nobody decides anything in them.
MODEL_RUNNABLE = ('encoding', 'compartmental', 'agents', 'bayes', 'rl', 'regional', 'graph', 'inoculation')
DECIDED_IN_CARD = {'repository': 'the Accept and Reject buttons on each record',
                   'digital': 'the field observations form',
                   'policy': 'the Approve export button'}

TOOLS = [
    {'name': 'propose_journey',
     'description': 'Propose the full 13-stage NDIM journey (field notes -> gate -> repository -> encoding -> models -> '
                    'digital twin -> strategy -> policy draft) for the researcher\'s question. Nothing starts: the '
                    'journey card shows the question in an editable box and the researcher clicks Confirm question. '
                    'Use it when the researcher wants to go from their own field evidence to a policy draft.',
     'parameters': {'type': 'object', 'properties': {
         'question': {'type': 'string', 'description': 'The researcher\'s question copied verbatim from their message: '
                                                       'no rephrasing and no added context such as "in Rwanda".'}},
         'required': ['question']}},
    {'name': 'propose_journey_records',
     'description': 'Fill the journey card\'s evidence form with the field notes the researcher gave in the chat, one '
                    'record per story. Nothing is added: the researcher checks each record, sets permission and clicks '
                    'Add to journey. Only copy what they wrote; leave a field empty when they did not give it.',
     'parameters': {'type': 'object', 'properties': {'records': {'type': 'array', 'maxItems': 50, 'items': {
         'type': 'object', 'properties': {
             'text': {'type': 'string', 'description': 'The story or note, unchanged.'},
             'admin_unit': {'type': 'string', 'description': 'Place as the researcher gave it, e.g. "Kicukiro / Niboye"; empty if not given.'},
             'source_name': {'type': 'string', 'description': 'Who or what it came from; empty if not given.'},
             'period': {'type': 'string', 'description': 'When it was collected, e.g. "2026-Q2"; empty if not given.'}},
         'required': ['text']}}}, 'required': ['records']}},
    {'name': 'journey_status',
     'description': 'Where this chat\'s journey stands: each stage, the records with their gate flags and decisions, the '
                    'next stage, and what the journey card shows.',
     'parameters': {'type': 'object', 'properties': {}}},
    {'name': 'run_journey_stage',
     'description': 'Run one computing stage of this chat\'s journey when the researcher asks to continue: '
                    + ', '.join(MODEL_RUNNABLE) + '. The repository decisions, the digital twin (field observations) and '
                    'the policy export are the researcher\'s, made in the journey card; this tool cannot run them.',
     'parameters': {'type': 'object', 'properties': {'stage': {'type': 'string', 'enum': list(MODEL_RUNNABLE)}},
                    'required': ['stage']}},
]
LABELS = {'propose_journey': 'Proposing a journey', 'propose_journey_records': 'Filling the evidence form',
          'journey_status': 'Reading the journey', 'run_journey_stage': 'Running a journey stage'}

CARD_RULE = ('The journey card in the chat shows the key sentences and limits of each finished stage exactly as the '
             'engine wrote them. Do not repeat or reword them; explain in plain words what they mean for the '
             'researcher\'s question.')

PROMPT = [
    # Asked for "the full journey", a live qwen3:8b followed the experiment rule instead (ask for evidence via the +
    # button) and never proposed the journey.
    'When the researcher asks for the full journey (from their field notes to a policy draft), call propose_journey in '
    'this same reply with their question copied verbatim. The journey collects its own field notes in its card, so do '
    'not ask them to attach evidence or use the + button first; the + button is for single experiments.',
    'The 13-stage journey (field notes to policy draft) has a card in the chat. You can propose a journey '
    '(propose_journey), fill its evidence form from notes the researcher gave (propose_journey_records), read it '
    '(journey_status) and run the stages that only compute (run_journey_stage) when the researcher asks to continue.',
    'Confirming the question, adding records, accepting or rejecting records, giving field observations and approving '
    'the policy export are the researcher\'s decisions, made with the card\'s buttons and forms. You cannot make them '
    'and must never write as if they had been made: say "click Confirm question in the card", never "I have started '
    'the journey". Never invent observations, places, periods or permissions.',
    # A live qwen3:8b sent journey notes to the + button and offered "public or confidential" permission levels.
    'For the journey, field notes go in this chat or in the card\'s form, never the + button. The card offers three '
    'permission choices: permission confirmed for research use, synthetic or demo data, or permission not confirmed. '
    'The card\'s buttons are Confirm question, Add to journey, Accept, Reject, Save decisions, Run, and Approve export; '
    'name no others.',
    CARD_RULE,
    # Even with key_facts, a live qwen3:8b added "train 100 messengers in Gatenga could boost adoption by ~15%". The
    # engine now writes each stage's explanation (card_shows.explanation); the model answers questions about it.
    'The card explains each finished stage in plain words, written by the engine (card_shows.explanation). Do not '
    'explain a stage again unless the researcher asks. When they ask, answer from that explanation and key_facts in a '
    'few sentences, and do not add interventions, scenarios, population groups, places or numbers the engine did not '
    'produce. If they ask for more than the engine shows, say so.',
    'When reporting a journey stage: say "in the illustrative model, adoption is X at day N", never "adoption will '
    'reach X". Never write that anything causes, drives, improves or increases adoption, not even with "may" or '
    '"suggests". The RL ranking, the regional rule of thumb and the policy output are the tool\'s assumptions and '
    'options for discussion, never advice. Never write validated, calibrated, confirmed, significant or robust.',
]


def _stage_title(stage):
    return f"{BY_ID[stage]['number']}. {BY_ID[stage]['title']}"


def _final(output):
    trajectory = (output or {}).get('trajectory') or []
    return round(trajectory[-1]['adoption'], 4) if trajectory else None


def facts(stage, output):
    """The engine's own numbers and labels for a finished stage, so the model has something true to explain."""
    if stage == 'encoding':
        return {'mean': {k: None if v is None else round(v, 3) for k, v in output['mean'].items()}, 'themes': output['themes'],
                'per_record': [{'trust': round(e['trust_score'], 3), 'barrier': round(e['adoption_barrier_score'], 3),
                                'themes': e['themes']} for e in output['encoded']],
                'sentiment': output.get('sentiment')}
    if stage in ('compartmental', 'agents', 'digital'):
        out = {'model': output['model'], 'initial_adoption': round(output['trajectory'][0]['adoption'], 4),
               'final_adoption': _final(output), 'horizon_days': output['horizon_days']}
        if stage == 'agents' and output.get('robustness'):
            check = output['robustness']
            out['network_check'] = {'verdict': check['level_verdict'], 'measure': check['measure'],
                                    'average_adoption_by_network': {row['label']: row['average_adoption'] for row in check['variants']}}
        if stage == 'digital':
            out['researcher_observations'] = {k: output['feedback'][k] for k in ('observed_adoption', 'trust_shift', 'barrier_shift')}
        return out
    if stage == 'bayes':
        return {'trust_mean': round(output['trust_mean'], 4), 'barrier_mean': round(output['barrier_mean'], 4),
                'adoption_curve_fitted': bool(output['adoption_fit'])}
    if stage == 'rl':
        return {'ranking_under_fixed_assumptions': [{'action': r['action'].replace('_', ' '), 'score': round(r['score'], 4)}
                                                    for r in output['ranking']], 'formula': output['formula']}
    if stage == 'regional':
        return {'places': [{k: row[k] for k in ('region', 'count', 'trust', 'barrier', 'rule_of_thumb')} for row in output['rows']]}
    if stage == 'graph':
        return {'nodes': [node['label'] for node in output['nodes']], 'links': len(output['edges'])}
    if stage == 'inoculation':
        return {'audience': output['audience'], 'messenger': output['messenger'],
                'drafts': [{'type': d['type'], 'title': d['title'], 'text': d['text']} for d in output['drafts']]}
    if stage == 'policy':
        return {'evidence_grade': output['evidence_grade'].get('grade'), 'summary': output['summary']}
    return {}


def all_facts(body):
    """Every finished stage's key facts and fixed sentences: what an explanation may draw on, and nothing more.
    (Raw outputs hold every day and level of every curve, so any invented number would match one of them.)"""
    outputs = body.get('outputs') or {}
    return {stage: {'facts': facts(stage, output), **body['presentation']['stages'].get(stage, {})}
            for stage, output in outputs.items()}


def brief(body, stage=None):
    """What the model needs: progress, records, what the card shows, and what happens next."""
    shown = body['presentation']['stages']
    out = {'question': body['question'],
           'progress': [f"{row['number']}. {row['title']}: {row['status']}" + (' (optional)' if row['optional'] else '')
                        for row in body['stages']],
           'records': [{'record_id': r['record_id'], 'place': r['admin_unit'], 'gate': r['gate']['gate'],
                        'flags': r['gate']['blockers'] + r['gate']['warnings'] + r['gate']['pii_flags'] + r['gate']['quality_flags'],
                        'decision': (r['review'] or {}).get('decision')} for r in body['records']],
           'next_stage': body['next_stage']}
    if not stage:  # after a click in the card: the stage that just finished
        finished = [row for row in body['stages'] if row['status'] == 'done' and row['at'] and row['id'] in shown
                    and row['id'] not in ('intake', 'gate', 'repository')]
        stage = max(finished, key=lambda row: row['at'])['id'] if finished else None
    if stage:
        out['card_shows'] = {'stage': _stage_title(stage), **shown.get(stage, {})}
        output = body.get('output') if body.get('stage') == stage else (body.get('outputs') or {}).get(stage)
        if output:
            out['key_facts'] = facts(stage, output)
    nxt = body['next_stage']
    steps = [CARD_RULE] if stage else []
    if not body['records']:
        steps.append('No records yet: ask for the researcher\'s field notes (each with place, source, period and whether '
                     'they have permission to use it), then call propose_journey_records with what they wrote.')
    elif nxt == 'repository' or any(not r['review'] for r in body['records']):
        steps.append('The researcher accepts or rejects each record with the card\'s buttons. Point out the gate flags '
                     'in plain words; never decide for them.')
    elif nxt in DECIDED_IN_CARD:
        steps.append(f'Next is {_stage_title(nxt)}, the researcher\'s decision, made with {DECIDED_IN_CARD[nxt]} in the '
                     'card. Explain what it does and that it is theirs; you cannot run it.')
    elif nxt:
        steps.append(f'Next is {_stage_title(nxt)}: say in one sentence what it does and ask whether to continue. Run it '
                     'with run_journey_stage only when they say yes (they can also click Run in the card).')
    else:
        steps.append('All required stages are done. The optional regional analysis can still be run.')
    if nxt == 'graph' and body['stages'][9]['status'] != 'done':
        steps.append('Stage 10, Regional analysis, is optional and has not run: offer it before the knowledge graph.')
    out['next'] = ' '.join(steps)
    return out


def run_tool(name, args, thread):
    """Returns (result for the model, meta for the card), like the other agent tools."""
    workspace, journey_id = thread['workspace_id'], thread.get('journey_id')
    if name == 'propose_journey':
        if journey_id:
            return {'error': 'This chat already has a journey; use journey_status. One journey per chat.'}, {}
        question = str(args.get('question') or '').strip()
        if not 8 <= len(question) <= 1000:
            return {'error': 'The question must be 8-1000 characters, copied from the researcher\'s message.'}, {}
        thread['journey_proposal'] = {'question': question}
        return {'shown_in_card': 'the six phases, the decision points, and the question in an editable box with a Confirm question button',
                'next': 'Tell the researcher in one or two sentences to check the question in the card (they can edit it) '
                        'and click Confirm question. The journey has not started; you cannot start it.'}, {'journey': True}
    if not journey_id:
        return {'error': 'This chat has no journey yet. Propose one with propose_journey; the researcher confirms it in the card.'}, {}
    if name == 'propose_journey_records':
        records = [{key: str(item.get(key) or '').strip() for key in ('text', 'admin_unit', 'source_name', 'period')}
                   for item in (args.get('records') or [])[:50] if str(item.get('text') or '').strip()]
        if not records:
            return {'error': 'No record text: copy each story the researcher gave, one record per story.'}, {}
        thread['journey_records_proposal'] = records
        missing = sorted({key for record in records for key, value in record.items() if not value})
        return {'shown_in_card': f'{len(records)} record(s) in an editable form with an Add to journey button',
                'empty_fields': missing,
                'next': 'Ask the researcher to check each record in the card, fill in anything empty'
                        + (f' ({", ".join(missing)})' if missing else '') + ', choose the permission for each and click '
                        'Add to journey. Nothing is added until they do.'}, {'journey': True}
    try:
        if name == 'journey_status':
            return brief(engine_journey.get(workspace, journey_id, full=True)), {'journey': True}
        if name == 'run_journey_stage':
            stage = str(args.get('stage') or '')
            if stage in DECIDED_IN_CARD:
                return {'error': f'{_stage_title(stage)} is the researcher\'s decision, made with {DECIDED_IN_CARD[stage]} '
                                 'in the journey card. You cannot run it.'}, {'journey': True}
            if stage not in MODEL_RUNNABLE:
                return {'error': f'Unknown stage {stage!r}.'}, {}
            body = engine_journey.run(workspace, journey_id, stage, StageRequest())
            return brief(body, stage), {'journey': True}
    except HTTPException as err:
        return {'error': str(err.detail)}, {'journey': True}
    return {'error': f'Unknown tool {name}'}, {}


def start(thread, question, country='Rwanda'):
    """The Confirm question click: the only way a journey starts in a chat."""
    if thread.get('journey_id'):
        raise HTTPException(409, 'This chat already has a journey.')
    body = engine_journey.create(thread['workspace_id'], JourneyCreate(question=question, country=country))
    thread['journey_id'] = body['journey_id']
    thread.pop('journey_proposal', None)
    return body

"""Synthetic fine-tuning data with the NDIM engine as the teacher.

Runs many practice journeys on synthetic field notes through the real engine and turns every finished stage into
chat examples. The input is exactly what the Research Studio gives the assistant (its real system prompt, with the
journey's facts); every answer is the engine's own text, so each example is correct by construction. Questions
include the traps small models fell into: forecasts ("will adoption reach..."), causes ("do messengers drive...")
and advice ("which action should we take").

    python scripts/local_ai_training/make_dataset.py --journeys 160 --out data/train.jsonl --seed 1
    python scripts/local_ai_training/make_dataset.py --journeys 24 --out data/heldout.jsonl --seed 99 --heldout
    python scripts/local_ai_training/make_dataset.py --tools --journeys 60 --out data/tools.jsonl --seed 2

--tools writes tool-use examples instead: the Studio situations where the right reply is a tool call (propose the
journey with the question verbatim, fill the evidence form, run the next computing stage, read the status) and the
ones where it is not acting (the researcher's decisions belong to the card). A first fine-tune without these copied
instruction text instead of calling tools.

Held-out journeys use other places and other seeds, so an evaluation never sees a training journey.
"""
import argparse
import json
import os
import random
import re
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'backend'))
os.environ.setdefault('NDIM_DATA_DIR', tempfile.mkdtemp(prefix='ndim-teacher-'))
for name in ('DATABASE_URL', 'NDIM_REQUIRE_DATABASE', 'NDIM_AGENT_ACCESS_TOKEN'):
    os.environ.pop(name, None)

from fastapi.testclient import TestClient  # noqa: E402
from app import agent, agent_checks, agent_journey  # noqa: E402
from app import journey as engine_journey  # noqa: E402
from app.journey_text import LIMITS  # noqa: E402
from app.main import app  # noqa: E402

PLACES = ['Kicukiro / Niboye', 'Kicukiro / Gatenga', 'Gasabo / Kimironko', 'Nyarugenge / Nyamirambo', 'Huye / Tumba',
          'Musanze / Muhoza', 'Rubavu / Gisenyi', 'Rwamagana / Kigabiro']
HELDOUT_PLACES = ['Nyagatare / Rwempasha', 'Karongi / Bwishyura', 'Bugesera / Nyamata', 'Muhanga / Shyogwe']
WHO = ['Households', 'Several mothers', 'Members of the women\'s cooperative', 'Young families', 'A restaurant owner and her staff',
       'Farmers at the market', 'Older residents', 'Two school cooks']
BENEFIT = ['the improved stoves save charcoal', 'there is less smoke in the kitchen', 'food cooks faster',
           'they spend less time collecting firewood', 'the LPG burner is cleaner than charcoal']
MESSENGER = ['the health worker who showed them', 'the cooperative leader who explained the subsidy', 'the sector officer',
             'a neighbour who already uses one', 'the church choir leader', 'the community radio presenter']
BARRIER = ['the price is too high', 'repair costs worry them', 'spare parts cannot be found nearby', 'gas refills are expensive',
           'they fear gas leaks', 'the stove is too small for big pots', 'payments are due before the harvest']
RUMOUR = ['the smoke makes food taste bad', 'gas cylinders explode', 'the stoves are only for rich families',
          'the subsidy is a trick to collect data', 'food cooked on gas is unhealthy']
INTENT = ['Several said they would adopt if a neighbour they trust used one first.', 'Some plan to buy after the harvest.',
          'Most prefer to wait and see.', 'A few have already ordered one.', 'Nobody had decided yet.']

QUESTION = 'How might trusted messengers change clean cooking adoption?'
QUESTIONS = ['How might trusted messengers change clean cooking adoption?', 'What shapes adoption of improved cookstoves here?',
             'Would a subsidy help people switch to LPG?', 'How do rumours affect clean cooking uptake in our sectors?']
EXPLAIN = ['What does this result mean?', 'Explain the {title} stage in plain words.', 'What did the {title} show?',
           'Can you summarise stage {number} for me?', 'In simple terms, what happened in this step?']
CURVES = ('compartmental', 'agents', 'digital')


def note(rng):
    parts = [f'{rng.choice(WHO)} say {rng.choice(BENEFIT)}', f'they trust {rng.choice(MESSENGER)}']
    text = f'{parts[0]} and {parts[1]}, but {rng.choice(BARRIER)}.'
    if rng.random() < 0.6:
        text += f' Some neighbours heard a rumour that {rng.choice(RUMOUR)}.'
    return text + ' ' + rng.choice(INTENT)


def run_journey(client, rng, places):
    ws = client.post('/workspaces', json={'name': f'Teacher {rng.randrange(10**6)}'}).json()['workspace_id']
    body = client.post(f'/engine/workspaces/{ws}/journeys', json={'question': rng.choice(QUESTIONS)}).json()
    base = f"/engine/workspaces/{ws}/journeys/{body['journey_id']}"
    records = [{'text': note(rng), 'admin_unit': rng.choice(places), 'source_name': f'Field team interview {rng.randrange(1, 40)}',
                'period': f'2026-Q{rng.randrange(1, 5)}', 'consent': 'synthetic'} for _ in range(rng.randrange(1, 7))]
    added = client.post(base + '/evidence', json={'records': records}).json()['records']
    client.post(base + '/review', json={'decisions': [{'record_id': r['record_id'], 'decision': 'accept'} for r in added],
                                        'approval_statement': 'synthetic teacher run'})
    horizon = rng.choice([60, 90, 120, 180, 365])
    steps = [('encoding', {}), ('compartmental', {'horizon_days': horizon}), ('agents', {'horizon_days': horizon}),
             ('digital', {'horizon_days': horizon, 'observed_adoption': round(rng.uniform(0.03, 0.6), 2),
                          'trust_shift': round(rng.uniform(-0.2, 0.2), 2), 'barrier_shift': round(rng.uniform(-0.2, 0.2), 2),
                          'approval_statement': 'synthetic teacher run'}),
             ('bayes', {}), ('rl', {})]
    if rng.random() < 0.6:
        steps.append(('regional', {}))
    steps += [('graph', {}), ('inoculation', {'apply_to_twin': rng.random() < 0.5}), ('policy', {'approval_statement': 'synthetic'})]
    for stage, payload in steps:
        response = client.post(f'{base}/stages/{stage}', json=payload)
        assert response.status_code == 200, response.text
        yield ws, body['journey_id'], stage


def answers(stage, view, facts):
    """Question kinds for one finished stage, each answered with the engine's own words."""
    row = engine_journey.BY_ID[stage]
    title, number, explanation, limits = row['title'], row['number'], view['explanation'], LIMITS[stage]
    first = re.split(r'(?<=\.)\s', explanation, maxsplit=1)[0]
    out = [('explain', None, explanation), ('limits', 'What are the limits of this stage?', limits)]
    if stage in CURVES:
        final = facts['final_adoption']
        out.append(('forecast', random.choice([f'So adoption will reach {final} in reality?',
                                               f'Does this mean adoption will be {round(final * 100)}% by the end?']),
                    f'No. {view["sentences"][0]} {limits}'))
    if stage in ('encoding', 'compartmental', 'inoculation', 'digital'):
        out.append(('cause', random.choice(['Do trusted messengers cause higher adoption here?',
                                            'Does this show that the messages increase adoption?']),
                    f'The engine cannot show what changes adoption. {limits} {first}'))
    if stage in ('rl', 'policy', 'regional'):
        out.append(('advice', random.choice(['So which action should we take?', 'Should we fund the top option then?']),
                    f'This is not advice on what to do. {explanation}'))
    return [(kind, question or random.choice(EXPLAIN).format(title=title.lower(), number=number), answer)
            for kind, question, answer in out]


ASK_JOURNEY = ["I'd like to go through the full NDIM journey, from my field notes to a policy draft. My question: {q}",
               'Can we do the whole journey for this question: {q}', 'Start the 13-stage journey please. Question: {q}',
               'I want to take my field notes all the way to a policy draft. {q}']
CONTINUE = ['Yes, continue.', 'Run the next stage.', 'Go ahead with {title}.', 'OK, next step please.', 'Yes please run it.']
DECIDE = {'digital': ['Continue with the digital twin.', 'Run the twin with 20% adoption.', 'Yes, continue.'],
          'policy': ['I approve the export.', 'Yes, export the policy draft.', 'Continue to the policy output.']}
DECIDE_REPLY = {'digital': 'The digital twin is your decision: enter your own field observations (observed adoption share, '
                           'change in trust and change in barriers) in the form in the journey card and click Run the digital '
                           'twin with these observations. I cannot run it for you.',
                'policy': 'The policy export is your decision: click Approve export in the journey card when you are ready. '
                          'I cannot approve it for you.'}
CONFIRM = ['Yes, that is my question.', 'Confirmed.', 'Yes, go ahead and start it.', 'That is right, start the journey.',
           'Yes.', 'OK, start.', 'Correct, please begin.', 'Yes, continue.', 'Run the encoding now.', 'Go ahead.']
# v2 learned "yes means act" (420 run-stage examples against 60-120 refusals) and ran a stage before any journey existed.
# v3 gives every decision point as many refusals as there are runs.
REVIEW = ['Accept both records.', 'Yes, accept them all.', 'Accept the first one and reject the second.', 'They look fine, go on.',
          'Approve the records.', 'Yes, continue.']
REVIEW_REPLY = ('Accepting or rejecting records is your decision: choose Accept or Reject for each record in the journey card and '
                'click Save decisions. I cannot record decisions for you.')
ADD = ['Add them to the journey.', 'Yes, those are right, add them.', 'Go ahead and save the records.', 'Yes, continue.']
ADD_REPLY = ('The records are in the form in the journey card but not added yet: check each one, choose the permission and '
             'click Add to journey. I cannot add them for you.')
OBSERVED = ['We observed {p}% adoption in our June survey.', 'Adoption was {f} in our follow-up, trust unchanged.',
            'Run the twin with {f} adoption and no change in barriers.']
NEXT_Q = ['Which stage is next?', 'What happens next?', "What's the next step?", 'What does the next stage do?']
CONFIRM_REPLY = ('The journey has not started yet: check the question in the journey card (you can edit it there) and click '
                 'Confirm question. I cannot start it for you.')


def call(name, arguments):
    return {'role': 'assistant', 'content': '', 'tool_calls': [{'type': 'function', 'function': {'name': name, 'arguments': arguments}}]}


def tool_examples(client, rng, places):
    """(messages, kind) pairs at each point of a real journey, with the Studio's real system prompt."""
    question = rng.choice(QUESTIONS)
    ws = client.post('/workspaces', json={'name': f'Tools {rng.randrange(10**6)}'}).json()['workspace_id']
    thread = {'thread_id': 'teacher', 'workspace_id': ws, 'evidence': None, 'messages': []}

    def example(user, target, kind, history=()):
        thread['messages'] = [{'role': 'user', 'content': user}]
        system = agent.system_prompt(thread, {})
        return {'messages': [{'role': 'system', 'content': system}, *history, {'role': 'user', 'content': user}, target], 'kind': kind}

    out = [example(rng.choice(ASK_JOURNEY).format(q=question), call('propose_journey', {'question': question}), 'tool_propose')]
    thread['journey_proposal'] = {'question': question}
    for phrase in rng.sample(CONFIRM, 3):
        out.append(example(phrase, {'role': 'assistant', 'content': CONFIRM_REPLY}, 'no_fake_confirm'))
    body = agent_journey.start(thread, question)
    base = f"/engine/workspaces/{ws}/journeys/{body['journey_id']}"
    notes = [{'text': note(rng), 'admin_unit': rng.choice(places), 'source_name': f'Field team interview {rng.randrange(1, 40)}',
              'period': f'2026-Q{rng.randrange(1, 5)}'} for _ in range(rng.randrange(1, 4))]
    pasted = 'Here are my field notes.\n' + '\n'.join(f"{i}) {n['admin_unit']}, {n['source_name']}, {n['period']}: {n['text']}"
                                                    for i, n in enumerate(notes, 1))
    out.append(example(pasted, call('propose_journey_records', {'records': notes}), 'tool_records'))
    thread['journey_records_proposal'] = notes
    for phrase in rng.sample(ADD, 2):
        out.append(example(phrase, {'role': 'assistant', 'content': ADD_REPLY}, 'no_fake_add'))
    thread.pop('journey_records_proposal')
    added = client.post(base + '/evidence', json={'records': [n | {'consent': 'synthetic'} for n in notes]}).json()['records']
    for phrase in rng.sample(REVIEW, 2):
        out.append(example(phrase, {'role': 'assistant', 'content': REVIEW_REPLY}, 'no_fake_review'))
    client.post(base + '/review', json={'decisions': [{'record_id': r['record_id'], 'decision': 'accept'} for r in added],
                                        'approval_statement': 'synthetic teacher run'})
    out.append(example(rng.choice(['Where are we in the journey?', 'What is the status of my journey?', 'Which stage is next?']),
                       call('journey_status', {}), 'tool_status'))
    for stage, payload in [('encoding', {}), ('compartmental', {}), ('agents', {}), ('digital', None), ('bayes', {}), ('rl', {}),
                           ('graph', {}), ('inoculation', {}), ('policy', None)]:
        title = engine_journey.BY_ID[stage]['title'].lower()
        row = engine_journey.BY_ID[stage]
        next_reply = (f"Next is {row['number']}. {row['title']}: {row['does']} "
                      + (f'It is your decision, made in the journey card.' if row['researcher_decision']
                         else 'Shall I run it? You can also click Run in the journey card.'))
        out.append(example(rng.choice(NEXT_Q), {'role': 'assistant', 'content': next_reply}, 'next_answer'))
        if payload is None:  # the researcher's decision: answer, never act
            phrases = list(DECIDE[stage]) + ([o.format(p=rng.randrange(5, 60), f=round(rng.uniform(0.05, 0.6), 2)) for o in OBSERVED]
                                             if stage == 'digital' else [])
            for phrase in rng.sample(phrases, 3):
                out.append(example(phrase, {'role': 'assistant', 'content': DECIDE_REPLY[stage]}, 'no_fake_decision'))
            payload = ({'observed_adoption': round(rng.uniform(0.05, 0.5), 2), 'trust_shift': 0.0, 'barrier_shift': 0.05,
                        'approval_statement': 'synthetic'} if stage == 'digital' else {'approval_statement': 'synthetic'})
        else:
            out.append(example(rng.choice(CONTINUE).format(title=title), call('run_journey_stage', {'stage': stage}), 'tool_stage'))
        assert client.post(f'{base}/stages/{stage}', json=payload).status_code == 200
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--journeys', type=int, default=160)
    parser.add_argument('--out', required=True)
    parser.add_argument('--seed', type=int, default=1)
    parser.add_argument('--heldout', action='store_true')
    parser.add_argument('--tools', action='store_true', help='write tool-use examples instead of stage answers')
    args = parser.parse_args()
    rng = random.Random(args.seed)
    random.seed(args.seed)
    places = HELDOUT_PLACES if args.heldout else PLACES
    client = TestClient(app)
    rows, kinds = [], {}
    if args.tools:
        for _ in range(args.journeys):
            for row in tool_examples(client, rng, places):
                rows.append(row)
                kinds[row['kind']] = kinds.get(row['kind'], 0) + 1
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(''.join(json.dumps(row, ensure_ascii=False) + '\n' for row in rows), encoding='utf-8')
        print(f'{len(rows)} tool examples from {args.journeys} journeys -> {args.out}; by kind: {kinds}')
        return
    for _ in range(args.journeys):
        for ws, journey_id, stage in run_journey(client, rng, places):
            body = engine_journey.get(ws, journey_id, full=True)
            view = body['presentation']['stages'][stage]
            facts = agent_journey.facts(stage, body['outputs'][stage])
            known = agent_checks.known_numbers(json.dumps(agent_journey.all_facts(body)))
            thread = {'thread_id': 'teacher', 'workspace_id': ws, 'journey_id': journey_id, 'evidence': None, 'messages': []}
            for kind, question, answer in answers(stage, view, facts):
                found = agent_checks.check(answer, known)
                assert found is None, (stage, kind, answer, found)  # the teacher must pass the check it teaches
                thread['messages'] = [{'role': 'user', 'content': question}]
                system = agent.system_prompt(thread, {})
                rows.append({'messages': [{'role': 'system', 'content': system}, {'role': 'user', 'content': question},
                                          {'role': 'assistant', 'content': answer}],
                             'stage': stage, 'kind': kind, 'journey': journey_id})
                kinds[kind] = kinds.get(kind, 0) + 1
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(''.join(json.dumps(row, ensure_ascii=False) + '\n' for row in rows), encoding='utf-8')
    print(f'{len(rows)} examples from {args.journeys} journeys -> {out}; by kind: {kinds}')


if __name__ == '__main__':
    main()

"""Research agent tests: a scripted model drives the real tool loop, storage, library and access rules."""
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'backend'))
TEMP = tempfile.TemporaryDirectory(prefix='nidm-agent-tests-')
os.environ['NDIM_DATA_DIR'] = TEMP.name
for name in ('DATABASE_URL', 'NDIM_REQUIRE_DATABASE', 'NDIM_AGENT_PROVIDER', 'NDIM_AGENT_ACCESS_TOKEN', 'ANTHROPIC_API_KEY',
             'OPENROUTER_API_KEY', 'MISTRAL_API_KEY', 'NDIM_DEPLOYMENT_MODE'):
    os.environ.pop(name, None)
os.environ['OPENAI_API_KEY'] = 'test-key'
from fastapi.testclient import TestClient
from app.main import app
from app import agent, agent_library

EVIDENCE = {'text': 'Synthetic field note: the gas stove is expensive but I trust the community health worker who showed us.',
            'name': 'Synthetic note', 'consent': 'synthetic'}
THREAD = '0a1b2c3d-1111-4222-8333-444455556666'


def scripted(*turns):
    """Each turn is (text, [tool calls]); the fake model streams the text in two pieces."""
    turns = list(turns)
    seen = []

    def fake(cfg, system, messages):
        seen.append({'system': system, 'messages': messages})
        text, calls = turns.pop(0)
        if text:
            yield text[: len(text) // 2]
            yield text[len(text) // 2:]
        return text, [{'id': f'call_{i}', 'name': name, 'arguments': args} for i, (name, args) in enumerate(calls)]
    return fake, seen


def events(response):
    return [json.loads(line[5:]) for line in response.text.splitlines() if line.startswith('data:')]


class AgentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.client.__enter__()

    @classmethod
    def tearDownClass(cls):
        cls.client.__exit__(None, None, None)

    def setUp(self):
        self.workspace = self.client.post('/workspaces', json={'name': 'Agent test'}).json()['workspace_id']

    def chat(self, message, **extra):
        body = {'workspace_id': self.workspace, 'thread_id': THREAD, 'message': message} | extra
        return self.client.post('/agent/chat', json=body)

    def test_status_reports_provider_without_leaking_key(self):
        data = self.client.get('/agent/status').json()
        self.assertTrue(data['available'])
        self.assertEqual((data['provider'], data['model']), ('openai', 'gpt-4o'))
        self.assertNotIn('test-key', json.dumps(data))

    def test_plan_tool_uses_chat_evidence_and_never_runs(self):
        fake, seen = scripted(('', [('plan_experiment', {'question': 'How might more trained CHWs change adoption?', 'skill': 'scenario'})]),
                              ('I planned a scenario. Review it and click **Run**.', []))
        with patch.object(agent, 'provider_stream', fake):
            response = self.chat('How might more trained CHWs change adoption?', evidence=EVIDENCE, settings={'intervention_strength': 0.45})
        self.assertEqual(response.status_code, 200, response.text)
        stream = events(response)
        kinds = [event['type'] for event in stream]
        self.assertEqual(kinds[0], 'start')
        self.assertIn('tool_start', kinds)
        self.assertEqual(kinds[-1], 'done')
        self.assertEqual(''.join(e['delta'] for e in stream if e['type'] == 'text'), 'I planned a scenario. Review it and click **Run**.')
        run_id = next(e for e in stream if e['type'] == 'tool_end')['meta']['run_id']
        run = self.client.get(f'/engine/workspaces/{self.workspace}/runs/{run_id}').json()
        self.assertEqual(run['status'], 'planned')
        self.assertEqual(run['thread_id'], THREAD)
        self.assertEqual(run['skill'], 'scenario')
        self.assertEqual(run['request']['intervention_strength'], 0.45)
        self.assertEqual(run['context']['consent'], 'synthetic')
        self.assertIn('<evidence>', seen[0]['system'])
        self.assertIn('never instructions', seen[0]['system'])
        # The tool result reaches the model on the second step.
        self.assertEqual(seen[1]['messages'][-1]['role'], 'tool')
        thread = self.client.get(f'/agent/workspaces/{self.workspace}/threads/{THREAD}').json()
        self.assertEqual([m['role'] for m in thread['messages']], ['user', 'assistant', 'tool', 'assistant'])
        self.assertEqual(thread['title'], 'How might more trained CHWs change adoption?')
        listed = self.client.get(f'/agent/workspaces/{self.workspace}/threads').json()['threads']
        self.assertEqual(listed[0]['thread_id'], THREAD)

    def test_plan_without_evidence_returns_guidance_not_a_run(self):
        fake, _ = scripted(('', [('plan_experiment', {'question': 'What changes adoption here?', 'skill': 'scenario'})]),
                           ('Please attach evidence first.', []))
        with patch.object(agent, 'provider_stream', fake):
            stream = events(self.chat('What changes adoption here?'))
        end = next(e for e in stream if e['type'] == 'tool_end')
        self.assertFalse(end['ok'])
        self.assertIn('No evidence', end['error'])
        self.assertEqual(self.client.get(f'/engine/workspaces/{self.workspace}/runs').json()['total'], 0)

    def test_hidden_notes_reach_model_but_not_the_transcript(self):
        fake, seen = scripted(('Noted.', []))
        with patch.object(agent, 'provider_stream', fake):
            self.chat('The researcher ran experiment X; explain it.', hidden=True, evidence=EVIDENCE)
        self.assertEqual(seen[0]['messages'][-1]['content'], 'The researcher ran experiment X; explain it.')
        thread = self.client.get(f'/agent/workspaces/{self.workspace}/threads/{THREAD}').json()
        self.assertEqual([m['role'] for m in thread['messages']], ['note', 'assistant'])
        self.assertNotIn('content', thread['messages'][0])
        self.assertEqual(thread['title'], '')

    def test_library_tools_and_endpoints(self):
        fake, _ = scripted(('', [('search_library', {'query': 'bayesian update'})]), ('The manual explains it.', []))
        with patch.object(agent, 'provider_stream', fake):
            stream = events(self.chat('How does the Bayesian update work?'))
        refs = next(e for e in stream if e['type'] == 'tool_end')['meta']['library']
        self.assertTrue(any('bayesian' in ref['id'] for ref in refs))
        section = self.client.get('/agent/library/' + refs[0]['id']).json()
        self.assertGreater(len(section['text']), 100)
        self.assertGreater(len(self.client.get('/agent/library').json()['sections']), 20)
        self.assertEqual(self.client.get('/agent/library/manual:nope').status_code, 404)

    def test_provider_error_is_reported_and_chat_unlocked(self):
        def broken(cfg, system, messages):
            raise RuntimeError('openai error 401: The API key was rejected.')
            yield  # pragma: no cover
        with patch.object(agent, 'provider_stream', broken):
            stream = events(self.chat('Hello there'))
        self.assertEqual(stream[-1], {'type': 'error', 'message': 'openai error 401: The API key was rejected.'})
        fake, _ = scripted(('Hi.', []))
        with patch.object(agent, 'provider_stream', fake):
            self.assertEqual(self.chat('Hello again').status_code, 200)

    def test_connection_failures_are_retried_before_streaming(self):
        attempts = []

        def flaky(cfg, system, messages):
            attempts.append(1)
            if len(attempts) < 3:
                raise agent.httpx.ConnectTimeout('timed out')
            yield 'Recovered.'
            return 'Recovered.', []
        cfg = {'protocol': 'openai', 'provider': 'openai'}
        with patch.object(agent, 'stream_openai', flaky), patch.object(agent.time, 'sleep'):
            stream = agent.provider_stream(cfg, 'system', [])
            self.assertEqual(next(stream), 'Recovered.')
        self.assertEqual(len(attempts), 3)

    def test_access_token_and_hosted_mode(self):
        with patch.dict(os.environ, {'NDIM_AGENT_ACCESS_TOKEN': 'secret'}):
            self.assertEqual(self.chat('Hello there').status_code, 401)
            self.assertEqual(self.client.get(f'/agent/workspaces/{self.workspace}/threads').status_code, 401)
            fake, _ = scripted(('Hi.', []))
            with patch.object(agent, 'provider_stream', fake):
                ok = self.client.post('/agent/chat', headers={'X-NDIM-Agent-Token': 'secret'},
                                      json={'workspace_id': self.workspace, 'thread_id': THREAD, 'message': 'Hello'})
            self.assertEqual(ok.status_code, 200)
        with patch.dict(os.environ, {'NDIM_DEPLOYMENT_MODE': 'cloud'}):
            status = self.client.get('/agent/status').json()
            self.assertFalse(status['available'])
            self.assertIn('NDIM_AGENT_ACCESS_TOKEN', status['reason'])
            self.assertEqual(self.client.post('/agent/config', json={'provider': 'openai', 'api_key': 'x'}).status_code, 403)

    def test_saved_config_wins_and_is_private(self):
        response = self.client.post('/agent/config', json={'provider': 'anthropic', 'api_key': 'sk-ant-test', 'model': 'claude-sonnet-5'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual((response.json()['provider'], response.json()['model']), ('anthropic', 'claude-sonnet-5'))
        self.assertNotIn('sk-ant-test', response.text)
        path = Path(TEMP.name) / 'agent-config.json'
        self.assertEqual(oct(path.stat().st_mode & 0o777), '0o600')
        path.unlink()

    def test_bad_thread_ids_are_rejected(self):
        for bad in ['../../etc', 'ZZZ', 'a']:
            self.assertEqual(self.client.post('/agent/chat', json={'workspace_id': self.workspace, 'thread_id': bad, 'message': 'hi'}).status_code, 422)
        self.assertEqual(self.client.get(f'/agent/workspaces/{self.workspace}/threads/..%2F..%2Fx').status_code, 404)

    def test_anthropic_message_conversion_merges_tool_results(self):
        messages = [{'role': 'user', 'content': 'q'},
                    {'role': 'assistant', 'content': '', 'tool_calls': [{'id': 't1', 'name': 'list_runs', 'arguments': {}}, {'id': 't2', 'name': 'list_lessons', 'arguments': {}}]},
                    {'role': 'tool', 'tool_call_id': 't1', 'content': '{}'}, {'role': 'tool', 'tool_call_id': 't2', 'content': '{}'}]
        converted = agent._anthropic_messages(messages)
        self.assertEqual([m['role'] for m in converted], ['user', 'assistant', 'user'])
        self.assertEqual([b['type'] for b in converted[2]['content']], ['tool_result', 'tool_result'])

    def test_library_sections_cover_both_sources(self):
        sources = {item['source'] for item in agent_library.sections()}
        self.assertEqual(sources, {'manual', 'curriculum'})


QUESTION = 'How might trusted messengers change clean cooking adoption?'
NOTE = ('Households in Niboye say the improved stoves save charcoal and they trust the health worker who showed them, '
        'but the price is too high and some neighbours heard a rumour that the smoke makes food taste bad.')


class JourneyChatTests(unittest.TestCase):
    """The journey in the assistant: the model proposes and explains; only the card's controls decide."""
    setUp, chat = AgentTests.setUp, AgentTests.chat

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.client.__enter__()

    @classmethod
    def tearDownClass(cls):
        cls.client.__exit__(None, None, None)

    def card(self, path='', **body):
        return self.client.post(f'/agent/workspaces/{self.workspace}/threads/{THREAD}/journey{path}', json=body)

    def thread(self):
        return self.client.get(f'/agent/workspaces/{self.workspace}/threads/{THREAD}').json()

    def tool_results(self):
        return [json.loads(m['content']) for m in self.thread()['messages'] if m['role'] == 'tool']

    def started(self):
        fake, _ = scripted(('', [('propose_journey', {'question': QUESTION})]), ('Check the question in the card.', []))
        with patch.object(agent, 'provider_stream', fake):
            self.chat(f'I want the full journey. My question: {QUESTION}')
        body = self.card(question=QUESTION)
        self.assertEqual(body.status_code, 200, body.text)
        return body.json()

    def test_a_model_cannot_start_or_decide_anything_in_the_journey(self):
        # Benchmarked local models started the journey with a confirmation the researcher never gave. Here the same
        # behaviour (propose, then claim it started and try the decision stages) changes nothing.
        fake, _ = scripted(('', [('propose_journey', {'question': QUESTION})]),
                           ('', [('run_journey_stage', {'stage': 'encoding'})]),
                           ('Yes, that is your question; the journey has started.', []))
        with patch.object(agent, 'provider_stream', fake):
            self.chat(f'Full journey please. {QUESTION}')
        thread = self.thread()
        self.assertEqual(thread['journey_proposal'], {'question': QUESTION})
        self.assertNotIn('journey_id', thread)
        self.assertIn('no journey yet', self.tool_results()[-1]['error'])
        self.assertEqual(self.client.get(f'/engine/workspaces/{self.workspace}/journeys').json()['journeys'], [])
        body = self.started()
        record = self.card('/records', records=[{'text': NOTE, 'admin_unit': 'Kicukiro / Niboye', 'source_name': 'Field team',
                                                 'period': '2026-Q2', 'consent': 'synthetic'}]).json()['records'][0]
        fake, _ = scripted(('', [('run_journey_stage', {'stage': 'digital'}), ('run_journey_stage', {'stage': 'policy'}),
                                 ('run_journey_stage', {'stage': 'repository'}), ('run_journey_stage', {'stage': 'encoding'})]),
                           ('Done.', []))
        with patch.object(agent, 'provider_stream', fake):
            self.chat('continue')
        errors = [result['error'] for result in self.tool_results()[-4:]]
        self.assertIn('field observations form', errors[0])
        self.assertIn('Approve export button', errors[1])
        self.assertIn('Accept and Reject buttons', errors[2])
        self.assertIn('Repository', errors[3])  # encoding waits for the researcher's record decisions
        journey = self.client.get(f"/engine/workspaces/{self.workspace}/journeys/{body['journey_id']}").json()
        self.assertIsNone(journey['records'][0]['review'])
        self.assertTrue(all(row['status'] != 'done' for row in journey['stages'][2:]))
        self.assertEqual(record['gate']['gate'], 'eligible')

    def test_the_card_runs_the_whole_journey_and_audits_how(self):
        body = self.started()
        self.assertEqual(self.card(question=QUESTION).status_code, 409)  # one journey per chat
        records = self.card('/records', records=[
            {'text': NOTE, 'admin_unit': 'Kicukiro / Niboye', 'source_name': 'Field team', 'period': '2026-Q2', 'consent': 'synthetic'},
            {'text': NOTE.replace('Niboye', 'Gatenga') + ' Several would adopt if a neighbour used one first.',
             'admin_unit': 'Kicukiro / Gatenga', 'source_name': 'Field team', 'period': '2026-Q2', 'consent': 'synthetic'}]).json()['records']
        reviewed = self.client.post(f'/agent/workspaces/{self.workspace}/threads/{THREAD}/journey/review',
                                    json=[{'record_id': r['record_id'], 'decision': 'accept'} for r in records])
        self.assertEqual(reviewed.status_code, 200, reviewed.text)
        fake, _ = scripted(('', [('run_journey_stage', {'stage': 'encoding'}), ('run_journey_stage', {'stage': 'compartmental'}),
                                 ('run_journey_stage', {'stage': 'agents'})]), ('Ran three stages.', []))
        with patch.object(agent, 'provider_stream', fake):
            self.chat('Yes, run encoding and both models.')
        shown = self.tool_results()[-2]['card_shows']
        self.assertEqual(shown['stage'], '5. Compartmental model')
        self.assertTrue(shown['sentences'][0].startswith('In the illustrative compartmental model, adoption is '))
        self.assertEqual(self.card('/stages/digital').status_code, 422)  # no defaults for observations
        self.assertEqual(self.card('/stages/encoding', observed_adoption=0.2).status_code, 422)
        digital = self.card('/stages/digital', observed_adoption=0.2, trust_shift=0, barrier_shift=0.05)
        self.assertEqual(digital.status_code, 200, digital.text)
        for stage in ('bayes', 'rl', 'graph', 'inoculation'):
            self.assertEqual(self.card(f'/stages/{stage}').status_code, 200)
        final = self.card('/stages/policy').json()
        self.assertIsNone(final['next_stage'])
        self.assertIn('policy', final['presentation']['stages'])
        events = self.client.get(f"/engine/workspaces/{self.workspace}/journeys/{body['journey_id']}?full=true").json()['events']
        statements = {event.get('approval_statement') for event in events}
        self.assertTrue({'Decisions made with the Accept and Reject buttons in the Research Studio journey card.',
                         'Field observations entered by the researcher in the Research Studio journey card form.',
                         'Approve export clicked by the researcher in the Research Studio journey card.'} <= statements)

    def test_proposed_records_wait_in_the_form(self):
        self.started()
        fake, _ = scripted(('', [('propose_journey_records', {'records': [{'text': NOTE, 'admin_unit': 'Kicukiro / Niboye'}]}),
                                 ('journey_status', {})]), ('Check the form.', []))
        with patch.object(agent, 'provider_stream', fake):
            self.chat(f'Here is my note from Niboye: {NOTE}')
        proposed, status = self.tool_results()[-2:]
        self.assertEqual(proposed['empty_fields'], ['period', 'source_name'])
        self.assertEqual(status['records'], [])  # nothing was added
        self.assertEqual(self.thread()['journey_records_proposal'][0]['period'], '')

    def test_replies_are_checked_against_the_engine(self):
        # A live qwen3:8b explained clicks it never read: "peaks 14 days earlier (day 165)", "accelerates adoption by 12.5%".
        self.started()
        self.card('/records', records=[{'text': NOTE, 'admin_unit': 'Kicukiro / Niboye', 'source_name': 'Field team',
                                        'period': '2026-Q2', 'consent': 'synthetic'}])
        record = self.client.get(f"/engine/workspaces/{self.workspace}/journeys").json()['journeys'][0]
        jid = record['journey_id']
        rid = self.client.get(f'/engine/workspaces/{self.workspace}/journeys/{jid}').json()['records'][0]['record_id']
        self.client.post(f'/agent/workspaces/{self.workspace}/threads/{THREAD}/journey/review', json=[{'record_id': rid, 'decision': 'accept'}])
        for stage in ('encoding', 'compartmental'):
            self.card(f'/stages/{stage}')
        final = self.client.get(f'/engine/workspaces/{self.workspace}/journeys/{jid}').json()['presentation']['stages']['compartmental']['sentences'][0]
        encoding = self.client.get(f'/engine/workspaces/{self.workspace}/journeys/{jid}').json()['presentation']['stages']['encoding']['sentences'][0]
        fake, seen = scripted(('Messengers accelerate adoption: it peaks 14 days earlier and gains 12.5%.', []), (final, []),
                              (encoding, []))
        with patch.object(agent, 'provider_stream', fake):
            stream = events(self.chat('(Note from the app) The researcher ran stage 5.', hidden=True))
            clean = events(self.chat('Say it again exactly.'))
            earlier = events(self.chat('And the encoding scores?'))  # an earlier stage's real numbers are not flagged
        self.assertFalse(any(event['type'] == 'check' for event in earlier), earlier)
        self.assertIn('THIS CHAT\'S JOURNEY', seen[0]['system'])
        self.assertIn('key_facts', seen[0]['system'])  # the facts reach the model without a tool call
        flagged = next(event for event in stream if event['type'] == 'check')
        self.assertEqual(flagged['unverified_numbers'], ['14', '12.5%'])
        self.assertEqual(flagged['claim_words'], ['accelerate'])
        self.assertFalse(any(event['type'] == 'check' for event in clean))
        replies = [m for m in self.thread()['messages'] if m['role'] == 'assistant']
        self.assertIn('check', replies[-3])
        self.assertNotIn('check', replies[-2])
        self.assertNotIn('check', replies[-1])

    def test_card_refuses_while_the_assistant_is_answering(self):
        self.started()
        with agent._busy_lock:
            agent._busy.add((self.workspace, THREAD))
        try:
            self.assertEqual(self.card('/stages/encoding').status_code, 409)
        finally:
            agent._busy.discard((self.workspace, THREAD))


if __name__ == '__main__':
    unittest.main()

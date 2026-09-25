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


if __name__ == '__main__':
    unittest.main()

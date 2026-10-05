"""Online sync of approved answers (backend/app/answer_sync.py): the privacy check, the settings, what is sent and
withdrawn, and how other researchers' answers are recalled. A fake sync service stands in for the Worker; set
NDIM_SYNC_TEST_URL to a local `wrangler dev` (see scripts/test_answer_sync_worker.py) to also run against the real one.
"""
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'backend'))
TEMP = tempfile.TemporaryDirectory(prefix='nidm-sync-tests-')
os.environ['NDIM_DATA_DIR'] = TEMP.name
for name in ('DATABASE_URL', 'NDIM_REQUIRE_DATABASE', 'NDIM_AGENT_PROVIDER', 'NDIM_AGENT_ACCESS_TOKEN', 'ANTHROPIC_API_KEY',
             'OPENROUTER_API_KEY', 'MISTRAL_API_KEY', 'NDIM_DEPLOYMENT_MODE', 'NDIM_SYNC_TOKEN', 'NDIM_SYNC_URL'):
    os.environ.pop(name, None)
os.environ['OPENAI_API_KEY'] = 'test-key'
import httpx
from fastapi.testclient import TestClient
from app.main import app
from app import agent, agent_learning, answer_sync

NOTE = ('Mukamana Odette told us on Tuesday that the gas stove is expensive, but she trusts Jean Bosco the community '
        'health worker from Gatenga who showed the family how to light it safely.')
EVIDENCE = {'text': NOTE, 'name': 'Visit to Gatenga', 'consent': 'research_use'}
THREAD = '0a1b2c3d-1111-4222-8333-444455556666'
LIVE = os.getenv('NDIM_SYNC_TEST_URL')


class PrivacyCheck(unittest.TestCase):
    """Adversarial answers: each must be held back; ordinary engine explanations must pass."""

    def held(self, answer, names=()):
        return answer_sync.check(answer, [NOTE], names)

    def test_plain_explanations_pass(self):
        for answer in ['Trust scored higher than barrier in this illustrative model.',
                       'Adoption rose from 0.41 to 0.876 by day 179; the intervention strength was 0.3.',
                       'Runs from 2020-2026 and the run of 2026-10-05 agree within 0.02.',
                       'A community health worker is a trusted messenger in many Rwandan villages.',
                       'In Kigali and across Rwanda, the engine reads English keywords only.']:
            self.assertEqual(self.held(answer), [], answer)

    def test_quotes_of_the_evidence_are_held_back_however_disguised(self):
        for answer in ['She said the gas stove is expensive, but she trusts the worker.',
                       'THE GAS STOVE IS EXPENSIVE BUT SHE TRUSTS — so trust wins.',
                       'the gas\nstove is\nexpensive, but\nshe trusts',
                       'the g​as stove is expensive but she trusts',  # hidden character inside a word
                       'thé gas stové is expensive but shé trusts']:  # accents added
            self.assertTrue(any('repeats words' in r or 'hidden' in r for r in self.held(answer)), answer)

    def test_names_from_the_notes_and_workspace_are_held_back(self):
        self.assertIn('Odette', ' '.join(self.held('Odette prefers the stove when it is safe.')))
        self.assertIn('Bosco', ' '.join(self.held('Trust in bosco explains the result.')))  # lower case too
        self.assertIn('Gatenga', ' '.join(self.held('Households in GATENGA trust health workers.')))
        self.assertTrue(self.held('This is about the Umucyo Cooperative.', names=['Umucyo']))  # a workspace or record name
        self.assertEqual(self.held('Tuesday visits found trust mattered.'), [])  # common capitalised words are fine

    def test_contact_details_and_ids_are_held_back(self):
        for answer in ['Write to jane.doe@example.org for the notes.', 'Email jane (at) example (dot) org.',
                       'Call +250 788 123 456.', 'Call 0788123456.', 'Phone 078-812-3456 after 5.',
                       'Her ID is 1 1990 8 0012345 0 12.', 'Case RW2026A4471 was interviewed.',
                       'See https://drive.example.com/file/abc for the transcript.', 'Ask @mukamana_o on X.']:
            self.assertTrue(self.held(answer), answer)

    def test_length_limits(self):
        self.assertTrue(self.held(''))
        self.assertTrue(self.held('x ' * 2001))


class FakeService:
    """The Worker's behaviour (src/shared-answers.ts), in memory, behind httpx.MockTransport."""

    def __init__(self):
        self.rows, self.clock, self.requests = {}, 0, []

    def __call__(self, request):
        self.requests.append(request)
        if request.headers.get('Authorization') != 'Bearer team-key' or not request.headers.get('X-NDIM-Install'):
            return httpx.Response(401, json={'error': 'A valid access key is needed.'})
        owner = request.headers['X-NDIM-Install']
        self.clock += 1
        if request.method == 'POST':
            for item in json.loads(request.content)['answers']:
                assert set(item) == {'id', 'kind', 'answer'}, item
                self.rows[item['id']] = item | {'owner': owner, 'updated_at': f'{self.clock:06d}', 'deleted': False}
            return httpx.Response(200, json={'saved': 1})
        if request.method == 'DELETE':
            row = self.rows.get(request.url.path.rsplit('/', 1)[1])
            if not row or row['owner'] != owner or row['deleted']:
                return httpx.Response(404, json={'error': 'No answer of yours with that id.'})
            row.update(answer='', deleted=True, updated_at=f'{self.clock:06d}')
            return httpx.Response(204)
        since = request.url.params.get('since', '')
        rows = sorted((r for r in self.rows.values() if r['owner'] != owner and r['updated_at'] > since), key=lambda r: r['updated_at'])
        return httpx.Response(200, json={'answers': [{'id': r['id'], 'deleted': True, 'updated_at': r['updated_at']} if r['deleted'] else
                                                     {k: r[k] for k in ('id', 'kind', 'answer', 'updated_at')} for r in rows],
                                         'cursor': rows[-1]['updated_at'] if rows else since, 'more': False})


def scripted(*texts):
    texts, seen = list(texts), []

    def fake(cfg, system, messages):
        seen.append(system)
        text = texts.pop(0)
        yield text
        return text, []
    return fake, seen


class SyncThroughTheEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.client.__enter__()

    @classmethod
    def tearDownClass(cls):
        cls.client.__exit__(None, None, None)

    def setUp(self):
        self.workspace = self.client.post('/workspaces', json={'name': 'Umucyo Cooperative'}).json()['workspace_id']
        agent_learning.save({'lessons': [], 'terms': []})
        for name in ('sync.json', 'shared-answers.json'):
            (Path(TEMP.name) / 'learning' / name).unlink(missing_ok=True)
        self.service = FakeService()
        real = answer_sync._client
        self.patches = [patch.object(answer_sync, '_client', lambda data: httpx.Client(
            transport=httpx.MockTransport(self.service), base_url='https://sync.test', headers=real(data).headers)),
            patch.object(answer_sync, 'sync_soon', lambda evidence_for: answer_sync.enabled() and answer_sync.sync(evidence_for))]
        for item in self.patches:
            item.start()

    def tearDown(self):
        for item in self.patches:
            item.stop()

    def chat(self, message, **extra):
        body = {'workspace_id': self.workspace, 'thread_id': THREAD, 'message': message} | extra
        response = self.client.post('/agent/chat', json=body)
        self.assertEqual(response.status_code, 200, response.text)

    def replies(self):
        thread = self.client.get(f'/agent/workspaces/{self.workspace}/threads/{THREAD}').json()
        return [m for m in thread['messages'] if m['role'] == 'assistant' and m.get('content')]

    def rate(self, message, **body):
        response = self.client.post(f"/agent/workspaces/{self.workspace}/threads/{THREAD}/messages/{message['id']}/feedback", json=body)
        self.assertEqual(response.status_code, 200, response.text)
        return response.json()

    def answers(self, *texts):
        fake, seen = scripted(*texts)
        with patch.object(agent, 'provider_stream', fake):
            for i, _ in enumerate(texts):
                self.chat(f'Question number {i} about trust and stoves?', **({'evidence': EVIDENCE} if i == 0 else {}))
        return self.replies()

    def test_sync_is_off_by_default_and_nothing_leaves(self):
        plain, = self.answers('Trust scored higher than barrier in this illustrative model.')
        self.rate(plain, rating='up', share=True)
        status = self.client.get('/agent/learning/sync').json()
        self.assertFalse(status['enabled'])
        self.assertEqual([row['status'] for row in status['outbox']], ['will share'])  # shown before anything leaves
        self.assertEqual(self.service.requests, [])
        self.assertEqual(self.client.put('/agent/learning/sync', json={'enabled': True}).status_code, 422)  # needs a key
        self.assertEqual(self.client.post('/agent/learning/sync/run').status_code, 409)

    def test_only_checked_answers_are_sent_and_withdrawals_propagate(self):
        plain, naming, contact, unshared = self.answers(
            'Trust scored higher than barrier in this illustrative model.', 'Odette trusts the health worker most.',
            'Ask the team at field@example.org for the data.', 'Barrier words were rare in this note.')
        for reply in (plain, naming, contact):
            self.rate(reply, rating='up', share=True)
        self.rate(unshared, rating='up')
        status = self.client.put('/agent/learning/sync', json={'enabled': True, 'token': 'team-key'}).json()
        self.assertIsNone(status['last_sync']['error'])
        self.assertEqual(sorted(row['status'] for row in status['outbox']), ['held back', 'held back', 'shared'])
        sent = [json.loads(r.content) for r in self.service.requests if r.method == 'POST']
        self.assertEqual([item['answer'] for body in sent for item in body['answers']],
                         ['Trust scored higher than barrier in this illustrative model.'])
        everything = json.dumps(sent)
        for private in ('Question number', 'Odette', 'example.org', 'Umucyo', 'Gatenga', 'expensive', self.workspace):
            self.assertNotIn(private, everything)
        self.assertNotIn('team-key', json.dumps(status))  # the key is never shown back
        # Unticking withdraws it online at once (sync is on).
        lesson_id = next(row['id'] for row in status['outbox'] if row['status'] == 'shared')
        self.client.post(f'/agent/learning/{lesson_id}/share', json={'share': False})
        self.assertTrue(self.service.rows[lesson_id]['deleted'])
        # Ticking again shares it again; forgetting it withdraws it too.
        self.client.post(f'/agent/learning/{lesson_id}/share', json={'share': True})
        self.assertFalse(self.service.rows[lesson_id]['deleted'])
        self.assertEqual(self.client.delete(f'/agent/learning/{lesson_id}').status_code, 204)
        self.assertTrue(self.service.rows[lesson_id]['deleted'])
        self.assertEqual(self.client.get('/agent/learning/sync').json()['withdraw'], 0)

    def test_withdrawals_wait_while_sync_is_off(self):
        plain, = self.answers('Trust scored higher than barrier in this illustrative model.')
        lesson_id = self.rate(plain, rating='up', share=True)['id']
        self.client.put('/agent/learning/sync', json={'enabled': True, 'token': 'team-key'})
        self.client.put('/agent/learning/sync', json={'enabled': False})
        count = len(self.service.requests)
        self.client.delete(f'/agent/learning/{lesson_id}')
        self.assertEqual(len(self.service.requests), count)  # off means no contact at all
        self.assertEqual(self.client.get('/agent/learning/sync').json()['withdraw'], 1)  # shown as waiting
        self.client.put('/agent/learning/sync', json={'enabled': True})
        self.assertTrue(self.service.rows[lesson_id]['deleted'])

    def test_answers_from_others_are_recalled_below_the_teams_own(self):
        self.service.rows['f' * 32] = {'id': 'f' * 32, 'kind': 'answer', 'owner': 'someone-else', 'deleted': False,
                                       'updated_at': '000001', 'answer': 'Sensitivity sweeps vary intervention strength from 0 to 1 to show how robust adoption is.'}
        self.service.rows['e' * 32] = {'id': 'e' * 32, 'kind': 'answer', 'owner': 'someone-else', 'deleted': False,
                                       'updated_at': '000002', 'answer': 'Call 0788123456 to learn about sensitivity sweeps and intervention strength.'}
        status = self.client.put('/agent/learning/sync', json={'enabled': True, 'token': 'team-key'}).json()
        self.assertEqual(status['others'], 1)  # the one with a phone number was refused on the way in too
        fake, seen = scripted('ok', 'ok')
        with patch.object(agent, 'provider_stream', fake):
            self.chat('How do sensitivity sweeps of intervention strength work?')
            self.client.put('/agent/learning/sync', json={'enabled': False})
            self.chat('How do sensitivity sweeps of intervention strength work?')
        self.assertIn('other NDIM researchers approved and shared online', seen[0])
        self.assertIn('Sensitivity sweeps vary intervention strength', seen[0])
        self.assertNotIn('Sensitivity sweeps vary', seen[1])  # sync off: other researchers' answers are not used
        # A withdrawal by its owner removes the local copy at the next pull.
        self.service.rows['f' * 32].update(deleted=True, answer='', updated_at='999999')
        self.assertEqual(self.client.put('/agent/learning/sync', json={'enabled': True}).json()['others'], 0)

    def test_an_answer_whose_chat_is_gone_is_not_shared(self):
        plain, = self.answers('Trust scored higher than barrier in this illustrative model.')
        self.rate(plain, rating='up', share=True)
        self.client.delete(f'/agent/workspaces/{self.workspace}/threads/{THREAD}')
        row, = self.client.get('/agent/learning/sync').json()['outbox']
        self.assertEqual(row['status'], 'held back')

    def test_the_public_demo_engine_never_syncs(self):
        with patch.dict(os.environ, {'NDIM_DEPLOYMENT_MODE': 'cloud', 'NDIM_AGENT_ACCESS_TOKEN': 'demo'}):
            headers = {'X-NDIM-Agent-Token': 'demo'}
            self.assertEqual(self.client.put('/agent/learning/sync', json={'enabled': True, 'token': 'team-key'}, headers=headers).status_code, 403)
            self.assertEqual(self.client.post('/agent/learning/sync/run', headers=headers).status_code, 403)
            self.assertFalse(self.client.get('/agent/learning/sync', headers=headers).json()['available'])


@unittest.skipUnless(LIVE, 'set NDIM_SYNC_TEST_URL to a local wrangler dev to run against the real Worker')
class AgainstTheLocalWorker(unittest.TestCase):
    def test_two_computers_share_and_withdraw(self):
        material = lambda lesson: ([NOTE], [])
        lesson = {'id': os.urandom(16).hex(), 'kind': 'answer', 'share': True, 'question': 'q', 'workspace_id': 'w',
                  'thread_id': 't', 'message_id': 'm', 'created_at': '', 'answer': 'Sweeps show how robust the illustrative adoption curve is.'}
        agent_learning.save({'lessons': [lesson], 'terms': []})
        answer_sync.configure(True, LIVE, 'team-key-aaaaaaaaaaaaaaaa')
        first = answer_sync.sync(material)
        self.assertEqual((first['error'], first['sent']), (None, 1))
        # A second computer: a fresh learning folder (the data folder is resolved once per process).
        here = answer_sync._folder()
        with tempfile.TemporaryDirectory() as other, patch.object(answer_sync, '_folder', lambda: Path(other)), \
                patch.object(agent_learning, '_file', lambda: Path(other) / 'lessons.json'):
            answer_sync.configure(True, LIVE, 'team-key-aaaaaaaaaaaaaaaa')
            answer_sync.sync(material)
            self.assertIn(lesson['id'], [item['id'] for item in answer_sync.others()])
            with patch.object(answer_sync, '_folder', lambda: here), patch.object(agent_learning, '_file', lambda: here / 'lessons.json'):
                agent_learning.forget(lesson['id'])
                self.assertEqual(answer_sync.sync(material)['withdrawn'], 1)
            answer_sync.sync(material)
            self.assertNotIn(lesson['id'], [item['id'] for item in answer_sync.others()])


if __name__ == '__main__':
    unittest.main()

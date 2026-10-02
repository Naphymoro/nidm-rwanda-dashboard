"""Durable mirror tests: the test plays the host (the Cloudflare Worker), which restores and pulls the data folder."""
import base64
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'backend'))
TOKEN = 'test-mirror-token'
os.environ['NDIM_MIRROR_TOKEN'] = TOKEN
os.environ['NDIM_DATA_DIR'] = tempfile.mkdtemp(prefix='nidm-mirror-')
for name in ('DATABASE_URL', 'NDIM_REQUIRE_DATABASE', 'NDIM_AGENT_ACCESS_TOKEN'):
    os.environ.pop(name, None)
from fastapi.testclient import TestClient  # noqa: E402
from app import durable_mirror  # noqa: E402
from app.main import app  # noqa: E402

QUESTION = 'How might trusted messengers change clean cooking adoption?'
THREAD = '0a0b0c0d-1111-4222-8333-444455556666'
HOST = {'X-NDIM-Mirror-Token': TOKEN}


class MirrorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.client.__enter__()

    @classmethod
    def tearDownClass(cls):
        cls.client.__exit__(None, None, None)

    def pull(self):
        """What the Worker does after a request: fetch the changes, save them, acknowledge."""
        batch = self.client.get('/__mirror/changes', headers=HOST).json()
        if batch['id']:
            self.assertEqual(self.client.post('/__mirror/ack', headers=HOST, json={'id': batch['id']}).status_code, 200)
        return batch

    def test_restore_then_keep_every_change(self):
        # Starting: nothing reads the folder until the host has restored it.
        self.assertEqual(self.client.get('/workspaces').status_code, 503)
        self.assertEqual(self.client.get('/health').json()['mirror']['status'], 'waiting for restore')
        self.assertEqual(self.client.post('/__mirror/restore', json={'done': True}).status_code, 404)  # no token
        self.assertEqual(self.client.get('/__mirror/changes', headers={'X-NDIM-Mirror-Token': 'wrong'}).status_code, 404)

        # The saved copy from the previous container: one chat with a journey, and a key trying to escape the folder.
        saved_thread = {'thread_id': THREAD, 'workspace_id': 'ndim-core', 'title': 'Saved chat', 'created_at': '2026-10-01T00:00:00+00:00',
                        'evidence': None, 'messages': [], 'journey_id': None}
        files = {f'workspaces/ndim-core/evidence/agent-chats/{THREAD}.json': json.dumps(saved_thread),
                 '../escaped.txt': 'should not be written'}
        restored = self.client.post('/__mirror/restore', headers=HOST, json={
            'files': {key: base64.b64encode(value.encode()).decode() for key, value in files.items()}, 'done': True})
        self.assertEqual(restored.status_code, 200, restored.text)
        self.assertFalse((Path(os.environ['NDIM_DATA_DIR']).parent / 'escaped.txt').exists())
        self.assertEqual(self.client.get(f'/agent/workspaces/ndim-core/threads/{THREAD}').json()['title'], 'Saved chat')
        # A second restore could write an older copy over newer work: refused.
        self.assertEqual(self.client.post('/__mirror/restore', headers=HOST, json={'done': True}).status_code, 409)

        # Defaults created after the restore are new to the host; the restored chat is not sent back.
        first = self.pull()
        self.assertTrue(first['put'])
        self.assertNotIn(f'workspaces/ndim-core/evidence/agent-chats/{THREAD}.json', first['put'])
        self.assertEqual(self.pull()['put'], {})  # acknowledged: nothing pending

        # New work is pulled; a deletion is reported.
        ws = self.client.post('/workspaces', json={'name': 'Mirror test'}).json()['workspace_id']
        fresh = '0d1e2f3a-2222-4333-8444-555566667777'
        started = self.client.post(f'/agent/workspaces/{ws}/threads/{fresh}/journey', json={'question': QUESTION}).json()
        batch = self.pull()
        self.assertTrue(any(key.endswith(started['journey_id'] + '.json') for key in batch['put']), list(batch['put']))
        self.client.delete(f'/agent/workspaces/ndim-core/threads/{THREAD}')
        self.assertEqual(self.pull()['delete'], [f'workspaces/ndim-core/evidence/agent-chats/{THREAD}.json'])

        # Large files and rebuildable folders are not kept.
        root = Path(os.environ['NDIM_DATA_DIR'])
        (root / 'uploads').mkdir(exist_ok=True)
        (root / 'uploads' / 'big.bin').write_bytes(b'x' * (durable_mirror.MAX_BYTES + 1))
        (root / 'exports').mkdir(exist_ok=True)
        (root / 'exports' / 'bundle.zip').write_bytes(b'zip')
        self.assertEqual(self.pull()['put'], {})
        self.assertEqual(self.client.get('/health').json()['mirror']['status'], 'on')

    def test_then_an_unacknowledged_batch_is_sent_again(self):
        durable_mirror.ready.wait(5)
        if not durable_mirror.ready.is_set():
            self.skipTest('runs after test_restore_then_keep_every_change')
        ws = self.client.post('/workspaces', json={'name': 'Unacknowledged'}).json()['workspace_id']
        first = self.client.get('/__mirror/changes', headers=HOST).json()  # the Worker failed to save: no ack
        self.assertTrue(any(ws in key for key in first['put']))
        again = self.pull()
        self.assertEqual(set(again['put']), set(first['put']))


if __name__ == '__main__':
    unittest.main()

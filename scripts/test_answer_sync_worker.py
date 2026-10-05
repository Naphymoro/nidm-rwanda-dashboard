"""Worker tests for shared answers (cloudflare/engine-container/src/shared-answers.ts), against a local `wrangler dev`.

Run the Worker first (local D1 only, no container):
  cd cloudflare/engine-container
  printf 'NDIM_SYNC_TOKENS=team-key-aaaaaaaaaaaaaaaa,team-key-bbbbbbbbbbbbbbbb\\nNDIM_MIRROR_TOKEN=local-only\\n' > .dev.vars
  npx wrangler d1 migrations apply ndim-engine-data --local
  npx wrangler dev --port 8799 --enable-containers=false
then: NDIM_SYNC_TEST_URL=http://127.0.0.1:8799 python3 scripts/test_answer_sync_worker.py
"""
import json
import os
import secrets
import unittest
import urllib.error
import urllib.request

URL = os.getenv('NDIM_SYNC_TEST_URL', 'http://127.0.0.1:8799').rstrip('/')
KEY_A, KEY_B = 'team-key-aaaaaaaaaaaaaaaa', 'team-key-bbbbbbbbbbbbbbbb'


def call(method, path, body=None, key=KEY_A, install=None, raw=None):
    headers = {'User-Agent': 'NDIM test', 'Content-Type': 'application/json'}
    if key:
        headers['Authorization'] = f'Bearer {key}'
    if install:
        headers['X-NDIM-Install'] = install
    data = raw if raw is not None else json.dumps(body).encode() if body is not None else None
    request = urllib.request.Request(URL + path, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(request) as response:
            text = response.read().decode()
            return response.status, json.loads(text) if text else None
    except urllib.error.HTTPError as error:
        text = error.read().decode()
        try:
            return error.code, json.loads(text)
        except ValueError:
            return error.code, text


def new_id():
    return secrets.token_hex(16)


def pull_all(install, key=KEY_A):
    cursor, seen = '', {}
    while True:
        status, page = call('GET', '/shared-answers?since=' + urllib.request.quote(cursor), key=key, install=install)
        assert status == 200, page
        for item in page['answers']:
            seen[item['id']] = item
        cursor = page['cursor']
        if not page['more']:
            return seen, cursor


class SharedAnswersWorker(unittest.TestCase):
    def setUp(self):
        self.me, self.other = secrets.token_hex(24), secrets.token_hex(24)

    def test_access_needs_a_valid_key_and_a_computer_id(self):
        self.assertEqual(call('GET', '/shared-answers', key=None, install=self.me)[0], 401)
        self.assertEqual(call('GET', '/shared-answers', key='team-key-wrong-wrong-wrong', install=self.me)[0], 401)
        self.assertEqual(call('POST', '/shared-answers', {'answers': [{'id': new_id(), 'kind': 'answer', 'answer': 'junk'}]},
                              key=None, install=self.me)[0], 401)
        self.assertEqual(call('GET', '/shared-answers', install=None)[0], 400)
        self.assertEqual(call('GET', '/__mirror/changes')[0], 404)  # the mirror stays closed to everyone outside

    def test_share_pull_and_withdraw(self):
        item = {'id': new_id(), 'kind': 'correction', 'answer': 'Encoding counts English keywords in each note.'}
        self.assertEqual(call('POST', '/shared-answers', {'answers': [item]}, install=self.me), (200, {'saved': 1}))
        mine, _ = pull_all(self.me)
        self.assertNotIn(item['id'], mine)  # a computer does not get its own answers back
        theirs, cursor = pull_all(self.other, key=KEY_B)  # another team's key reads everyone's answers
        self.assertEqual(theirs[item['id']]['answer'], item['answer'])
        self.assertEqual(set(theirs[item['id']]), {'id', 'kind', 'answer', 'updated_at'})  # no owner or key leaks
        # Another computer can neither overwrite nor withdraw it.
        call('POST', '/shared-answers', {'answers': [item | {'answer': 'Overwritten by someone else.'}]}, install=self.other)
        self.assertEqual(pull_all(secrets.token_hex(24))[0][item['id']]['answer'], item['answer'])
        self.assertEqual(call('DELETE', f"/shared-answers/{item['id']}", install=self.other)[0], 404)
        # The owner withdraws it; the next pull from the old cursor carries a marker, with no text.
        self.assertEqual(call('DELETE', f"/shared-answers/{item['id']}", install=self.me)[0], 204)
        status, page = call('GET', '/shared-answers?since=' + urllib.request.quote(cursor), key=KEY_B, install=self.other)
        marker = next(row for row in page['answers'] if row['id'] == item['id'])
        self.assertTrue(marker['deleted'])
        self.assertNotIn('answer', marker)
        self.assertEqual(call('DELETE', f"/shared-answers/{item['id']}", install=self.me)[0], 404)

    def test_only_answers_are_accepted(self):
        good = {'id': new_id(), 'kind': 'answer', 'answer': 'Trust scored higher than barrier in this illustrative model.'}
        cases = [good | {'question': 'What did the women in Niboye say?'}, good | {'kind': 'flagged'}, good | {'id': 'x' * 32},
                 good | {'answer': 'Write to me at jane.doe@example.org'}, good | {'answer': 'Call +250 788 123 456 for the data.'},
                 good | {'answer': 'ID 1 1990 8 0012345 0 12'}, good | {'answer': 'x' * 4001}, good | {'answer': ' '}]
        for bad in cases:
            status, body = call('POST', '/shared-answers', {'answers': [good, bad]}, install=self.me)
            self.assertEqual(status, 422, bad)
            self.assertEqual(body['refused'][0]['index'], 1)
        self.assertNotIn(good['id'], pull_all(self.other)[0])  # nothing of a refused batch was saved
        self.assertEqual(call('POST', '/shared-answers', {'answers': [good | {'answer': 'Adoption rose from 0.41 to 0.876 '
                                                          'between 2020-2026 (run of 2026-10-05).'}]}, install=self.me)[0], 200)
        self.assertEqual(call('POST', '/shared-answers', {'answers': []}, install=self.me)[0], 400)
        many = [{'id': new_id(), 'kind': 'answer', 'answer': 'ok answer'} for _ in range(51)]
        self.assertEqual(call('POST', '/shared-answers', {'answers': many}, install=self.me)[0], 400)
        self.assertEqual(call('POST', '/shared-answers', raw=b'{"answers": [' + b' ' * 260_000 + b']}', install=self.me)[0], 413)
        self.assertEqual(call('POST', '/shared-answers', raw=b'not json', install=self.me)[0], 400)

    def test_pull_pages_through_everything(self):
        ids = []
        for _ in range(2):
            batch = [{'id': new_id(), 'kind': 'answer', 'answer': f'Paged answer {i}.'} for i in range(50)]
            ids += [item['id'] for item in batch]
            self.assertEqual(call('POST', '/shared-answers', {'answers': batch}, install=self.me)[0], 200)
        seen, cursor = pull_all(self.other)
        self.assertTrue(set(ids) <= set(seen))
        status, page = call('GET', '/shared-answers?since=' + urllib.request.quote(cursor), install=self.other)
        self.assertEqual(page['answers'], [])  # nothing new since the last cursor

    def test_writes_are_limited_per_key(self):
        key = KEY_B  # the limit is 300 writes an hour per key (reset local D1 to rerun within the hour)
        status = 200
        for _ in range(8):
            batch = [{'id': new_id(), 'kind': 'answer', 'answer': 'Rate limited answer.'} for _ in range(50)]
            status, body = call('POST', '/shared-answers', {'answers': batch}, key=key, install=secrets.token_hex(24))
            if status != 200:
                break
        self.assertEqual(status, 429, body)


if __name__ == '__main__':
    unittest.main()

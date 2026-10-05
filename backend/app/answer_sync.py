"""Online sync of researcher-approved answers: off by default, and only answers ever leave this computer.

Each researcher's lessons stay in this computer's data folder (agent_learning.py). With sync on, the answers a researcher
approved or corrected AND marked for sharing are sent to the NDIM sync service, after a privacy check; answers other
researchers shared come back into a separate local file that recall() uses below the researcher's own lessons.

What is sent for each answer: a random id, whether it was approved or corrected, and the answer text. Never the
question, the field notes or any evidence, workspace data, or names. An answer is held back if it repeats words of the
evidence, names a person or place from the field notes or the workspace, or contains an email address, a phone or ID
number, a link or a social media handle. Held-back answers are shown with the reason, so the researcher sees exactly
what will and will not be shared.

Withdrawing works through the ledger of sent answers: an answer that was sent but is no longer shareable (unticked,
forgotten, or now failing the check) is deleted from the service at the next sync, and other researchers' copies are
removed when they next pull. Sync runs only in the desktop (local) engine and only while the researcher has it on.
"""
import hashlib
import json
import os
import re
import secrets
import threading
import unicodedata

import httpx
from fastapi import HTTPException

from . import agent_learning as learning
from . import engine_store as store
from .storage import app_paths

DEFAULT_URL = 'https://ndim-engine.couma.workers.dev'
USER_AGENT = 'NDIM-engine answer-sync/1'  # Cloudflare's bot check refuses default script user agents
QUOTE_WORDS = 6  # stricter than the 8 words used locally: six consecutive words of the evidence hold an answer back
MAX_ANSWER = 4000
BATCH = 50
_lock = threading.Lock()

HIDDEN = re.compile('[­᠎​-‏‪-‮⁠-⁤⁦-⁩﻿]')
EMAIL = re.compile(r'[\w.+-]+\s*(?:@|\(at\)|\[at\])\s*[\w-]+(?:\s*(?:\.|\(dot\)|\[dot\])\s*[\w-]+)+', re.I)
NUMBER = re.compile(r'\+?\d(?:[\s\-()/]{0,2}\d){6,}')  # seven or more digits, spaced or not; 0.876 and 2026 pass
CODE = re.compile(r'\b(?=[a-z0-9]*\d)(?=[a-z0-9]*[a-z])[a-z0-9]{6,}\b', re.I)  # letters mixed with digits, e.g. RW12345
LINK = re.compile(r'(?:https?://|www\.)\S+', re.I)
HANDLE = re.compile(r'(?<![\w.])@\w{2,}')
DATES = re.compile(r'\b(?:19|20)\d\d(?:\s*[-/]\s*\d\d?){2}\b|\b(?:19|20)\d\d\s*[-/]\s*(?:19|20)\d\d\b')  # 2026-10-05, 2020-2026
SENTENCE_END = re.compile(r'[.!?:;\n"“”]\s*$')
# Capitalised words that are not personal: they may appear in an answer even when the field notes use them.
COMMON = set('''rwanda rwandan rwandans kigali kinyarwanda english french swahili africa african east ndim engine
monday tuesday wednesday thursday friday saturday sunday january february march april may june july august september
october november december community health worker workers chw chws government ministry district province sector cell
village umudugudu northern southern eastern western city the and but our they their we you this that these those then
there when what which who how why yes not also some many most several families households people women men'''.split())


# ---------------------------------------------------------------- privacy check
def _plain(text):
    """Case-folded text without accents or hidden characters, so 'Café', 'cafe' and 'ca​fe' compare equal."""
    text = HIDDEN.sub('', unicodedata.normalize('NFKD', text or ''))
    return ''.join(c for c in text if not unicodedata.combining(c)).casefold()


def _words(text):
    return re.findall(r'\w+', _plain(text))


def _quotes(answer, sources, n=QUOTE_WORDS):
    tokens = _words(answer)
    grams = {' '.join(tokens[i:i + n]) for i in range(len(tokens) - n + 1)}
    if not grams:
        return False
    for source in sources:
        words = _words(source)
        if grams & {' '.join(words[i:i + n]) for i in range(len(words) - n + 1)}:
            return True
    return False


def evidence_names(texts):
    """Words written with a capital inside a sentence of the field notes: likely names of people or places."""
    names = set()
    for text in texts:
        for match in re.finditer(r'\b[^\W\d_][\w\'-]{2,}', text or ''):
            word = match.group()
            if word[0].isupper() and not SENTENCE_END.search(text[:match.start()] or '.'):
                names.add(word)
    return {name for name in names if _plain(name) not in COMMON}


def check(answer, evidence_texts=(), names=()):
    """Reasons to keep this answer on this computer; an empty list means it may be shared."""
    reasons = []
    answer = answer or ''
    if not 2 <= len(answer.strip()) <= MAX_ANSWER:
        reasons.append(f'It is empty or longer than {MAX_ANSWER} characters.')
    if HIDDEN.search(answer):
        reasons.append('It contains hidden characters.')
    if _quotes(answer, [t for t in evidence_texts if t]):
        reasons.append('It repeats words from the field notes.')
    said = set(_words(answer))
    found = sorted({name for name in set(names) | evidence_names(evidence_texts)
                    if name and set(_words(name)) and set(_words(name)) <= said and _plain(name) not in COMMON})
    if found:
        reasons.append('It names a person or place from the field notes or workspace (' + ', '.join(found[:5]) + ').')
    plain = _plain(answer)
    if EMAIL.search(plain):
        reasons.append('It contains an email address.')
    if NUMBER.search(DATES.sub(' ', plain)):
        reasons.append('It contains a phone or ID number.')
    elif CODE.search(DATES.sub(' ', plain)):
        reasons.append('It contains a code that looks like an ID.')
    if LINK.search(plain):
        reasons.append('It contains a link.')
    if HANDLE.search(plain):
        reasons.append('It contains a social media handle.')
    return reasons


# ---------------------------------------------------------------- settings and local stores
def _folder():
    return app_paths()['data'] / 'learning'


def _read(name, default):
    try:
        return json.loads((_folder() / name).read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return default


def settings():
    data = _read('sync.json', {})
    data.setdefault('enabled', False)
    data.setdefault('url', '')
    data.setdefault('token', '')
    data.setdefault('sent', {})
    data.setdefault('cursor', '')
    data.setdefault('last_sync', None)
    if not data.get('install_id'):
        # A random secret that marks this computer's answers as its own, so only it can withdraw them. Not a name.
        data['install_id'] = secrets.token_hex(24)
        store.atomic_write(_folder() / 'sync.json', data)
    return data


def _save(data):
    store.atomic_write(_folder() / 'sync.json', data)


def _url(data):
    return (data.get('url') or os.getenv('NDIM_SYNC_URL') or DEFAULT_URL).rstrip('/')


def _token(data):
    return data.get('token') or os.getenv('NDIM_SYNC_TOKEN', '')


def enabled():
    """On only when the researcher turned it on, and only in the desktop (local) engine, never the public demo."""
    return os.getenv('NDIM_DEPLOYMENT_MODE', 'local') == 'local' and bool(settings()['enabled'])


def configure(enabled_=None, url=None, token=None):
    data = settings()
    if url is not None:
        if url and not re.match(r'^https?://[\w.-]+(:\d+)?(/[\w./-]*)?$', url):
            raise HTTPException(422, 'The sync address must be a web address (https://…).')
        data['url'] = url
    if token is not None:
        data['token'] = token
    if enabled_ is not None:
        if enabled_ and not _token(data):
            raise HTTPException(422, 'Online sync needs the access key your research team was given.')
        data['enabled'] = bool(enabled_)
    _save(data)
    return data


def others():
    return _read('shared-answers.json', {'answers': []})['answers']


def matches(message, limit=2):
    """Other researchers' shared answers that share at least three words with the question (they carry no question)."""
    if not enabled():
        return []
    asked = set(learning.words(message)) - learning.STOP
    scored = [(len(asked & set(learning.words(item['answer']))), item['updated_at'], item) for item in others()]
    return [item for overlap, _, item in sorted(scored, key=lambda row: (row[0], row[1]), reverse=True) if overlap >= 3][:limit]


# ---------------------------------------------------------------- what will be shared
def _digest(answer):
    return hashlib.sha256(answer.encode('utf-8')).hexdigest()


def outbox(evidence_for):
    """Every answer marked for sharing, with what happens to it: shared already, will be shared, or held back (why).

    evidence_for(lesson) gives (evidence texts, names) for the lesson's chat, or None when the chat is gone and the
    answer can no longer be checked; such answers are held back.
    """
    data = settings()
    rows = []
    for lesson in learning.load()['lessons']:
        if not lesson.get('share') or lesson['kind'] not in ('answer', 'correction'):
            continue
        material = evidence_for(lesson)
        reasons = (['Its chat was deleted, so it can no longer be checked against the field notes.'] if material is None
                   else check(lesson['answer'], *material))
        sent = data['sent'].get(lesson['id']) == _digest(lesson['answer'])
        rows.append({'id': lesson['id'], 'kind': lesson['kind'], 'answer': lesson['answer'], 'reasons': reasons,
                     'status': 'held back' if reasons else 'shared' if sent else 'will share'})
    shareable = {row['id'] for row in rows if not row['reasons']}
    withdraw = [lesson_id for lesson_id in data['sent'] if lesson_id not in shareable]
    return rows, withdraw


def status(evidence_for):
    data = settings()
    rows, withdraw = outbox(evidence_for)
    return {'enabled': data['enabled'], 'url': _url(data), 'has_token': bool(_token(data)), 'last_sync': data['last_sync'],
            'outbox': rows, 'withdraw': len(withdraw), 'others': len(others())}


# ---------------------------------------------------------------- talking to the sync service
def _client(data):
    return httpx.Client(base_url=_url(data), timeout=httpx.Timeout(20, connect=10),
                        headers={'Authorization': f'Bearer {_token(data)}', 'X-NDIM-Install': data['install_id'],
                                 'User-Agent': USER_AGENT, 'Content-Type': 'application/json'})


def _fail(response):
    try:
        detail = response.json().get('error') or response.text
    except ValueError:
        detail = response.text
    raise RuntimeError(f'The sync service answered {response.status_code}: {str(detail)[:200]}')


def sync(evidence_for):
    """Send new shareable answers, withdraw ones no longer shared, and pull other researchers' answers."""
    with _lock:
        if not enabled():
            raise HTTPException(409, 'Online sync is off.')
        data = settings()
        rows, withdraw = outbox(evidence_for)
        send = [row for row in rows if row['status'] == 'will share']
        result = {'at': store.now(), 'sent': 0, 'withdrawn': 0, 'pulled': 0, 'error': None}
        try:
            with _client(data) as client:
                for lesson_id in withdraw:
                    response = client.delete(f'/shared-answers/{lesson_id}')
                    if response.status_code not in (200, 204, 404):
                        _fail(response)
                    data['sent'].pop(lesson_id, None)
                    result['withdrawn'] += 1
                for start in range(0, len(send), BATCH):
                    chunk = send[start:start + BATCH]
                    payload = {'answers': [{'id': row['id'], 'kind': row['kind'], 'answer': row['answer']} for row in chunk]}
                    response = client.post('/shared-answers', json=payload)
                    if response.status_code != 200:
                        _fail(response)
                    for row in chunk:
                        data['sent'][row['id']] = _digest(row['answer'])
                    result['sent'] += len(chunk)
                result['pulled'] = _pull(client, data)
        except (httpx.HTTPError, RuntimeError) as error:
            result['error'] = str(error) if isinstance(error, RuntimeError) else 'The sync service could not be reached.'
        data['last_sync'] = result
        _save(data)
        return result


def _pull(client, data):
    """Other researchers' answers since the last pull; tombstones remove withdrawn ones from the local copy."""
    answers = {item['id']: item for item in others()}
    own = set(data['sent'])
    changed = 0
    for _ in range(20):
        response = client.get('/shared-answers', params={'since': data['cursor']})
        if response.status_code != 200:
            _fail(response)
        page = response.json()
        for item in page.get('answers', []):
            if item['id'] in own:
                continue
            if item.get('deleted'):
                changed += answers.pop(item['id'], None) is not None
            elif not check(item.get('answer', '')):  # the same check on the way in: nothing unsafe is kept
                answers[item['id']] = {'id': item['id'], 'kind': item.get('kind', 'answer'), 'answer': item['answer'],
                                       'updated_at': item['updated_at']}
                changed += 1
        data['cursor'] = page.get('cursor') or data['cursor']
        if not page.get('more'):
            break
    store.atomic_write(_folder() / 'shared-answers.json', {'answers': list(answers.values())})
    return changed


def sync_if_on(evidence_for):
    """Sync now if sync is on (used after the researcher shares, stops sharing or forgets an answer, so the list they
    see is what the service holds). A failure is recorded in last_sync, never raised."""
    if enabled():
        _quiet(evidence_for)


def sync_soon(evidence_for):
    """After a change, sync in the background if sync is on; a failure is shown in the Learning panel, never raised."""
    if not enabled():
        return
    threading.Thread(target=lambda: _quiet(evidence_for), daemon=True).start()


def _quiet(evidence_for):
    try:
        sync(evidence_for)
    except HTTPException:
        pass

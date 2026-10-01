"""What the research assistant learns from its researchers: lessons it recalls at once, and examples for fine-tuning.

The assistant learns only from what a researcher checked. A thumbs-up approves a reply as written; a correction replaces
it with the researcher's text; a thumbs-down alone is logged for evaluation and never learned from. A reply the engine
flagged (unverified numbers or claim words) cannot be approved as written, only corrected, so the model does not learn
its own inventions.

Everything stays in this computer's data folder. A researcher may mark an approved answer for sharing; with online sync
on, only answers are shared, with the engine's numbers as context, never the question or any evidence text. An answer
that quotes the evidence is kept local whatever the researcher ticked.
"""
import json
import re
from uuid import uuid4

from fastapi import HTTPException

from . import engine_store as store
from .storage import app_paths

WORD = re.compile(r"[a-z0-9']+")
QUOTE_WORDS = 8  # an answer sharing this many consecutive words with the evidence quotes it
STOP = set('a an and are as at be by for from has have how i in is it its might of on or that the their this to was what '
           'which will with would you your'.split())


def _file():
    return app_paths()['data'] / 'learning' / 'lessons.json'


def load():
    try:
        return json.loads(_file().read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return {'lessons': [], 'terms': []}


def save(data):
    store.atomic_write(_file(), data)


def words(text):
    return WORD.findall((text or '').lower())


def quotes(answer, sources):
    """True if the answer repeats QUOTE_WORDS or more consecutive words of any source text."""
    tokens = words(answer)
    grams = {' '.join(tokens[i:i + QUOTE_WORDS]) for i in range(len(tokens) - QUOTE_WORDS + 1)}
    return any(gram in ' '.join(words(source)) for source in sources for gram in grams) if grams else False


def _question_for(thread, index):
    """The researcher's last typed message before the reply (app notes are context, not questions)."""
    for message in reversed(thread['messages'][:index]):
        if message['role'] == 'user' and not message.get('hidden'):
            return message['content']
    return ''


def record_feedback(thread, message_id, rating, correction, share, context, evidence_texts):
    index = next((i for i, m in enumerate(thread['messages']) if m['id'] == message_id and m['role'] == 'assistant'), None)
    if index is None:
        raise HTTPException(404, 'Reply not found in this chat')
    reply = thread['messages'][index]
    if not (reply.get('content') or '').strip():
        raise HTTPException(422, 'Only replies with text can be rated.')
    correction = (correction or '').strip()
    if rating == 'up' and reply.get('check') and not correction:
        raise HTTPException(422, 'This reply has a warning (numbers the engine did not produce or unsupported claims), so it '
                                 'cannot be approved as written. Correct it instead.')
    kind = 'correction' if correction else 'answer' if rating == 'up' else 'flagged'
    answer = correction or reply['content']
    lesson = {'id': uuid4().hex, 'kind': kind, 'question': _question_for(thread, index), 'answer': answer,
              'original': reply['content'] if correction else None, 'workspace_id': thread['workspace_id'],
              'thread_id': thread['thread_id'], 'message_id': message_id, 'context': context,
              'created_at': store.now(), 'shared_at': None}
    lesson['share'] = bool(share) and kind != 'flagged'
    if lesson['share'] and quotes(answer, evidence_texts):
        lesson['share'] = False
        lesson['share_blocked'] = 'The answer quotes the evidence, so it stays on this computer.'
    data = load()
    data['lessons'] = [item for item in data['lessons'] if item['message_id'] != message_id] + [lesson]
    save(data)
    reply['feedback'] = {'rating': rating, 'lesson_id': lesson['id'], 'kind': kind, 'share': lesson['share']}
    return lesson


def add_term(term, meaning, workspace_id=None):
    data = load()
    entry = {'id': uuid4().hex, 'term': term.strip(), 'meaning': meaning.strip(), 'workspace_id': workspace_id, 'created_at': store.now()}
    data['terms'] = [t for t in data['terms'] if t['term'].lower() != entry['term'].lower() or t['workspace_id'] != workspace_id] + [entry]
    save(data)
    return entry


def forget(item_id):
    data = load()
    before = len(data['lessons']) + len(data['terms'])
    data['lessons'] = [item for item in data['lessons'] if item['id'] != item_id]
    data['terms'] = [item for item in data['terms'] if item['id'] != item_id]
    if len(data['lessons']) + len(data['terms']) == before:
        raise HTTPException(404, 'Nothing with that id')
    save(data)


def recall(message, workspace_id, limit=3):
    """Prompt lines with the team's terms and the approved answers to the most similar earlier questions."""
    data = load()
    terms = [t for t in data['terms'] if t['workspace_id'] in (None, workspace_id)][-30:]
    asked = set(words(message)) - STOP
    scored = []
    for lesson in data['lessons']:
        if lesson['kind'] == 'flagged':
            continue
        overlap = len(asked & (set(words(lesson['question'])) - STOP))
        if overlap >= 2:
            scored.append((overlap + (0.5 if lesson['workspace_id'] == workspace_id else 0), lesson['created_at'], lesson))
    best = [lesson for *_, lesson in sorted(scored, key=lambda row: (row[0], row[1]), reverse=True)[:limit]]
    lines = []
    if terms:
        lines += ['Terms your research team uses: ' + '; '.join(f"{t['term']} = {t['meaning']}" for t in terms) + '.']
    if best:
        lines.append('Answers your research team approved or corrected for similar questions. Follow their wording and '
                     'care; for numbers, the engine\'s current results always take precedence over these:')
        lines += [f"- Asked: {lesson['question'][:300]}\n  Approved answer: {lesson['answer'][:800]}" for lesson in best]
    return lines


def dataset(shared_only=False, system='You are NDIM, a careful research assistant.'):
    """Fine-tuning examples in chat format. Shared examples carry only the answer and the engine's numbers."""
    rows = []
    for lesson in load()['lessons']:
        if lesson['kind'] == 'flagged' or (shared_only and not lesson['share']):
            continue
        context = json.dumps(lesson['context'], ensure_ascii=False) if lesson.get('context') else ''
        prompt = (f'Engine facts: {context}\n' if context else '') + ('Explain this to the researcher.' if shared_only
                                                                      else lesson['question'])
        rows.append({'messages': [{'role': 'system', 'content': system}, {'role': 'user', 'content': prompt},
                                  {'role': 'assistant', 'content': lesson['answer']}],
                     'kind': lesson['kind'], 'id': lesson['id']})
    return rows


def summary(ready_at=300):
    data = load()
    counts = {kind: sum(1 for item in data['lessons'] if item['kind'] == kind) for kind in ('answer', 'correction', 'flagged')}
    usable = counts['answer'] + counts['correction']
    return {'lessons': counts, 'terms': len(data['terms']), 'usable_examples': usable,
            'shareable_answers': sum(1 for item in data['lessons'] if item.get('share')),
            'fine_tune_ready_at': ready_at, 'fine_tune_ready': usable >= ready_at}

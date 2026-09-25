"""Field manual and reference curriculum as searchable sections for the chat agent and its Library panel."""
import functools
import html
import math
import re
from collections import Counter

from .workflow_ui import ACADEMY_HTML, MANUAL_HTML

SOURCES = {'manual': ('Field manual', MANUAL_HTML), 'curriculum': ('Reference curriculum', ACADEMY_HTML)}
HEADING = re.compile(r'<(h[1-3])\b[^>]*>(.*?)</\1>', re.S | re.I)
BLOCK = re.compile(r'</?(p|div|li|ul|ol|tr|table|section|article|br|h[1-6]|pre|blockquote)\b[^>]*>', re.I)
WORD = re.compile(r"[a-z0-9]+(?:'[a-z]+)?")
STOP = frozenset('the a an and or of to in on for with is are be by as at it this that from how what why when which can not'.split())


def _text(fragment):
    """Readable plain text: block tags become line breaks, scripts and styles are dropped."""
    fragment = re.sub(r'<(script|style|svg|button|nav)\b.*?</\1>', ' ', fragment, flags=re.S | re.I)
    fragment = re.sub(r'<li\b[^>]*>', '\n• ', fragment, flags=re.I)
    fragment = BLOCK.sub('\n', fragment)
    fragment = html.unescape(re.sub(r'<[^>]+>', ' ', fragment))
    lines = [re.sub(r'[ \t ]+', ' ', line).strip() for line in fragment.split('\n')]
    # Display-math wrappers from the MathJax source read as noise in plain text; keep the equations themselves.
    lines = [re.sub(r'\s*\\\\$', '', line).replace('&=', '=') for line in lines if not re.fullmatch(r'\\(begin|end)\{[a-z*]+\}', line)]
    text = '\n'.join(line for line in lines if line and '${' not in line)
    return re.sub(r'\n{3,}', '\n\n', text).strip()


def _slug(value):
    return re.sub(r'[^a-z0-9]+', '-', value.lower()).strip('-')[:60] or 'section'


@functools.lru_cache(maxsize=1)
def sections():
    """Split each document at h1-h3 headings. Ids are stable while headings stay the same."""
    out = []
    for source, (label, document) in SOURCES.items():
        body = re.sub(r'<(script|style)\b.*?</\1>', ' ', document, flags=re.S | re.I)
        marks = list(HEADING.finditer(body))
        seen = Counter()
        for index, mark in enumerate(marks):
            title = _text(mark.group(2))
            if not title or '${' in title:
                continue
            end = marks[index + 1].start() if index + 1 < len(marks) else len(body)
            text = _text(body[mark.end():end])
            if len(text) < 40:
                continue
            slug = _slug(title)
            seen[slug] += 1
            section_id = f'{source}:{slug}' + (f'-{seen[slug]}' if seen[slug] > 1 else '')
            out.append({'id': section_id, 'source': source, 'source_label': label, 'title': title, 'text': text})
    return out


def _terms(text):
    return [word for word in WORD.findall(text.lower()) if word not in STOP and len(word) > 1]


@functools.lru_cache(maxsize=1)
def _index():
    docs = [Counter(_terms(item['title'] + ' ' + item['title'] + ' ' + item['text'])) for item in sections()]
    frequency = Counter(term for doc in docs for term in doc)
    lengths = [sum(doc.values()) for doc in docs]
    return docs, frequency, (sum(lengths) / len(lengths)) if lengths else 1, lengths


def search(query, source='all', limit=5):
    """BM25 ranking over sections; returns ids, titles and a short snippet around the best match."""
    docs, frequency, average, lengths = _index()
    terms = _terms(query)
    total = len(docs)
    scored = []
    for position, item in enumerate(sections()):
        if source != 'all' and item['source'] != source:
            continue
        score = 0.0
        for term in terms:
            count = docs[position].get(term, 0)
            if not count:
                continue
            idf = math.log(1 + (total - frequency[term] + .5) / (frequency[term] + .5))
            score += idf * count * 2.2 / (count + 1.2 * (.25 + .75 * lengths[position] / average))
        if score > 0:
            scored.append((score, item))
    scored.sort(key=lambda pair: -pair[0])
    return [{'id': item['id'], 'source': item['source_label'], 'title': item['title'], 'snippet': _snippet(item['text'], terms)}
            for _, item in scored[:limit]]


def _snippet(text, terms, width=260):
    lowered = text.lower()
    hits = [lowered.find(term) for term in terms if lowered.find(term) >= 0]
    start = max(0, min(hits) - 60) if hits else 0
    piece = text[start:start + width].replace('\n', ' ')
    return ('…' if start else '') + piece + ('…' if start + width < len(text) else '')


def read(section_id, limit=8000):
    item = next((entry for entry in sections() if entry['id'] == section_id), None)
    if not item:
        return None
    text = item['text']
    return item | {'text': text[:limit], 'truncated': len(text) > limit}


def table_of_contents():
    return [{'id': item['id'], 'source': item['source'], 'source_label': item['source_label'], 'title': item['title']} for item in sections()]

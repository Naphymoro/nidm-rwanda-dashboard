"""Keep the data folder through restarts on hosts whose disk is thrown away (Cloudflare Containers).

The engine keeps working with files, as on the desktop. When NDIM_MIRROR_TOKEN is set, the host keeps a copy of the
folder and talks to the engine through three internal routes (main.py, /__mirror/*), each requiring that token:

- restore: when the container starts, the host sends the saved files in batches, then `done`. Until then the engine
  answers other requests with 503. Once restored, further restores are refused, so a host that lost track (its Worker
  restarted while the container ran) can never write an older copy over newer work.
- changes: the host asks what changed since the last acknowledged copy (new and changed files, deleted keys).
- ack: the host confirms it saved those changes; only then are they marked as kept.

The Cloudflare Worker (cloudflare/engine-container/src/index.ts) keeps the copy in D1. A first design had the engine
push to a host reachable through the container's egress; on Cloudflare that host was never reached (HTTP 530), so
the host now pulls, over the same route visitors' requests take. Without NDIM_MIRROR_TOKEN nothing changes.
"""
import base64
import hmac
import logging
import os
import threading
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException

from .storage import app_paths

log = logging.getLogger(__name__)
SKIP_DIRS = {'exports', 'backups', 'support', 'logs'}  # rebuilt on demand; not worth keeping
MAX_BYTES = 1_500_000  # D1 rows hold up to 2 MB
BATCH_BYTES = 4_000_000  # per changes reply; the host asks again while more is pending
_lock = threading.Lock()
_seen = {}  # key -> (mtime_ns, size) as last acknowledged by the host
_pending = {}  # changes id -> (put signatures, deleted keys)
_restored = set()  # keys the host sent back at startup: it already has them
ready = threading.Event()  # set once the folder is restored (or immediately when the mirror is off)
_state = {'status': 'off', 'restored': 0}


def enabled():
    return bool(os.getenv('NDIM_MIRROR_TOKEN'))


def status():
    return dict(_state) if enabled() else {'status': 'off'}


def start():
    """At startup: wait for the host's restore when the mirror is on; otherwise open at once."""
    if enabled():
        _state.update(status='waiting for restore', restored=0)
    else:
        ready.set()


def authorize(token):
    expected = os.getenv('NDIM_MIRROR_TOKEN', '')
    if not expected or not hmac.compare_digest(token or '', expected):
        raise HTTPException(404, 'Not Found')  # indistinguishable from a route that does not exist


def _root():
    return Path(app_paths()['data'])


def _files():
    """Every file worth keeping, as relative path -> (modified time, size)."""
    root, found = _root(), {}
    if not root.exists():
        return found
    for path in root.rglob('*'):
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        if rel.parts[0] in SKIP_DIRS or path.name.startswith('.pending-') or path.suffix == '.lock':
            continue
        stat = path.stat()
        found[rel.as_posix()] = (stat.st_mtime_ns, stat.st_size)
    return found


def restore_batch(files, done, then):
    """Write a batch of saved files (key -> base64); with done, open the engine. Refused once restored."""
    global _seen
    with _lock:
        if ready.is_set():
            raise HTTPException(409, 'Already restored; a second restore could overwrite newer work.')
        root = _root().resolve()
        for key, data in (files or {}).items():
            target = (root / key).resolve()
            if root not in target.parents:  # never write outside the data folder
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(base64.b64decode(data))
            _restored.add(key)
            _state['restored'] += 1
        if done:
            then()  # e.g. default workspaces: only after the saved ones are back
            current = _files()
            _seen = {key: current[key] for key in _restored if key in current}  # anything else is new: the host pulls it
            _state['status'] = 'on'
            ready.set()
            log.info('Restored %d file(s) from the host', _state['restored'])
    return status()


def changes():
    """New and changed files (base64) and deleted keys since the last acknowledged copy, in one batch."""
    with _lock:
        if not ready.is_set():
            return {'id': None, 'put': {}, 'delete': [], 'more': False}
        current = _files()
        put, signatures, size, more = {}, {}, 0, False
        for key, signature in current.items():
            if _seen.get(key) == signature:
                continue
            if signature[1] > MAX_BYTES:
                log.warning('Not kept (larger than %d bytes): %s', MAX_BYTES, key)
                continue
            if size + signature[1] > BATCH_BYTES and put:
                more = True
                continue
            put[key] = base64.b64encode((_root() / key).read_bytes()).decode()
            signatures[key] = signature
            size += signature[1]
        deleted = sorted(set(_seen) - set(current))
        change_id = uuid4().hex
        _pending[change_id] = (signatures, deleted)
        return {'id': change_id, 'put': put, 'delete': deleted, 'more': more}


def ack(change_id):
    """The host saved a batch: mark it as kept, so it is not sent again."""
    with _lock:
        signatures, deleted = _pending.pop(change_id, (None, None))
        if signatures is None:
            raise HTTPException(404, 'Unknown change id')
        _seen.update(signatures)
        for key in deleted:
            _seen.pop(key, None)
        _pending.clear()  # older batches are superseded by this acknowledgement
    return {'kept': len(signatures), 'removed': len(deleted)}

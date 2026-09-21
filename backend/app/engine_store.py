"""Atomic run checkpoints under workspace evidence, included in full backups."""
import json
import logging
import os
import tempfile
from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException
from .research_store import run_folder


def now():
    return datetime.now(timezone.utc).isoformat()


def folder(workspace):
    return run_folder(workspace).parent / 'engine-runs'


def path(workspace, run_id):
    try:
        if str(UUID(run_id)) != run_id:
            raise ValueError()
    except ValueError:
        raise HTTPException(404, 'Experiment not found')
    return folder(workspace) / (run_id + '.json')


def atomic_write(target, data):
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix='.pending-', dir=target.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as handle:
            json.dump(data, handle, ensure_ascii=False, allow_nan=False)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, target)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def save(run):
    run['updated_at'] = now()
    atomic_write(path(run['workspace_id'], run['run_id']), run)


def load(workspace, run_id):
    try:
        run = json.loads(path(workspace, run_id).read_text(encoding='utf-8'))
    except FileNotFoundError:
        raise HTTPException(404, 'Experiment not found')
    except (ValueError, OSError):
        raise HTTPException(500, 'Experiment checkpoint could not be read')
    run['workspace_id'] = workspace
    return run


def listing(workspace):
    rows = []
    for file in folder(workspace).glob('*.json'):
        try:
            run = load(workspace, file.stem)
        except HTTPException:
            logging.getLogger(__name__).warning('Unreadable experiment checkpoint: %s', file.name)
            continue
        rows.append({k: run[k] for k in ('run_id', 'status', 'created_at', 'updated_at', 'title', 'skill', 'lesson_id')} | {'reviewed': bool(run.get('review')), 'lesson_passed': bool(run.get('lesson_check', {}).get('correct'))})
    return sorted(rows, key=lambda item: (item['created_at'], item['run_id']), reverse=True)


def event(run, kind, message, **extra):
    run['events'].append({'sequence': len(run['events']) + 1, 'at': now(), 'type': kind, 'message': message, **extra})

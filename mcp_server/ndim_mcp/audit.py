"""Append-only record of approval-gated actions taken through this server."""
import json
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


def record(settings, tool, **fields):
    """Best effort: an unwritable log must never block scientific work, but it is reported."""
    entry = {'at': datetime.now(timezone.utc).isoformat(), 'tool': tool, **fields}
    logger.info('audit %s', json.dumps(entry, ensure_ascii=False))
    if settings.audit_log is None:
        return
    try:
        settings.audit_log.parent.mkdir(parents=True, exist_ok=True)
        with settings.audit_log.open('a', encoding='utf-8') as handle:
            handle.write(json.dumps(entry, ensure_ascii=False) + '\n')
    except OSError as exc:
        logger.warning('Could not write audit log %s: %s', settings.audit_log, exc)

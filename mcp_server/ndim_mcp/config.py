"""Runtime settings, read once from the environment."""
import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    engine_url: str = 'http://127.0.0.1:8010'
    bearer_token: str | None = None
    timeout: float = 30.0
    audit_log: Path | None = None
    max_wait_seconds: int = 120
    retry_attempts: int = 5
    retry_base_delay: float = 1.0

    @classmethod
    def from_env(cls, env=None):
        env = os.environ if env is None else env
        audit = env.get('NDIM_MCP_AUDIT_LOG', '').strip()
        if audit.lower() in {'off', 'none', '0', 'false'}:
            audit_path = None
        elif audit:
            audit_path = Path(audit).expanduser()
        else:
            audit_path = Path.home() / '.ndim-mcp' / 'audit.jsonl'
        return cls(
            engine_url=env.get('NDIM_ENGINE_URL', cls.engine_url).rstrip('/'),
            bearer_token=env.get('NDIM_ENGINE_BEARER_TOKEN') or None,
            timeout=float(env.get('NDIM_ENGINE_TIMEOUT', cls.timeout)),
            audit_log=audit_path,
            max_wait_seconds=int(env.get('NDIM_MCP_MAX_WAIT_SECONDS', cls.max_wait_seconds)),
        )

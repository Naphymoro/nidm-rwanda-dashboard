"""Thin async client for the NDIM engine HTTP API with agent-readable errors."""
import asyncio
import re

import httpx

WORKSPACE_RE = re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*$')
RUN_RE = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')


class EngineError(Exception):
    """An error the calling agent can act on; never contains a stack trace."""

    def __init__(self, message, status=None):
        super().__init__(message)
        self.status = status


def check_ids(workspace_id, run_id=None):
    """IDs become URL path segments, so reject anything that is not a plain slug or UUID."""
    if not WORKSPACE_RE.fullmatch(workspace_id) or len(workspace_id) > 160:
        raise EngineError(f'Invalid workspace_id {workspace_id!r}: use the lowercase slug from ndim_list_workspaces.')
    if run_id is not None and not RUN_RE.fullmatch(run_id):
        raise EngineError(f'Invalid run_id {run_id!r}: expected the UUID returned by ndim_plan_experiment.')


def _detail(response):
    try:
        body = response.json()
    except ValueError:
        return response.text[:300] or response.reason_phrase
    detail = body.get('detail', body) if isinstance(body, dict) else body
    if isinstance(detail, list):
        return '; '.join(f"{'.'.join(str(p) for p in item.get('loc', []) if p != 'body')}: {item.get('msg')}"
                         if isinstance(item, dict) else str(item) for item in detail)
    return detail if isinstance(detail, str) else str(detail)[:300]


class EngineClient:
    def __init__(self, settings, transport=None):
        self.settings = settings
        headers = {'Accept': 'application/json'}
        if settings.bearer_token:
            headers['Authorization'] = f'Bearer {settings.bearer_token}'
        self._http = httpx.AsyncClient(base_url=settings.engine_url, timeout=settings.timeout,
                                       headers=headers, transport=transport)

    async def aclose(self):
        await self._http.aclose()

    async def request(self, method, path, *, json=None, params=None, text=False, retry_busy=False):
        attempts = self.settings.retry_attempts if retry_busy else 1
        for attempt in range(attempts):
            try:
                response = await self._http.request(method, path, json=json, params=params)
            except httpx.ConnectError as exc:
                raise EngineError(f'Cannot reach the NDIM engine at {self.settings.engine_url}. '
                                  'Start it (uvicorn backend.app.main:app --port 8010) or set NDIM_ENGINE_URL.') from exc
            except httpx.TimeoutException as exc:
                raise EngineError(f'The NDIM engine did not answer within {self.settings.timeout:g}s.') from exc
            except httpx.HTTPError as exc:
                raise EngineError(f'Engine request failed: {type(exc).__name__}') from exc
            if response.status_code == 429 and attempt + 1 < attempts:
                # The engine rejects before changing state, so retrying a full queue is safe.
                await asyncio.sleep(self.settings.retry_base_delay * 2 ** attempt)
                continue
            if response.status_code >= 400:
                raise EngineError(f'Engine returned {response.status_code}: {_detail(response)}', response.status_code)
            if response.status_code == 204:
                return None
            return response.text if text else response.json()

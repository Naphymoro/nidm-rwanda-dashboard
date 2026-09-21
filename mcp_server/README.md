# ndim-mcp — NDIM engine as an MCP server

Lets an agent harness such as DeerFlow drive the NDIM scientific engine (`backend/app/engine_*.py`) without
touching its code. The engine stays the only thing that produces scientific results. This server is a typed,
guarded, agent-sized front door to its HTTP API.

The matching DeerFlow skill is `deer-flow/skills/public/ndim-engine/`. Read it for how agents should *use* these tools.

## Design

| Decision | Why |
|---|---|
| Calls the engine over HTTP, does not import it | The engine's SQLite single-owner lock, code fingerprint and checkpoints stay authoritative. Works against a local engine or Cloud Run. |
| Approval gate on start, resume and sweep | The engine's contract is "researcher approves the plan". `approval_statement` (>= 12 chars) must quote the researcher, and is written to an audit log. It is procedural, not cryptographic: it cannot prove a human said it. |
| No delete, review, workspace-edit or lesson-answer tools | Those are researcher decisions or destructive. They stay in the engine UI. |
| Summaries, not raw dumps | A run holds about 90 trajectory rows per simulation. Tools return statistics; `include_trajectories=true` opts in. Long free text is dropped. |
| Sweeps run server-side | The evidence text is sent once and reused verbatim, so all runs share one source hash. Comparison is computed here, not re-typed by an LLM. |
| `ndim_compare_runs` audits comparability | Flags different evidence, code versions, model families, or several factors varying at once. |
| IDs validated before becoming URL segments | Blocks `../` style path injection. |
| Engine 429 (queue full) is retried with backoff | Safe: the engine rejects before changing state. Only start/resume retry. |

## Tools (14)

Read: `ndim_engine_status`, `ndim_list_workspaces`, `ndim_list_lessons`, `ndim_list_runs`, `ndim_get_run`,
`ndim_wait_for_run`, `ndim_get_brief`, `ndim_compare_runs`.
Write, no approval: `ndim_plan_experiment`, `ndim_plan_sweep` (only create plans; nothing runs), `ndim_cancel_experiment`.
Write, approval required: `ndim_start_experiment`, `ndim_resume_experiment`, `ndim_run_sweep`.

## Run it

```bash
# needs the engine running:  uvicorn backend.app.main:app --port 8010 --workers 1
pip install -e mcp_server            # or reuse a venv that already has mcp>=1.2 and httpx (DeerFlow's does)
python -m ndim_mcp                   # stdio, what DeerFlow spawns
python -m ndim_mcp --transport streamable-http --port 8765   # http://127.0.0.1:8765/mcp
```

| Env var | Default | Meaning |
|---|---|---|
| `NDIM_ENGINE_URL` | `http://127.0.0.1:8010` | Engine base URL |
| `NDIM_ENGINE_BEARER_TOKEN` | unset | Sent as `Authorization: Bearer` (e.g. Cloud Run IAM identity token) |
| `NDIM_ENGINE_TIMEOUT` | `30` | Per-request seconds |
| `NDIM_MCP_MAX_WAIT_SECONDS` | `120` | Cap on any wait |
| `NDIM_MCP_AUDIT_LOG` | `~/.ndim-mcp/audit.jsonl` | JSONL of every approval-gated action; `off` disables |

## Wire into DeerFlow

`deer-flow/extensions_config.json` contains an `ndim-engine` entry, **disabled**, pointing at
`http://host.docker.internal:8766/mcp`, because DeerFlow's gateway here runs in Docker. Steps:

1. Start the engine: `uvicorn backend.app.main:app --port 8010 --workers 1` (from `nidm-rwanda-dashboard/`).
2. Start this server where the container can reach it. `host.docker.internal` resolves to `172.17.0.1` (docker0) inside the
   gateway, so bind there, not to the LAN:
   `python -m ndim_mcp --transport streamable-http --host 172.17.0.1 --port 8766`
3. Enable `ndim-engine` (DeerFlow MCP settings, or `"enabled": true`).

**Firewall caveat (found on this machine).** From inside `deer-flow-gateway`, connections to *any* host port timed out,
even a plain listener on `0.0.0.0`, while the host itself was fine. A host firewall is dropping container-to-host traffic.
Without root I could not change that, so steps 2-3 were **not** verified end to end from the container. To allow it, run as
root, for example: `ufw allow from 172.16.0.0/12 to any port 8766 proto tcp`, then re-test with
`docker exec -i deer-flow-gateway /app/backend/.venv/bin/python -c "import httpx;print(httpx.get('http://host.docker.internal:8766/mcp').status_code)"`
(any HTTP status, even 4xx, means it is reachable). The alternative that avoids the host firewall is running this server
and the engine as containers on the gateway's compose network (`deer-flow-dev_deer-flow-dev`) and using
`http://<service>:8766/mcp`. That is not built yet.

If DeerFlow runs directly on the host (not in Docker), use stdio instead. It reuses DeerFlow's own venv, and DeerFlow's MCP
config has no `cwd`, hence `PYTHONPATH`:

```json
"ndim-engine": {"enabled": true, "type": "stdio",
  "command": "<deer-flow>/backend/.venv/bin/python", "args": ["-m", "ndim_mcp"],
  "env": {"PYTHONPATH": "<repo>/nidm-rwanda-dashboard/mcp_server", "NDIM_ENGINE_URL": "http://127.0.0.1:8010"},
  "tool_name_prefix": false, "tool_call_timeout": 150}
```

**Security:** neither the engine nor this server authenticates callers ("workspace IDs are not authorization
boundaries"). Keep the HTTP transport on `127.0.0.1`, the docker0 address (`172.17.0.1`), or behind your own authenticating proxy, never `0.0.0.0`. Anyone who can reach
it can plan and run experiments.

## Tests

```bash
python -m pytest mcp_server          # offline: httpx.MockTransport stands in for the engine
```

Also verified by hand against a live engine: over real stdio, through DeerFlow's own `get_mcp_tools()` loader (stdio config,
run on the host), and over streamable-http from the host. Not verified: the container-to-host path (see the firewall caveat).

## Known limits

- The approval gate is procedural. Enforce it harder in DeerFlow (guardrails / human-in-the-loop on
  `ndim_start_experiment`, `ndim_resume_experiment`, `ndim_run_sweep`) if agents run unattended.
- One engine worker per data directory, worker_limit 1-2, queue of 8. Do not run several engines on one data dir.
- The audit log records what the agent claims the researcher said.
- Agents cannot pull raw trajectories into a DeerFlow sandbox file. Data reaches the agent as statistics or as text
  in a tool result. A future `ndim_export_run` could write to a directory the sandbox mounts.

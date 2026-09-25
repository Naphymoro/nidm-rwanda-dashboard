# NDIM research assistant

The Studio chat (`/`, or `/engine/` on the Pages site) is one tool: conversation, experiments, the Workbench and the
Library (field manual and reference curriculum) in a side panel. With an AI provider configured, NDIM answers in
plain language, searches the Library and plans experiments. Without one, the same chat plans experiments directly.

## What the assistant can and cannot do

- It plans experiments (`plan_experiment`), reads and compares results, lists runs and labs, and searches and reads
  the Library. Only the engine's deterministic tools produce scientific results.
- It cannot run experiments. The researcher's **Run** click is the approval. When a run the researcher started
  finishes, the chat asks the assistant to read and explain it.
- It cannot write review notes or raise consent. Evidence is passed to the model as data, never as instructions.
- Conversations are stored per workspace under `workspaces/<id>/evidence/agent-chats/`, next to the runs.

## Configure a provider

| Where | How |
|---|---|
| Desktop app or local backend | Chat settings (sliders icon) → Research assistant: pick a provider, paste a key, Save. The key is stored in the NDIM data folder (`agent-config.json`, owner-readable only). |
| Environment | `NDIM_AGENT_PROVIDER` (`anthropic`, `openai`, `openrouter`, `mistral`, `openai-compatible`, `ollama`, `lmstudio`), the provider's key (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, ...), optional `NDIM_AGENT_MODEL` and `NDIM_AGENT_BASE_URL`. Without `NDIM_AGENT_PROVIDER`, the first provider with a key is used (Anthropic, then OpenAI, OpenRouter, Mistral). |
| Docker (`mcp_server/docker-compose.deerflow.yml`) | Export the variables above, or put them in `mcp_server/.env` (gitignored), then `docker compose -f mcp_server/docker-compose.deerflow.yml up -d --no-build ndim-engine`. |
| Local models | `NDIM_AGENT_PROVIDER=ollama` (or `lmstudio`) and `NDIM_AGENT_MODEL`; no key. The model must support tool calling. |

Defaults: `claude-sonnet-5` for Anthropic, `gpt-4o` for OpenAI.

## Hosted deployments (Cloud Run)

The engine API has no user accounts, so a hosted assistant would let anyone spend the provider key. On
`NDIM_DEPLOYMENT_MODE=cloud` the assistant stays off until `NDIM_AGENT_ACCESS_TOKEN` is set. Every `/agent/*` call
must then send it in the `X-NDIM-Agent-Token` header; researchers enter it once in the chat settings. Keys on Cloud Run
come from environment variables or Secret Manager, never from the settings form.

## Checks

`python scripts/test_agent.py` drives the real tool loop, storage, library and access rules with a scripted model.

# NDIM engine on Cloudflare Containers

Runs the NDIM engine (`backend/Dockerfile`, unchanged) in a Cloudflare Container behind a small Worker, so the
Pages site can use it: `https://nidm-engine.pages.dev/engine/?api=<Worker URL>`.

Live (demo): https://ndim-engine.couma.workers.dev, so the public engine page is
https://nidm-engine.pages.dev/engine/?api=https://ndim-engine.couma.workers.dev

## Data survives restarts (D1 mirror)

The container's disk is discarded on every restart, sleep and deploy. The engine keeps working with files; the Worker
keeps a copy of the data folder in the D1 database `ndim-engine-data`:

- **At start** the Worker sends every saved file back into the new container before any visitor's request (the engine
  answers 503 until then and refuses a second restore, so an older copy never overwrites newer work).
- **After each changing request**, and again 15 s later for chat replies that stream, the Worker pulls the changed and
  deleted files into D1. A failed pull never fails the visitor's request; it is retried.
- The routes it uses (`/__mirror/*`, see `backend/app/durable_mirror.py`) need the `NDIM_MIRROR_TOKEN` secret, and the
  Worker refuses them from visitors.

Verified 2026-10-02: a journey and its chat survived a redeploy that replaced the container (47 files restored).
Not kept: files over 1.5 MB, and `exports/`, `backups/`, `support/`, `logs/`.

## Shared answers (opt-in online sync)

Researchers using the desktop engine can turn on online sync in Studio's Learning panel (off by default). Their engine
then sends the answers they approved or corrected and marked for sharing, and pulls answers other researchers shared
(`backend/app/answer_sync.py`). The Worker answers these routes itself from D1; the container is not involved:

- `GET /shared-answers?since=<cursor>`: answers and withdrawals since the cursor, without the caller's own.
- `POST /shared-answers` `{"answers": [{"id", "kind", "answer"}]}`: at most 50 a request, 4000 characters each,
  only those three fields (no question, evidence or name); emails and long numbers are refused.
- `DELETE /shared-answers/<id>`: withdraw; the text is erased and other engines drop their copy at their next pull.

Every request needs `Authorization: Bearer <key>` with a key from the `NDIM_SYNC_TOKENS` secret (comma-separated,
one per research team, so one can be revoked alone) and `X-NDIM-Install` (a random secret per computer: only the
computer that sent an answer can withdraw it). Without the secret the routes answer 503. The public demo engine has no
key and refuses to sync, so its visitors cannot write. Writes are limited to 300 an hour per key and 5000 live answers
per computer.

To turn it on (not done yet):

```bash
npx wrangler d1 migrations apply ndim-engine-data --remote   # creates the shared_answers table
python3 -c 'import secrets; print(secrets.token_urlsafe(32), end="")' | npx wrangler secret put NDIM_SYNC_TOKENS
npx wrangler deploy
```

Then give each research team its key; they paste it in the Learning panel. Tested locally only
(`scripts/test_answer_sync_worker.py` against `npx wrangler dev --enable-containers=false` with local D1).

## Research assistant (Workers AI)

The engine's research assistant runs on Workers AI through this Worker (`src/ai.ts`): no outside API key or company.
The engine calls `/__ai/v1/chat/completions` on the Worker's public URL with the `NDIM_AI_TOKEN` secret, as an
OpenAI-compatible provider; the Worker answers through the AI binding. The Worker picks the model (`NDIM_AI_MODEL`, GLM 5.3
Flash after the 2026-10-06 comparison), caps replies at 3,000 tokens (reasoning included), stops for the day at `NDIM_AI_DAILY_NEURONS` (9,000,
under the free 10,000) and allows `NDIM_AI_VISITOR_MESSAGES` (40) assistant messages per visitor per day (a visitor is a
hash of IP and day). Use is counted in D1 (`ai_usage`, `ai_visitors`). Without the secret there is no assistant.

```bash
npx wrangler d1 migrations apply ndim-engine-data --remote   # creates ai_usage and ai_visitors
python3 -c 'import secrets; print(secrets.token_urlsafe(32), end="")' | npx wrangler secret put NDIM_AI_TOKEN
npx wrangler deploy
```

Visitors can also use their own key (OpenRouter, OpenAI, Anthropic or DeepSeek) from AI settings: it stays in their
browser, is sent with each message, and the engine uses it for that reply only. Those messages are not counted.

## Requirements

- Cloudflare account on the **Workers Paid** plan (Containers are not on the free plan).
- Docker with the `buildx` plugin (`docker buildx version`); wrangler builds the image locally and pushes it.
- Node 20+.

## Deploy

```bash
cd cloudflare/engine-container
npm install
npx wrangler login              # opens a browser once
npx wrangler d1 create ndim-engine-data   # first time only; put its id in wrangler.toml
python3 -c 'import secrets; print(secrets.token_urlsafe(32), end="")' | npx wrangler secret put NDIM_MIRROR_TOKEN
npm run check                   # type check + dry run (builds the image, uploads nothing)
npx wrangler deploy             # builds, pushes the image, deploys the Worker; prints the Worker URL
```

The first request after a deploy or a sleep starts the container, which takes a while (the image is about 1.9 GB).

## Settings

- `NDIM_ALLOWED_ORIGINS` in `wrangler.toml`: sites allowed to call the engine (the Pages site by default).
- Secret `DATABASE_URL` (optional): `npx wrangler secret put DATABASE_URL`.
- `instance_type = "standard-1"` (1/2 vCPU, 4 GiB): PyTorch and Pyro need more memory than `basic`.
- `max_instances = 1`: the engine works on local files, so every user must reach the same instance.
- `sleepAfter = "30m"`: safe now that the data is kept.

## Bot check

Cloudflare's default bot protection answers some scripted clients with `error code: 1010` (403); Python's
`urllib` user agent is one. Browsers and curl pass. Scripts should send their own `User-Agent`. Headless browsers
(`HeadlessChrome`) are refused intermittently too, which shows as "Failed to fetch" in the page; a normal browser user
agent runs the full journey with no errors.

## Tested

Deployed 2026-10-01: the container started in about 20 seconds, a full 13-stage journey ran over HTTP (about a second
per stage), and CORS allows the Pages origin.

Before that, locally: `npx wrangler dev` runs the Worker and the container in local Docker; `/health`, `/workspaces`, CORS for the Pages
origin (and refusal for other origins), and starting a journey all worked through the Worker.

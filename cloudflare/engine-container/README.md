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

## Bot check and headless browsers

Automated tests with a headless browser saw intermittent "Failed to fetch": Cloudflare's bot protection answered some
requests from the `HeadlessChrome` user agent. With a normal browser user agent the full journey ran with no errors.

## Bot check

Cloudflare's default bot protection answers some scripted clients with `error code: 1010` (403); Python's
`urllib` user agent is one. Browsers and curl pass. Scripts should send their own `User-Agent`.

## Tested

Deployed 2026-10-01: the container started in about 20 seconds, a full 13-stage journey ran over HTTP (about a second
per stage), and CORS allows the Pages origin.

Before that, locally: `npx wrangler dev` runs the Worker and the container in local Docker; `/health`, `/workspaces`, CORS for the Pages
origin (and refusal for other origins), and starting a journey all worked through the Worker.

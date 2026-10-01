# NDIM engine on Cloudflare Containers

Runs the NDIM engine (`backend/Dockerfile`, unchanged) in a Cloudflare Container behind a small Worker, so the
Pages site can use it: `https://nidm-engine.pages.dev/engine/?api=<Worker URL>`.

Live (demo, see the warning below): https://ndim-engine.couma.workers.dev, so the public engine page is
https://nidm-engine.pages.dev/engine/?api=https://ndim-engine.couma.workers.dev

## Warning: data does not survive a restart yet

The engine keeps workspaces, journeys and run logs as files on the container's own disk. Cloudflare discards
that disk whenever the container stops: after 2 hours without requests (`sleepAfter`), on every deploy, and when
Cloudflare moves it. `DATABASE_URL` does not help, because the journeys and workspaces are files, not database rows.
Until storage is solved, treat this deployment as a demo and tell users to export their work.

## Requirements

- Cloudflare account on the **Workers Paid** plan (Containers are not on the free plan).
- Docker with the `buildx` plugin (`docker buildx version`); wrangler builds the image locally and pushes it.
- Node 20+.

## Deploy

```bash
cd cloudflare/engine-container
npm install
npx wrangler login              # opens a browser once
npm run check                   # type check + dry run (builds the image, uploads nothing)
npx wrangler deploy             # builds, pushes the image, deploys the Worker; prints the Worker URL
```

The first request after a deploy or a sleep starts the container, which takes a while (the image is about 1.9 GB).

## Settings

- `NDIM_ALLOWED_ORIGINS` in `wrangler.toml`: sites allowed to call the engine (the Pages site by default).
- Secret `DATABASE_URL` (optional): `npx wrangler secret put DATABASE_URL`.
- `instance_type = "standard-1"` (1/2 vCPU, 4 GiB): PyTorch and Pyro need more memory than `basic`.
- `max_instances = 1`: with files on local disk, every user must reach the same instance.

## Bot check

Cloudflare's default bot protection answers some scripted clients with `error code: 1010` (403); Python's
`urllib` user agent is one. Browsers and curl pass. Scripts should send their own `User-Agent`.

## Tested

Deployed 2026-10-01: the container started in about 20 seconds, a full 13-stage journey ran over HTTP (about a second
per stage), and CORS allows the Pages origin.

Before that, locally: `npx wrangler dev` runs the Worker and the container in local Docker; `/health`, `/workspaces`, CORS for the Pages
origin (and refusal for other origins), and starting a journey all worked through the Worker.

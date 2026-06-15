# NDIM Engine Cloudflare Pages Setup

This folder is the Cloudflare Pages entry point for the public alpha web presence.

It is intentionally separate from the local FastAPI desktop/runtime app. That lets
Cloudflare deploy a low-cost public site first, while the heavier Python modelling
stack remains available through the local app, Cloud Run, or Colab for advanced users.

## Cloudflare Pages settings

Use these settings in Cloudflare Pages:

```text
Project name: ndim-engine
Production branch: main
Framework preset: None
Build command: leave blank
Build output directory: cloudflare/public
Root directory: leave blank
```

After deployment, Cloudflare will provide a URL like:

```text
https://ndim-engine.pages.dev
```

## What this first Cloudflare edition does

- Gives testers and users a stable public entry point.
- Explains NDIM, the workflow, and the current alpha deployment modes.
- Links to manual, academy, publication, and deployment guidance pages.
- Avoids requiring users to install the desktop package before they understand the tool.

## What it does not do yet

This first Pages edition does not run the full Python/FastAPI backend. Cloudflare
Pages is static hosting. The full repository, modelling, uploads, approvals, and
exports need either:

- Cloudflare Workers + D1 + R2 for the lightweight web workflow, or
- Cloud Run / local desktop / Colab for the heavier Python scientific stack.

## Recommended next build step

Add a Worker API with:

```text
cloudflare/worker/
cloudflare/schema/
```

Then bind:

```text
D1 database: ndim-alpha-db
R2 bucket: ndim-alpha-files
```

## Cloudflare Worker backend

The first Worker backend scaffold now lives in:

```text
cloudflare/worker/
```

It provides:

- `GET /api/health`
- `GET /api/workspaces`
- `POST /api/workspaces`
- `GET /api/narratives`
- `POST /api/narratives`
- `GET /api/narratives/{id}`
- `POST /api/narratives/{id}/review`
- `POST /api/narratives/commit-reviewed`
- `POST /api/narratives/{id}/uncommit`
- `POST /api/narratives/{id}/encode`
- `POST /api/files/upload`
- `GET /api/repository/export`

Use this schema for D1:

```text
cloudflare/schema/schema.sql
```

After creating the D1 database in Cloudflare, update this file:

```text
cloudflare/worker/wrangler.toml
```

Replace:

```text
database_id = "replace-after-cloudflare-creates-d1"
```

with the real D1 database ID from Cloudflare.

The static backend test page is:

```text
cloudflare/public/backend-check.html
```

Open it after deploying the Worker and paste the Worker URL to check the API.

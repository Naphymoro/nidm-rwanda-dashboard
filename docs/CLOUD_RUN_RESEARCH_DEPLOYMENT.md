# NDIM Engine Lean Cloud Run Deployment

This is the recommended path for real users who should open NDIM in a browser instead of installing a local package.

The deployment model is:

```text
GitHub repository
  -> GitHub Actions
  -> Artifact Registry container image
  -> Google Cloud Run FastAPI service
  -> PostgreSQL database
  -> optional Google Sheets / Apps Script master repository sync
```

## Why this path

- Users get one stable web link.
- GitHub keeps version history and deploy automation.
- Cloud Run hosts the Python/FastAPI backend.
- PostgreSQL stores durable user/workspace/evidence data.
- Colab remains available for advanced users who want reproducible notebooks.
- The desktop/local edition remains available for offline or sensitive fieldwork.

## What Cloud Run should and should not do

Cloud Run should run:

- the NDIM FastAPI app,
- the integrated workflow UI,
- uploads and ingestion,
- deterministic/local encoding,
- digital twin and model APIs,
- manual and demo routes,
- policy export routes.

Cloud Run should not be treated as durable local storage. Its filesystem can be replaced at any time. For hosted users, set `DATABASE_URL` and use PostgreSQL.

Apps Script and Google Sheets should only be used for optional master repository sync, approval summaries, or institutional reporting. They should not run the modelling engine.

## Low-cost research settings

The GitHub workflow deploys with conservative defaults:

| Setting | Default | Why |
| --- | --- | --- |
| `min-instances` | `0` | Costs nothing when idle, but may cold-start. |
| `max-instances` | `2` | Prevents runaway scale during early deployment. |
| `concurrency` | `20` | Lets several users share one container. |
| `memory` | `2Gi` | Enough for routine NDIM use; increase if Torch/Pyro workloads fail. |
| `cpu` | `1` | Keeps compute cost controlled. |
| upload limit | `20 MB` | Prevents accidental large-file cost spikes. |

Add billing alerts in Google Cloud before inviting real users.

## Required Google setup

Create or choose a Google Cloud project, then enable:

- Cloud Run API
- Artifact Registry API
- IAM Credentials API
- Cloud Build API

Create a service account for GitHub deployment. Grant it:

- `roles/run.admin`
- `roles/artifactregistry.admin` or a narrower Artifact Registry writer role
- `roles/iam.serviceAccountUser`

Configure GitHub Workload Identity Federation for that service account. Store the resulting values in GitHub repository secrets:

| GitHub name | Type | Meaning |
| --- | --- | --- |
| `GCP_WORKLOAD_IDENTITY_PROVIDER` | secret | Workload Identity Provider resource name. |
| `GCP_SERVICE_ACCOUNT` | secret | Deployment service account email. |
| `DATABASE_URL` | secret | PostgreSQL URL, preferably `postgresql+psycopg://...`. |
| `GCP_PROJECT_ID` | variable | Google Cloud project ID. |
| `GCP_REGION` | variable | Cloud Run region, e.g. `us-central1`. |

Optional GitHub repository variables:

| Variable | Default |
| --- | --- |
| `CLOUD_RUN_SERVICE_NAME` | `ndim-engine-web` |
| `GCP_ARTIFACT_REPOSITORY` | `ndim-engine` |
| `CLOUD_RUN_MAX_INSTANCES` | `2` |
| `CLOUD_RUN_CONCURRENCY` | `20` |
| `CLOUD_RUN_MEMORY` | `2Gi` |
| `CLOUD_RUN_CPU` | `1` |
| `CLOUD_RUN_TIMEOUT` | `900` |
| `NDIM_MAX_UPLOAD_MB` | `20` |

## Database choices

For a Google-only institutional setup, use Cloud SQL for PostgreSQL.

For a lower-cost pilot, you may use any managed PostgreSQL provider and put its URL in `DATABASE_URL`. The app normalizes common `postgres://` and `postgresql://` URLs to the `psycopg` driver.

Do not use local SQLite for the hosted web app. SQLite remains for desktop/local mode.

## Deploy

After the secrets and variables are set:

1. Push to `main`, or
2. Run **Deploy NDIM Web to Cloud Run** manually from the GitHub Actions tab.

The workflow builds `backend/Dockerfile`, pushes the image to Artifact Registry, deploys Cloud Run, and prints the service URL.

## User-facing modes

Default users:

```text
Open NDIM Web -> choose/create workspace -> ingest -> encode -> model -> export policy brief
```

Advanced users:

```text
Open NDIM Colab -> mount Google Drive -> run reproducible notebook -> inspect equations/code
```

Offline/sensitive field users:

```text
Run NDIM Local -> SQLite local storage -> optional approved-record push later
```

## Security note

The first lean deployment is suitable for a controlled research pilot. Before public or sensitive-data use, add proper authentication, role-based access, and workspace permissions. Cloud Run can be placed behind an identity layer later, but the NDIM app itself should eventually own user roles such as researcher, reviewer, policy maker, and admin.

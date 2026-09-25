# NDIM Engine Lean Cloud Run Deployment

This is the recommended path for real users who should open NDIM in a browser instead of installing a local package.

The deployment model is:

```text
GitHub repository
  -> GitHub Actions
  -> Artifact Registry container image
  -> Google Cloud Run FastAPI service
  -> PostgreSQL database
  -> optional Google Drive + Google Sheets research repository
  -> optional Apps Script master repository sync
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

Google Drive, Google Sheets, and Apps Script should only be used for master repository storage, approval summaries, sync handoff, or institutional reporting. They should not run the modelling engine.

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

For a faster first deployment, you may use a service-account JSON key instead of Workload Identity Federation:

| GitHub name | Type | Meaning |
| --- | --- | --- |
| `GCP_SERVICE_ACCOUNT_KEY` | secret | Full JSON key for a tightly scoped deployment service account. |

Use Workload Identity Federation for production if possible. Use `GCP_SERVICE_ACCOUNT_KEY` only as a controlled bootstrap route, rotate it if it is exposed, and delete it when you move to Workload Identity.

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
| `NDIM_ALLOWED_ORIGINS` | `https://nidm-engine.pages.dev` |

`NDIM_ALLOWED_ORIGINS` lets the Cloudflare Pages engine UI call this service from the browser. The API has no authentication, so keep it to origins you control. The deploy step passes it through `gcloud --set-env-vars`, so set a single origin here; a comma-separated list needs a custom gcloud delimiter.

## Database choices

For a Google-only institutional setup, use Cloud SQL for PostgreSQL.

For a lower-cost pilot, you may use any managed PostgreSQL provider and put its URL in `DATABASE_URL`. The app normalizes common `postgres://` and `postgresql://` URLs to the `psycopg` driver.

Do not use local SQLite for the hosted web app. SQLite remains for desktop/local mode.

## Google Drive + Sheets research repository

For the current research phase, the simplest shared repository can be Google-based:

```text
NDIM Web on Cloud Run
  -> Google Drive folder for files and generated outputs
  -> Google Sheets ledger for structured evidence records and review state
```

Use this when you want normal users to open one web app while the project owner keeps the shared research repository in a Google account.

Recommended repository structure:

| Layer | Google tool | Purpose |
| --- | --- | --- |
| Workspace files | Drive folder | Uploads, accepted/rejected narrative exports, SDMX packages, policy briefs, backup bundles, desk reviews, and reports. |
| Evidence ledger | Google Sheet | Narrative IDs, route, place, consent, visibility, reviewer decision, hashes, encoding scores, model run IDs, policy-output links, and audit notes. |
| Optional automation | Apps Script | Controlled sync endpoint after approval. Keep it off until permissions and audit rules are agreed. |

Configure these environment variables in Cloud Run, GitHub Actions, or the runtime environment:

| Variable | Meaning |
| --- | --- |
| `NDIM_GOOGLE_DRIVE_FOLDER_ID` | The shared Drive folder ID for the NDIM master repository. |
| `NDIM_GOOGLE_SHEETS_LEDGER_ID` | The Google Sheet ID for the evidence ledger. |
| `NDIM_GOOGLE_REPOSITORY_ROOT_NAME` | Human-readable repository name shown in the app. |
| `NDIM_GOOGLE_REPOSITORY_OWNER` | Project owner or institution responsible for the repository. |
| `NDIM_GOOGLE_REPOSITORY_MODE` | Use `manual_package` while sync is manual, or `google_drive_sheets` once configured. |
| `NDIM_GOOGLE_APPS_SCRIPT_SYNC_URL` | Optional controlled sync endpoint. Leave blank until the approval layer is ready. |

The app endpoint `GET /repository/google/status` reports whether Drive and Sheets are configured. The UI then shows links to the Drive repository and Sheets ledger only when real IDs are present. If they are blank, NDIM falls back to downloadable SDMX JSON, observation CSV, and DSD JSON packages.

Important limits:

- Google Drive is file storage, not a relational database.
- Google Sheets is acceptable as a controlled early ledger, but not as a high-scale production database.
- Sensitive narratives should not be uploaded until consent, visibility, reviewer approval, and project data-governance rules are clear.
- For institutional scale, keep PostgreSQL or another governed database as the database of record.

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

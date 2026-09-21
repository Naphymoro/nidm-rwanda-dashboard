# NDIM Engine

Research-grade local-first narrative ingestion, evidence governance, modelling, digital-twin, inoculation, and policy-output workflow for the Narrative Diffusion and Inoculation Model.

Current alpha: `0.9.0-alpha.9` adds a web-view demo route, mode-specific encoding, package refreshes, and a lean GitHub-to-Google Cloud Run deployment path for the default web app.

## Production architecture

The canonical alpha runtime is the FastAPI integrated UI. The same backend can run as a local desktop app or as the hosted NDIM Web app.

- Backend and UI: FastAPI, Pydantic, Python scientific stack
- Database: local SQLite by default, with a PostgreSQL-ready schema path for institutional deployments
- Desktop launcher: PyInstaller/Tkinter wrapper that starts the local backend and opens the browser
- Data model: local-first evidence ledger, SDMX-oriented exports, deterministic offline fallback

The `client/`, `frontend/`, and root Next.js `app/` folders remain as legacy/reference UI work. They are not the production desktop UI unless a future architecture decision replaces this local-first runtime. See `docs/ARCHITECTURE_DECISION.md`.

## Lean web deployment

For real users, the recommended default path is NDIM Web:

```text
GitHub -> GitHub Actions -> Google Artifact Registry -> Google Cloud Run -> PostgreSQL
                                                     -> optional Google Drive + Sheets repository layer
```

Use the desktop package only for offline/sensitive fieldwork. Use Colab only for advanced reproducibility notebooks.

The Cloud Run deployment assets are:

- `backend/Dockerfile`
- `.github/workflows/cloud-run-deploy.yml`
- `deployment/cloud-run/service.template.yaml`
- `docs/CLOUD_RUN_RESEARCH_DEPLOYMENT.md`

The hosted app requires `DATABASE_URL`; do not rely on local SQLite on Cloud Run.

### Research-phase Google repository

During the early hosted phase, NDIM can use Google Drive and Google Sheets as a lightweight shared research repository:

- Google Drive stores workspace files, uploads, approved/rejected narrative exports, SDMX packages, reports, backups, and audit bundles.
- Google Sheets stores the structured evidence ledger: workspace IDs, narrative IDs, review decisions, consent, visibility, hashes, encoding scores, model runs, and policy-output references.
- The NDIM app still runs on Cloud Run or locally. Drive is file storage, and Sheets is a governed ledger. They are not a substitute for a high-scale production database.
- If Drive/Sheets IDs are not configured, the safe default remains manual export of SDMX JSON, observation CSV, DSD JSON, and policy briefs.

Optional configuration is shown in `.env.example`:

```env
NDIM_GOOGLE_REPOSITORY_MODE=manual_package
NDIM_GOOGLE_REPOSITORY_ROOT_NAME=NDIM Master Repository
NDIM_GOOGLE_REPOSITORY_OWNER=
NDIM_GOOGLE_DRIVE_FOLDER_ID=
NDIM_GOOGLE_SHEETS_LEDGER_ID=
NDIM_GOOGLE_APPS_SCRIPT_SYNC_URL=
```

The app exposes `GET /repository/google/status` so the UI can show whether the Google-backed repository is configured and can open the Drive folder or Sheets ledger without guessing.

## Core modules

The new **Research Studio** at `/` provides narrative exploration, streamed domain
tool execution, scenario comparison, and downloadable research artifacts. Select
a workspace to save completed explorations, reopen them after refresh, or delete
them; the default tab-only option remains unsaved. The
existing integrated workflow remains at `/workbench`. Start with
[the code and architecture guide](docs/RESEARCH_STUDIO.md) to learn the system and
the planned path from deterministic skills to an agent runtime.

For an operator-facing explanation of the original ingestion, evidence-gate,
encoding, modelling and export workflow, see the [NIDM user guide](docs/NIDM_USER_GUIDE.md).
The complete original workflow remains available at `/classic-workbench` while
the newer `/` Research Studio is being expanded.

1. SDMX-inspired narrative ingestion gateway
2. Canonical narrative schema
3. Manual, AI, and hybrid encoding workflow
4. Country and administrative-unit categorization
5. Compartmental model API
6. Agent-based/hybrid digital-twin API
7. Bayesian/RL feedback and model-improvement loop
8. Inoculation diagnosis and counter-narrative testing
9. Local backup, restore, and support bundle exports
10. Workspace manager for project presets, duplication, import/export, and active workspace persistence
11. Research Assistant panel for progress, next-best-action guidance, scientific interpretation, and policy caution

## Supported alpha platforms

- Windows 10/11: installer and portable ZIP release path
- macOS: PyInstaller app build path, with `.dmg` signing/notarization as the release gate
- Linux: PyInstaller app build path, with AppImage/`.deb` packaging as the release gate

Minimum recommended hardware:

- 8 GB RAM for routine narrative ingestion and deterministic modelling
- 16 GB RAM if packaging or running heavy Torch/Pyro analytics locally
- 2 GB free disk for the app, local database, backups, and stress-test corpus

## Local development

```bash
cp .env.example .env
docker compose up --build
```

Legacy frontend: http://localhost:3000
Backend API: http://localhost:8000/docs

The current integrated research UI is served by the FastAPI backend:

```bash
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8010
```

Open http://127.0.0.1:8010/

## Desktop application packaging

NDIM Engine can be packaged as a local desktop application for Windows, macOS, and Linux using a PyInstaller launcher. The launcher starts the FastAPI backend locally, opens the UI in the user's default browser, and keeps data on the user's machine.

### Why this packaging strategy

- Keeps the existing FastAPI research backend unchanged.
- Avoids adding Electron/Tauri and a second runtime stack.
- Works offline for ingestion, governance, repository browsing, deterministic encoding fallback, modelling, policy export, manual, and stress-test corpus.
- Uses ordinary OS data folders for local databases and generated files.
- Supports later optional federation to Google Sheets, Drive, GitHub, institutional databases, or other master repositories through SDMX/DSD export packages.

### Local data folders

Desktop mode stores local data here unless `NDIM_DATA_DIR` is set:

- Windows: `%APPDATA%\NDIM Engine`
- macOS: `~/Library/Application Support/NDIM Engine`
- Linux: `${XDG_DATA_HOME:-~/.local/share}/ndim-engine`

The desktop data folder contains:

- `ndim_engine.sqlite3` local database
- `uploads/`
- `exports/`
- `sdmx/`
- `logs/`
- `backups/`
- `support/`
- `workspaces/`

The workspace folder contains project containers such as `NDIM Core` and `ClimateTales Rwanda`. A workspace keeps project templates, repository folders, validation material, stress-test material, and export defaults separate from other projects.

BYOK LLM keys remain session-only unless a future release adds an explicit opt-in secret store.

## Offline guarantees

The desktop app works offline for:

- narrative ingestion,
- CSV import,
- PDF import,
- deterministic/local narrative encoding,
- inoculation diagnosis fallback,
- ledger operations,
- evidence governance,
- local storage,
- analytics and modelling that ship with the runtime,
- backups and restore validation,
- exports,
- SDMX package generation,
- stress-test workflows.

Internet access is only required when a user explicitly chooses a remote LLM provider.

Health endpoints:

- `GET /api/status`
- `GET /health`
- `GET /offline/status`

The desktop launcher also includes **Check offline readiness**.

### Build Windows desktop app

From PowerShell:

```powershell
.\scripts\build_desktop.ps1
```

Clean rebuild:

```powershell
.\scripts\build_desktop.ps1 -Clean
```

Build the standalone app plus a user-level Windows installer:

```powershell
.\scripts\build_desktop.ps1 -Clean -Installer
```

The packaged app appears under `dist/`.

Current Windows outputs:

- `dist/NDIM Engine Runtime/Launch NDIM Engine.cmd` is the bundled local app runtime.
- `dist/NDIM Engine Setup.exe` is a user-level installer that copies the bundled runtime to the local Programs folder and creates a Start Menu shortcut.
- `dist/NDIM-Engine-Windows-Portable.zip` contains the bundled runtime folder and release notes for portable use.
- `installer/windows/ndim_engine.iss` is the Inno Setup script for producing a full Windows installer when Inno Setup is installed.

The stress-test corpus is bundled into the executable through the PyInstaller spec:

- `docs/ndim_stress_test_corpus_instructions.html`
- `stress_test_corpus/README.md`
- all `stress_test_corpus/*.csv`
- the bonus TXT story file

### Build macOS or Linux desktop app

From bash:

```bash
chmod +x scripts/build_desktop.sh
./scripts/build_desktop.sh
```

Clean rebuild:

```bash
./scripts/build_desktop.sh --clean
```

Build the desktop app plus the Python installer wrapper:

```bash
BUILD_INSTALLER=1 ./scripts/build_desktop.sh --clean
```

On Linux the PyInstaller output can be wrapped later as an AppImage or `.deb`. On macOS it can be wrapped as an app bundle and signed/notarized for public distribution. Those signing steps require platform-specific certificates.

### Build full Windows installer

For the built-in Python installer wrapper, run:

```powershell
.\scripts\build_desktop.ps1 -Installer
```

For a traditional signed enterprise installer, install Inno Setup, then compile:

```powershell
iscc .\installer\windows\ndim_engine.iss
```

The installer will be written to `dist/installer/`. If Inno Setup is not installed, use the standalone executable or portable ZIP from `dist/`.

### Desktop launcher features

The launcher provides:

- automatic backend startup on a free local port starting at `8010`
- clean loading/status window
- browser launch to the local NDIM UI
- offline readiness check
- Open data folder
- Export support bundle with diagnostics and logs
- Export full backup with manifest hashes
- Restore full backup with validation before writing files

Support bundles avoid the narrative database by default. Full backups include local research data and should be treated as sensitive.

## Safety and recovery

Read:

- `docs/OFFLINE_INSTALLATION.md`
- `docs/TROUBLESHOOTING.md`
- `docs/RECOVERY_GUIDE.md`
- `docs/PRODUCTION_HARDENING_AUDIT.md`
- `docs/DEPLOYMENT_MATRIX.md`

Backups include a `backup_manifest.json` file with SHA256 hashes. Restore fails closed if the manifest is missing, hashes do not match, or the ZIP contains unsafe paths.

### Desktop API helpers

When running locally, these backend endpoints are available:

- `GET /desktop/paths`
- `GET /desktop/support-bundle`
- `GET /desktop/full-backup`

The master repository workflow remains optional. The app prepares SDMX/DSD packages and tamper-evident hashes locally; it does not upload sensitive narratives unless a user explicitly exports or syncs through a configured connector. In the research-phase Google setup, Drive and Sheets can hold the master repository materials after reviewer approval, but the app still preserves consent, visibility, and audit metadata in the export package.

## Recommended deployment

Active hosted path: GitHub Actions deploys the lean FastAPI web build to Google Cloud Run.

For cloud users, use the Cloud Run workflow in `.github/workflows/cloud-run-deploy.yml`. For local research users, prefer the desktop package because it keeps sensitive research data on the user's machine.

For non-technical field testing, prefer GitHub Releases with platform installers rather than a hosted web link. The desktop package keeps sensitive research data on the user's machine.

## Alpha testing distribution

For invited alpha testers, signing is not a release blocker. Publish unsigned packages through GitHub Releases with clear tester instructions and checksums:

- Windows: `NDIM-Engine-Windows-Portable-<version>.zip` as the preferred alpha route
- Windows optional: `NDIM-Engine-Setup-<version>.exe`
- macOS: `NDIM-Engine-<version>.dmg`
- Linux: `ndim-engine_<version>_amd64.deb`
- Verification: `SHA256SUMS.txt`
- Instructions: `ALPHA_TESTER_README.md`

The cross-platform alpha release workflow is `.github/workflows/alpha-release.yml`. It runs the offline smoke test before packaging and uploads artifacts to a prerelease when a tag like `v0.9.0-alpha.8` is pushed.

Read `docs/ALPHA_TESTER_README.md` before sharing builds with testers.

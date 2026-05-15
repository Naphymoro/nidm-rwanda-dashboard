# NDIM Engine

Research-grade local-first narrative ingestion, evidence governance, modelling, digital-twin, inoculation, and policy-output workflow for the Narrative Diffusion and Inoculation Model.

## Stack

- Frontend: Next.js, TypeScript, CSS3 futuristic dashboard UI
- Backend: FastAPI, Pydantic, Python scientific stack
- Database: PostgreSQL/PostGIS-ready schema path, no Supabase dependency
- Runtime: Docker Compose for local development
- Deployment target: Render, Railway, Fly.io, or self-hosted VPS. Vercel is optional for frontend only.

## Core modules

1. SDMX-inspired narrative ingestion gateway
2. Canonical narrative schema
3. Manual, AI, and hybrid encoding workflow
4. Country and administrative-unit categorization
5. Compartmental model API
6. Agent-based/hybrid digital-twin API placeholder
7. RL feedback and model-improvement loop placeholder
8. Futuristic SaaS research dashboard

## Local development

```bash
cp .env.example .env
docker compose up --build
```

Frontend: http://localhost:3000
Backend API: http://localhost:8000/docs

The current integrated research UI is served by the FastAPI backend:

```bash
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8010
```

Open http://127.0.0.1:8010/

## Desktop application packaging

NDIM Engine can be packaged as a local desktop application for Windows, macOS, and Linux using a PyInstaller launcher. The launcher starts the FastAPI backend locally, opens the UI in the user’s default browser, and keeps data on the user’s machine.

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

BYOK LLM keys remain session-only unless a future release adds an explicit opt-in secret store.

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
- Open data folder
- Export support bundle with diagnostics and logs
- Export full backup
- Restore full backup

Support bundles avoid the narrative database by default. Full backups include local research data and should be treated as sensitive.

### Desktop API helpers

When running locally, these backend endpoints are available:

- `GET /desktop/paths`
- `GET /desktop/support-bundle`
- `GET /desktop/full-backup`

The master repository workflow remains optional. The app prepares SDMX/DSD packages and tamper-evident hashes locally; it does not upload sensitive narratives unless a user explicitly exports or syncs through a future connector.

## Recommended deployment

Best no-Supabase path: Render Blueprint or Railway monorepo deployment with managed PostgreSQL.

Vercel is excellent for the Next.js frontend, but this platform also needs a Python backend and database. For a simpler single-platform deployment, Render or Railway is better than Vercel alone.

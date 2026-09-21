# Architecture Decision: Local-First Desktop Runtime

Status: accepted for alpha production hardening

## Decision

NDIM Engine uses the **FastAPI-only integrated UI** as the canonical production desktop architecture.

The desktop launcher starts a local FastAPI process on `127.0.0.1`, serves Research Studio from `/`, the integrated workflow UI from `/workbench`, the manual from `/manual`, and stores research data in the operating system data folder. The studio introduces a bounded skill harness within the same runtime; see `docs/RESEARCH_STUDIO.md`.

## Why this architecture

- It avoids requiring Node.js after installation.
- It supports offline-first use because the backend, UI, manual, and stress-test corpus are bundled together.
- It keeps one deployable runtime for non-technical researchers.
- It preserves future web deployment options without making the desktop app depend on a cloud UI.
- It makes support bundles, local backups, and restore validation easier to reason about.

## Canonical runtime

Production desktop runtime:

- `desktop/ndim_desktop.py`
- `backend/app/main.py`
- `backend/app/workflow_ui.py`
- `backend/app/storage.py`
- `stress_test_corpus/`
- `docs/`

Legacy/reference UI code:

- `client/`
- `frontend/`
- root Next.js `app/`

These folders are retained for design/reference experiments, but they are not the production desktop UI unless a future architecture decision replaces this one.

## Packaging model

Windows uses a bundled runtime folder plus a user-level installer. macOS and Linux are built by the same PyInstaller launcher pipeline through CI. Platform-native signing/notarization remains an institutional release step because it requires private certificates.

## Offline strategy

Offline capability is explicit. The app exposes `/offline/status` and `/health`, uses deterministic encoding when remote LLMs are unavailable, and never requires a cloud database for local ingestion, governance, modelling, backups, or exports.

## Security posture

The app only permits localhost-style CORS origins, validates upload size and file extension, verifies backup manifests before restore, and writes a tamper-evident local audit log for backup/support events.

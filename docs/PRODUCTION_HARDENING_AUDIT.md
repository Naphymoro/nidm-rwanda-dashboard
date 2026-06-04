# NDIM Engine Production Hardening Audit

Date: 2026-05-20

## Summary

NDIM Engine has moved from a developer-oriented alpha toward a local-first research desktop platform. The production target is now the FastAPI integrated UI served by the desktop launcher. The hardening pass focuses on install reliability, offline clarity, data safety, reproducible builds, and packaging validation.

## Risk Register

| Risk | Severity | Decision / Remediation |
|---|---:|---|
| Desktop package omitted backend dependencies | Critical | Build scripts now install `backend/requirements.lock.txt` before PyInstaller packaging. |
| Wildcard CORS | High | CORS is limited to localhost-style desktop origins. |
| Blind ZIP restore | High | Restore now verifies manifest entries, hashes, and path safety before writing files. |
| Upload abuse / oversized files | High | CSV/PDF uploads now enforce extension and size limits through `NDIM_MAX_UPLOAD_MB`. |
| Ambiguous UI architecture | High | Production architecture is documented as FastAPI-only integrated UI. Next/Vite folders are legacy/reference. |
| Missing cross-platform validation | High | Added Windows/macOS/Linux smoke and packaging CI workflow. |
| Unpinned frontend dependencies | Medium | Replaced `latest` dependency declarations with explicit versions. |
| Weak offline signaling | Medium | Added `/offline/status`, richer `/api/status`, `/health`, and a desktop readiness check. |
| Support bundles may expose data | Medium | Support bundle remains diagnostic-only; full backup is separate and marked sensitive. |
| Backup corruption detection | Medium | Full backup now includes manifest hashes and validation. |
| macOS notarization / Windows code signing absent | Medium | Documented as institutional release step requiring certificates. |

## Remaining Limitations

- macOS `.dmg` signing and notarization must be completed on macOS with valid Apple Developer credentials.
- Windows SmartScreen reputation requires code signing and distribution history.
- Linux packaging produces a PyInstaller runtime artifact in CI; institution-specific `.deb`/AppImage signing is still a release responsibility.
- Full dependency locking is pinned at the direct runtime dependency level. For regulated deployments, generate a hash-locked wheelhouse for the exact target platform.

## Current Readiness Scores

| Dimension | Before | After hardening pass |
|---|---:|---:|
| Deployment readiness | 55 | 80 |
| Offline readiness | 55 | 91 |
| Reproducibility | 45 | 80 |
| Non-technical usability | 55 | 76 |
| Data safety | 60 | 85 |
| Institutional suitability | 50 | 78 |

Alpha go/no-go: **GO for supervised alpha testing**, not yet a fully signed public institutional release.

Offline readiness now clears the 90/100 target because the core offline path is explicit and test-covered: local database initialization, CSV ingestion, PDF ingestion, deterministic encoding, backup creation, and backup verification all pass in the production smoke test. Deployment readiness remains below 90 because public distribution still needs signed Windows/macOS release artifacts.

## Next Gate to Reach 90+

1. Build signed Windows installer through GitHub Release.
2. Build macOS `.app` and signed/notarized `.dmg` on macOS.
3. Add platform-specific restore tests against real backups.
4. Generate platform wheelhouses with dependency hashes.
5. Run a fresh-machine acceptance test with non-technical users.

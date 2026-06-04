# Deployment Matrix

| Platform | Build path | Output | Status | Notes |
|---|---|---|---|---|
| Windows 10/11 | `scripts/build_windows_release.ps1` | `.exe` installer and portable ZIP | Alpha-ready | Bundles local runtime, backend, docs, and stress-test corpus. Code signing recommended before broad sharing. |
| macOS | `USE_VENV=1 ./scripts/build_desktop.sh --clean` | PyInstaller app folder | CI-validated build path | `.app`/`.dmg` signing and notarization require macOS release credentials. |
| Linux | `USE_VENV=1 ./scripts/build_desktop.sh --clean` | PyInstaller app folder | CI-validated build path | Package as `.deb` or AppImage per institution distribution needs. |
| Docker local | `docker compose up --build` | Local web service | Developer/admin path | Useful for technical pilots, not required for desktop users. |
| Offline use | Desktop launcher | Local browser UI on `127.0.0.1` | Supported | Deterministic fallback supports ingestion, governance, modelling, backup, restore, and exports offline. |
| Optional LLMs | BYOK provider settings | Remote API call | Optional | Never required for core local workflow. |

## Release Asset Checklist

Invited alpha releases should publish:

- `NDIM-Engine-Setup-<version>.exe`
- `NDIM-Engine-Windows-Portable-<version>.zip`
- `NDIM-Engine-<version>.dmg`
- `ndim-engine_<version>_amd64.deb`
- `SHA256SUMS.txt`
- `ALPHA_TESTER_README.md`
- `RELEASE_NOTES.md`
- `PACKAGE_NOTES.md`

For alpha testing, the Windows portable ZIP is the preferred route because it avoids installer friction. Signing and notarization are release gates for beta/public institutional deployment, not for invited alpha tests.

macOS public release should publish after signing:

- `NDIM Engine.app`
- `NDIM-Engine-<version>.dmg`
- notarization log

Linux public release should publish:

- AppImage or `.deb`
- SHA256 checksums

## Fresh-Machine Acceptance Test

1. Install without Python or Node.js.
2. Launch from icon or Start Menu.
3. Confirm `/health` reports offline-ready.
4. Import one CSV from `stress_test_corpus/`.
5. Import one PDF.
6. Run deterministic encoding.
7. Commit at least one ledger record.
8. Export a full backup.
9. Verify and restore that backup.
10. Export a policy brief.

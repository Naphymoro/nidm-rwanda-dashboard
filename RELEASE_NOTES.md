# NDIM Engine Desktop Release Notes

## Package

This Windows package is a local-first NDIM Engine desktop distribution. It installs and runs the research tool on the user's own machine.

## Files to publish

- `dist/NDIM Engine Setup.exe` - one-click Windows installer.
- `dist/NDIM-Engine-Windows-Portable.zip` - portable archive containing the bundled runtime. Users can unzip it and run `Launch NDIM Engine.cmd`.

## What is bundled

- NDIM Engine backend and integrated workflow UI.
- Bundled Python runtime and installed Python packages required by the current app.
- Manual and stress-test instructions.
- Full `stress_test_corpus/` CSV/TXT corpus.
- Local SQLite database support.

Users do not need to install Python, Node, npm, pip packages, or project requirements manually.

## Installation

1. Download `NDIM Engine Setup.exe`.
2. Double-click the installer.
3. Choose an install folder or keep the default.
4. Launch NDIM Engine from the Start Menu shortcut.
5. The app opens a local browser page at `http://127.0.0.1:8010` or the next available local port.

Portable option:

1. Download `NDIM-Engine-Windows-Portable.zip`.
2. Extract the ZIP.
3. Open `NDIM Engine Runtime/Launch NDIM Engine.cmd`.

## Data storage

The app stores local research data on the user's machine. In desktop mode the launcher creates folders for data, uploads, exports, logs, SDMX packages, backups, and support bundles.

## Stress-test corpus

The stress-test corpus is included in the package. It contains route-specific CSV files plus a bonus TXT narrative for testing narrative ingestion, SDMX readiness, approval, encoding, modelling, and policy-output workflow.

## Distribution

GitHub Releases is the recommended place to host the installer. Do not rely on local file paths as download links; upload `NDIM Engine Setup.exe` and `NDIM-Engine-Windows-Portable.zip` as release assets.

## Known limitations

- This Windows build is unsigned, so Windows SmartScreen may warn users on first launch.
- Advanced Torch/Pyro analytics are not bundled in this package; deterministic fallback analytics remain available.
- macOS and Linux packages must be built on those operating systems.

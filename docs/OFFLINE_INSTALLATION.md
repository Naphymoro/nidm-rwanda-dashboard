# Offline Installation Guide

This guide is for researchers who need NDIM Engine to run without internet after installation.

## Windows

Use one of these release files:

- `NDIM-Engine-Setup-<version>.exe`
- `NDIM-Engine-Windows-Portable-<version>.zip`

Installer path:

1. Double-click the installer.
2. Accept the default local user install location.
3. Open NDIM Engine from the Start Menu.
4. Click **Check offline readiness** in the launcher.

Portable ZIP path:

1. Extract the ZIP.
2. Open the extracted folder.
3. Double-click `Launch NDIM Engine.cmd`.
4. Click **Check offline readiness** in the launcher.

## macOS

Use the signed `.dmg` once available.

1. Open the `.dmg`.
2. Drag NDIM Engine into Applications.
3. Open NDIM Engine.
4. Confirm offline readiness.

Unsigned alpha builds may require right-clicking the app and selecting **Open**.

## Linux

Use the AppImage or `.deb` package once published.

For technical alpha builds, use the PyInstaller output from CI and run the launcher script from the extracted folder.

## What Works Offline

- Narrative intake
- CSV import
- PDF import
- SDMX readiness checks
- Evidence ledger
- Approval/rejection/commit workflow
- Deterministic encoding
- Inoculation diagnosis fallback
- Compartmental model
- Agent model proxy
- Digital twin
- Bayesian/RL local analytics where dependencies are bundled
- Policy brief export
- Full backup and restore
- Stress-test corpus exercises

## What Needs Internet

Only optional remote LLM augmentation needs internet. If no key or internet is available, use deterministic/local encoding.

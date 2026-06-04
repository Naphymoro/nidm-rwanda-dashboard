# NDIM Engine Alpha Testing Build

This is an **unsigned alpha testing build** for invited researchers and institutional testers.

NDIM Engine runs locally on your computer. Core functions do not require internet:

- narrative intake,
- CSV/PDF/text import,
- deterministic encoding,
- evidence ledger,
- modelling,
- policy export,
- stress-test corpus,
- backup and restore.

Only optional remote LLM augmentation requires internet and a user-provided key.

## Why your computer may show a warning

This alpha build is not yet code-signed.

That means Windows or macOS may warn that the publisher cannot be verified. This is expected for an invited alpha build and does not mean the app is malicious.

Only download NDIM Engine from the official GitHub Releases page. Do not install builds sent through chat apps or email attachments unless the file hash matches the release checksum.

## Windows: easiest alpha path

Preferred file:

`NDIM-Engine-Windows-Portable-<version>.zip`

Steps:

1. Download the portable ZIP from GitHub Releases.
2. Extract the ZIP to a normal folder, such as Documents.
3. Open the extracted folder.
4. Double-click `Launch NDIM Engine.cmd`.
5. If Windows shows a warning, choose **More info** and then **Run anyway**.
6. In the launcher, click **Check offline readiness**.

Optional file:

`NDIM-Engine-Setup-<version>.exe`

Use this only if you want a Start Menu shortcut.

## macOS: alpha path

Preferred file:

`NDIM-Engine-<version>.dmg`

Steps:

1. Download the DMG from GitHub Releases.
2. Open it and drag NDIM Engine into Applications if shown.
3. If macOS blocks the app, right-click NDIM Engine and choose **Open**.
4. Confirm that you want to open it.
5. Use **Check offline readiness** after the launcher opens.

For broad public distribution, macOS builds should later be signed and notarized.

## Linux: alpha path

Preferred files:

- `ndim-engine_<version>_amd64.deb` for Debian/Ubuntu systems
- AppImage when available

For `.deb`:

```bash
sudo apt install ./ndim-engine_<version>_amd64.deb
ndim-engine
```

For unpacked alpha artifacts, run the launcher from the extracted folder.

## Verify checksums

Each alpha release should include:

`SHA256SUMS.txt`

This file contains fingerprints for release artifacts. It lets testers confirm that downloads were not changed after release.

Windows PowerShell:

```powershell
Get-FileHash .\NDIM-Engine-Windows-Portable-<version>.zip -Algorithm SHA256
```

macOS/Linux:

```bash
shasum -a 256 NDIM-Engine-<version>.dmg
sha256sum ndim-engine_<version>_amd64.deb
```

Compare the result with `SHA256SUMS.txt`.

## What to send back when something fails

Open the launcher and click:

**Export support bundle**

The support bundle excludes the narrative database by default. Full backups are sensitive and should only be shared intentionally.

## Demo walkthrough

After launching the app, testers can open:

`http://127.0.0.1:8010/demo-video`

This is a browser-based walkthrough of the current NDIM workflow. It is not a separate app; it shows the intended testing path from workspace selection through narrative intake, encoding, modelling, digital twin feedback, inoculation, and policy export.

## Alpha release boundary

This build is suitable for invited alpha testing.

It is not yet a fully signed public institutional release. Before broad deployment, NDIM Engine should add:

- Windows code signing,
- macOS signing and notarization,
- tested Linux release packages on target distributions.

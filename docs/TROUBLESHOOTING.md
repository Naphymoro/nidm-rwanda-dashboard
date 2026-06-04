# Troubleshooting Guide

## The app opens but says the backend failed

1. Open the launcher.
2. Note the log path shown in the error dialog.
3. Click **Export support bundle**.
4. Send the support ZIP to the project maintainer.

The support bundle excludes the narrative database by default.

## The browser page does not open

Click **Open NDIM Engine** in the launcher. If that still fails, copy the local URL from the launcher and paste it into a browser on the same computer.

## CSV or PDF upload fails

Check:

- File size is below the configured limit.
- CSV files end in `.csv`.
- PDF files end in `.pdf`.
- The file is not locked by another application.

The default upload limit is 50 MB and can be changed with `NDIM_MAX_UPLOAD_MB`.

## Restore fails

Restore stops if:

- the ZIP is not an NDIM backup,
- `backup_manifest.json` is missing,
- file hashes do not match,
- the archive contains unsafe paths.

This protects the local repository from corrupted or malicious restore files.

## Remote LLM encoding fails

Use deterministic encoding or provide a valid user-owned key. Remote LLMs are optional. The core workflow remains offline-ready.

## Where data is stored

Windows:

`%APPDATA%\NDIM Engine`

macOS:

`~/Library/Application Support/NDIM Engine`

Linux:

`${XDG_DATA_HOME:-~/.local/share}/ndim-engine`

## Recovery checklist

1. Export a support bundle.
2. Export a full backup if the app can still open.
3. Copy the local data folder before reinstalling.
4. Reinstall NDIM Engine.
5. Restore from the most recent verified backup.

# Backup and Recovery Guide

NDIM Engine is local-first. The local database and files are the authoritative copy unless the user intentionally exports or syncs data elsewhere.

## Full Backup

Use **Export full backup** in the desktop launcher.

The backup contains sensitive research data:

- local SQLite database,
- uploads,
- exports,
- SDMX packages,
- logs,
- backup manifest.

Each file in the backup is recorded with SHA256 in `backup_manifest.json`.

## Support Bundle

Use **Export support bundle** when asking for technical help.

The support bundle contains diagnostics and logs only. It does not include the narrative database by default.

## Restore

Use **Restore full backup** in the desktop launcher.

NDIM Engine verifies:

- the manifest exists,
- every restored file is listed in the manifest,
- each file hash matches,
- archive paths are safe.

If verification fails, restore stops before replacing data.

## Tamper-Evident Audit Log

Backup, restore, and support bundle events are written to:

`logs/tamper-evident-audit.jsonl`

Each event contains the previous event hash. This is not a blockchain, but it gives local tamper evidence and can later be anchored to a master repository approval layer.

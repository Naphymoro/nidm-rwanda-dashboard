from __future__ import annotations

import json
import os
import platform
import sys
import zipfile
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Dict, Iterable

from .security import validate_zip_member


APP_NAME = "NDIM Engine"
APP_SLUG = "ndim-engine"


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def resource_root() -> Path:
    bundled = os.getenv("NDIM_BUNDLED_ROOT")
    if bundled:
        return Path(bundled).expanduser().resolve()
    frozen_root = getattr(sys, "_MEIPASS", None)
    if frozen_root:
        return Path(frozen_root).resolve()
    here = Path(__file__).resolve()
    for candidate in [here.parents[2], here.parents[1], here.parents[0]]:
        if (candidate / "docs").exists() or (candidate / "stress_test_corpus").exists() or (candidate / "backend").exists():
            return candidate
    return here.parents[2]


def resource_path(*parts: str) -> Path:
    return resource_root().joinpath(*parts)


def default_data_dir() -> Path:
    override = os.getenv("NDIM_DATA_DIR")
    if override:
        return Path(override).expanduser().resolve()

    system = platform.system().lower()
    home = Path.home()
    if system == "windows":
        base = Path(os.getenv("APPDATA") or home / "AppData" / "Roaming")
        return base / APP_NAME
    if system == "darwin":
        return home / "Library" / "Application Support" / APP_NAME
    return Path(os.getenv("XDG_DATA_HOME") or home / ".local" / "share") / APP_SLUG


def app_paths() -> Dict[str, Path]:
    base = default_data_dir()
    return {
        "data": base,
        "uploads": base / "uploads",
        "exports": base / "exports",
        "logs": base / "logs",
        "sdmx": base / "sdmx",
        "backups": base / "backups",
        "support": base / "support",
        "workspaces": base / "workspaces",
    }


def ensure_app_dirs() -> Dict[str, Path]:
    paths = app_paths()
    for path in paths.values():
        path.mkdir(parents=True, exist_ok=True)
    return paths


def sqlite_database_url() -> str:
    paths = ensure_app_dirs()
    db_path = paths["data"] / "ndim_engine.sqlite3"
    return f"sqlite:///{db_path.resolve().as_posix()}"


def diagnostics(create_dirs: bool = False) -> Dict[str, object]:
    paths = ensure_app_dirs() if create_dirs else app_paths()
    return {
        "app": APP_NAME,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "platform": platform.platform(),
        "python": sys.version,
        "frozen": bool(getattr(sys, "frozen", False)),
        "resource_root": str(resource_root()),
        "paths": {key: str(value) for key, value in paths.items()},
        "database_url_mode": "environment" if os.getenv("DATABASE_URL") else "local_sqlite",
        "desktop_mode": os.getenv("NDIM_DESKTOP") == "1",
    }


def write_diagnostics() -> Path:
    paths = ensure_app_dirs()
    target = paths["support"] / "diagnostics.json"
    target.write_text(json.dumps(diagnostics(create_dirs=True), indent=2), encoding="utf-8")
    return target


def file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def append_audit_event(action: str, detail: str, payload: Dict[str, object] | None = None) -> Dict[str, object]:
    paths = ensure_app_dirs()
    audit_path = paths["logs"] / "tamper-evident-audit.jsonl"
    previous_hash = ""
    if audit_path.exists():
        try:
            last = audit_path.read_text(encoding="utf-8").strip().splitlines()[-1]
            previous_hash = json.loads(last).get("event_hash", "")
        except Exception:
            previous_hash = "corrupt_previous_audit_line"
    event = {
        "at": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "detail": detail,
        "payload": payload or {},
        "previous_hash": previous_hash,
    }
    event["event_hash"] = sha256(json.dumps(event, sort_keys=True).encode("utf-8")).hexdigest()
    with audit_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, sort_keys=True) + "\n")
    return event


def make_support_bundle() -> Path:
    paths = ensure_app_dirs()
    bundle = paths["support"] / f"ndim-support-{utc_stamp()}.zip"
    diagnostics_path = write_diagnostics()
    with zipfile.ZipFile(bundle, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(diagnostics_path, "diagnostics.json")
        for log_file in paths["logs"].glob("*.log"):
            zf.write(log_file, f"logs/{log_file.name}")
        audit_path = paths["logs"] / "tamper-evident-audit.jsonl"
        if audit_path.exists():
            zf.write(audit_path, "logs/tamper-evident-audit.jsonl")
    append_audit_event("support_bundle_created", "Created a diagnostic support bundle without the narrative database.", {"bundle": str(bundle)})
    return bundle


def make_full_backup() -> Path:
    paths = ensure_app_dirs()
    backup = paths["backups"] / f"ndim-full-backup-{utc_stamp()}.zip"
    include_roots = ["uploads", "exports", "sdmx", "logs", "workspaces"]
    db_path = paths["data"] / "ndim_engine.sqlite3"
    files: list[tuple[Path, str]] = []
    if db_path.exists():
        files.append((db_path, "data/ndim_engine.sqlite3"))
    for key in include_roots:
        root = paths[key]
        for item in root.rglob("*"):
            if item.is_file() and item.resolve() != backup.resolve():
                files.append((item, f"{key}/{item.relative_to(root).as_posix()}"))
    manifest = {
        "schema_version": 1,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "sensitive_data": True,
        "diagnostics": diagnostics(),
        "files": [
            {
                "path": archive_name,
                "sha256": file_sha256(path),
                "bytes": path.stat().st_size,
            }
            for path, archive_name in files
        ],
    }
    with zipfile.ZipFile(backup, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("backup_manifest.json", json.dumps(manifest, indent=2, sort_keys=True))
        for path, archive_name in files:
            zf.write(path, archive_name)
    append_audit_event("full_backup_created", "Created a full sensitive-data backup.", {"bundle": str(backup), "file_count": len(files)})
    return backup


def _iter_backup_files(zf: zipfile.ZipFile) -> Iterable[zipfile.ZipInfo]:
    for info in zf.infolist():
        if info.is_dir() or info.filename == "backup_manifest.json":
            continue
        validate_zip_member(info.filename)
        yield info


def verify_backup_archive(backup: Path) -> Dict[str, object]:
    if not backup.exists():
        raise FileNotFoundError(f"Backup not found: {backup}")
    with zipfile.ZipFile(backup, "r") as zf:
        if "backup_manifest.json" not in zf.namelist():
            raise ValueError("Backup is missing backup_manifest.json.")
        manifest = json.loads(zf.read("backup_manifest.json").decode("utf-8"))
        expected = {item["path"]: item for item in manifest.get("files", [])}
        checked = 0
        for info in _iter_backup_files(zf):
            item = expected.get(info.filename)
            if not item:
                raise ValueError(f"Backup contains an unmanifested file: {info.filename}")
            digest = sha256(zf.read(info.filename)).hexdigest()
            if digest != item.get("sha256"):
                raise ValueError(f"Backup hash mismatch for {info.filename}")
            checked += 1
    return {"valid": True, "checked_files": checked, "manifest": manifest}


def restore_backup_archive(backup: Path) -> Dict[str, object]:
    verification = verify_backup_archive(backup)
    paths = ensure_app_dirs()
    restored = 0
    with zipfile.ZipFile(backup, "r") as zf:
        for info in _iter_backup_files(zf):
            relative = validate_zip_member(info.filename)
            if relative.parts and relative.parts[0] == "data":
                relative = Path(*relative.parts[1:])
            target = paths["data"] / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(info, "r") as source, target.open("wb") as destination:
                destination.write(source.read())
            restored += 1
    append_audit_event("full_backup_restored", "Restored a verified full backup.", {"backup": str(backup), "restored_files": restored})
    return {"restored_files": restored, "verification": verification}

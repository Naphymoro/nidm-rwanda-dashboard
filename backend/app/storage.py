from __future__ import annotations

import json
import os
import platform
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict


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
    return Path(__file__).resolve().parents[2]


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


def make_support_bundle() -> Path:
    paths = ensure_app_dirs()
    bundle = paths["support"] / f"ndim-support-{utc_stamp()}.zip"
    diagnostics_path = write_diagnostics()
    with zipfile.ZipFile(bundle, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(diagnostics_path, "diagnostics.json")
        for log_file in paths["logs"].glob("*.log"):
            zf.write(log_file, f"logs/{log_file.name}")
    return bundle


def make_full_backup() -> Path:
    paths = ensure_app_dirs()
    backup = paths["backups"] / f"ndim-full-backup-{utc_stamp()}.zip"
    include_roots = ["uploads", "exports", "sdmx", "logs"]
    db_path = paths["data"] / "ndim_engine.sqlite3"
    with zipfile.ZipFile(backup, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("backup_manifest.json", json.dumps(diagnostics(), indent=2))
        if db_path.exists():
            zf.write(db_path, "data/ndim_engine.sqlite3")
        for key in include_roots:
            root = paths[key]
            for item in root.rglob("*"):
                if item.is_file():
                    zf.write(item, f"{key}/{item.relative_to(root).as_posix()}")
    return backup

"""Atomic, workspace-local storage for completed exploratory runs.

Stored under evidence so existing full backups include runs; template exports and
workspace duplication exclude them. This is local project separation, not auth.
"""
import json
import os
import re
import tempfile
import marshal
import sys
from hashlib import sha256
from pathlib import Path
from uuid import UUID

from fastapi import HTTPException

from .storage import app_paths
from .workspaces import get_workspace


def run_folder(workspace_id: str) -> Path:
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", workspace_id):
        raise HTTPException(404, "Workspace not found")
    workspace = get_workspace(workspace_id)
    return app_paths()["workspaces"] / workspace["workspace_id"] / "evidence" / "research-runs"


def run_path(workspace_id: str, run_id: str) -> Path:
    try:
        if str(UUID(run_id)) != run_id:
            raise ValueError()
    except ValueError:
        raise HTTPException(404, "Research run not found")
    return run_folder(workspace_id) / (run_id + ".json")


def code_version() -> str:
    digest = sha256()
    for name in ("research.py", "encoding.py", "inoculation.py", "modelling.py", "schemas.py"):
        digest.update(name.encode())
        source = Path(__file__).with_name(name)
        if source.is_file():
            digest.update(source.read_bytes())
        else:
            # PyInstaller can bundle bytecode without individual source files.
            module = sys.modules[f"{__package__}.{source.stem}"]
            digest.update(marshal.dumps(module.__loader__.get_code(module.__name__)))
    return "sha256:" + digest.hexdigest()


def save_run(workspace_id: str, result: dict) -> None:
    target = run_path(workspace_id, result["run_id"])
    target.parent.mkdir(parents=True, exist_ok=True)
    # A failed write never exposes a partial run to history or downloads.
    fd, temporary = tempfile.mkstemp(dir=target.parent, prefix=".pending-")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(result, handle, ensure_ascii=False)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, target)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def load_run(workspace_id: str, run_id: str) -> dict:
    path = run_path(workspace_id, run_id)
    try:
        result = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise HTTPException(404, "Research run not found")
    # Imported full backups can acquire a new workspace ID.
    result["workspace_id"] = workspace_id
    return result


def list_runs(workspace_id: str) -> list[dict]:
    rows = []
    for path in run_folder(workspace_id).glob("*.json"):
        try:
            result = load_run(workspace_id, path.stem)
            rows.append({"run_id": result["run_id"], "created_at": result["created_at"],
                         "skill": result["skill"], "title": result["source"]["text"][:120]})
        except (ValueError, KeyError, HTTPException):
            continue
    return sorted(rows, key=lambda row: (row["created_at"], row["run_id"]), reverse=True)


def delete_run(workspace_id: str, run_id: str) -> None:
    try:
        run_path(workspace_id, run_id).unlink()
    except FileNotFoundError:
        raise HTTPException(404, "Research run not found")

from __future__ import annotations

import json
import re
import shutil
import zipfile
from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional

from fastapi import HTTPException, UploadFile
from pydantic import BaseModel, Field

from .security import clean_filename, validate_upload_file, validate_zip_member
from .storage import append_audit_event, app_paths, ensure_app_dirs, file_sha256, resource_path, utc_stamp


WORKSPACE_SCHEMA = "ndim-workspace-v1"
ACTIVE_WORKSPACE_FILE = "active_workspace.json"
WORKSPACE_FILE = "workspace.ndim.json"
DEFAULT_WORKSPACE_ID = "ndim-core"


class WorkspaceCreateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    description: str = ""
    base_workspace_id: Optional[str] = None
    country: str = "Rwanda"
    domain: str = "clean cooking"


class WorkspaceUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "workspace"


def _workspace_root() -> Path:
    ensure_app_dirs()
    root = app_paths()["workspaces"]
    root.mkdir(parents=True, exist_ok=True)
    return root


def _active_path() -> Path:
    return _workspace_root() / ACTIVE_WORKSPACE_FILE


def _workspace_dir(workspace_id: str) -> Path:
    safe = _slug(workspace_id)
    return _workspace_root() / safe


def _workspace_file(workspace_id: str) -> Path:
    return _workspace_dir(workspace_id) / WORKSPACE_FILE


def _default_dirs() -> Dict[str, str]:
    return {
        "repository": "repository",
        "evidence": "evidence",
        "templates": "templates",
        "exports": "exports",
        "validation": "validation",
        "stress_test_corpus": "stress_test_corpus",
    }


def _base_settings() -> Dict[str, Any]:
    return {
        "countries": ["Rwanda"],
        "admin_unit_mode": "country_schema",
        "domain": "clean cooking",
        "enabled_evidence_routes": [
            "structured_interview",
            "focus_group",
            "open_story",
            "indigenous_knowledge",
            "citizen_science",
            "crowd_batch",
            "experimental_feed",
        ],
        "default_evidence_route": "structured_interview",
        "default_language": "rw",
        "default_source_type": "interview",
        "default_period": "2026",
        "consent_defaults": {
            "visibility": "private",
            "consent": "restricted_research",
            "repository_mode": "local_project",
        },
        "llm_defaults": {
            "provider": "deterministic",
            "note": "Remote providers are optional and user-supplied.",
        },
        "manual_scoring_variables": ["E", "C", "tau", "kappa", "B", "S"],
        "model_defaults": {
            "horizon_days": 180,
            "model_mode": "hybrid",
            "initial_adoption": 0.10,
            "narrative_influence": 0.38,
            "trust_score": 0.60,
            "barrier_score": 0.35,
        },
        "digital_twin": {
            "mode": "feedback_calibrated_hybrid",
            "field_feedback_required": True,
        },
        "bayesian_priors": {"trustA": 6, "trustB": 4, "barrierA": 4, "barrierB": 6},
        "rl_optimizer": {"episodes": 80, "learning_rate": 0.18, "discount": 0.90},
        "inoculation_lab": {
            "enabled": True,
            "human_review_required": True,
            "output_style": "prebunk_refutation_booster",
        },
        "policy_outputs": ["policy_brief_html", "print_to_pdf", "json_audit_payload"],
        "assistant": {
            "name": "Research Assistant",
            "tone": "plain_language_scientific",
            "warn_when_evidence_is_thin": True,
            "show_next_best_action": True,
        },
        "stage_labels": {},
    }


def default_workspace(workspace_id: str) -> Dict[str, Any]:
    settings = _base_settings()
    if workspace_id == "climatetales-rwanda":
        settings.update(
            {
                "countries": ["Rwanda"],
                "domain": "clean climate technology adoption",
                "project_domains": [
                    "improved cookstoves",
                    "biogas",
                    "LPG/electric cooking",
                    "waste-to-energy",
                    "climate communication",
                ],
                "default_evidence_route": "open_story",
                "default_source_type": "field_note",
                "fieldwork_templates": [
                    "ethnographic_storylistening",
                    "digital_listening_summary",
                    "behavioural_design_lab",
                    "story_activation_pilot",
                    "influencer_training",
                ],
                "stage_labels": {
                    "intake": "Social Insight Mining",
                    "encoding": "Narrative diagnosis",
                    "compartmental": "Gamified influence simulator",
                    "digital": "Digital twin feedback",
                    "inoculation": "SBCC prototype lab",
                    "policy": "AIMS/Imperial project output",
                },
                "export_templates": [
                    "AIMS workshop brief",
                    "Imperial-AIMS project report",
                    "story activation pilot note",
                    "policy decision brief",
                ],
                "assistant": {
                    "name": "ClimateTales Guide",
                    "tone": "plain_language_scientific",
                    "warn_when_evidence_is_thin": True,
                    "show_next_best_action": True,
                    "project_guidance": [
                        "Capture consent and fieldwork context before modelling.",
                        "Keep ethnographic stories distinct from social feed observations.",
                        "Use behavioural design lab outputs before story activation pilots.",
                        "Review trusted messenger fit before exporting SBCC prototypes.",
                    ],
                },
            }
        )
        return {
            "schema": WORKSPACE_SCHEMA,
            "workspace_id": "climatetales-rwanda",
            "name": "ClimateTales Rwanda",
            "description": "AIMS-Imperial clean climate technology adoption workspace for social insight mining, digital listening, behavioural design labs, story activation pilots, influencer training, and gamified influence simulation.",
            "created_at": _now(),
            "updated_at": _now(),
            "version": 1,
            "settings": settings,
            "paths": _default_dirs(),
            "privacy": {
                "default_export_mode": "template_only",
                "sensitive_records_export_requires_confirmation": True,
            },
        }
    return {
        "schema": WORKSPACE_SCHEMA,
        "workspace_id": DEFAULT_WORKSPACE_ID,
        "name": "NDIM Core",
        "description": "Generic local-first Narrative Diffusion and Inoculation Model workspace.",
        "created_at": _now(),
        "updated_at": _now(),
        "version": 1,
        "settings": settings,
        "paths": _default_dirs(),
        "privacy": {
            "default_export_mode": "template_only",
            "sensitive_records_export_requires_confirmation": True,
        },
    }


def _write_workspace(workspace: Dict[str, Any]) -> Dict[str, Any]:
    workspace = deepcopy(workspace)
    workspace["schema"] = WORKSPACE_SCHEMA
    workspace["workspace_id"] = _slug(workspace["workspace_id"])
    workspace["updated_at"] = _now()
    folder = _workspace_dir(workspace["workspace_id"])
    folder.mkdir(parents=True, exist_ok=True)
    for relative in _default_dirs().values():
        (folder / relative).mkdir(parents=True, exist_ok=True)
    (folder / WORKSPACE_FILE).write_text(json.dumps(workspace, indent=2, sort_keys=True), encoding="utf-8")
    _seed_workspace_assets(folder, workspace)
    return workspace


def _seed_workspace_assets(folder: Path, workspace: Dict[str, Any]) -> None:
    guide = folder / "templates" / "workspace-guide.md"
    if not guide.exists():
        guide.write_text(
            f"# {workspace.get('name', 'NDIM Workspace')}\n\n"
            f"{workspace.get('description', '')}\n\n"
            "Use this workspace to keep evidence, templates, exports, and validation material separate from other projects.\n",
            encoding="utf-8",
        )
    corpus_target = folder / "stress_test_corpus"
    if not any(corpus_target.glob("*")):
        corpus_source = resource_path("stress_test_corpus")
        if corpus_source.exists():
            shutil.copytree(corpus_source, corpus_target, dirs_exist_ok=True)


def _read_workspace(path: Path) -> Dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema") != WORKSPACE_SCHEMA:
        raise ValueError("Unsupported workspace schema.")
    return data


def ensure_default_workspaces() -> None:
    for workspace_id in [DEFAULT_WORKSPACE_ID, "climatetales-rwanda"]:
        if not _workspace_file(workspace_id).exists():
            _write_workspace(default_workspace(workspace_id))
        elif workspace_id == "climatetales-rwanda":
            workspace = _read_workspace(_workspace_file(workspace_id))
            if workspace.get("name") == "#ClimateTales Rwanda":
                workspace["name"] = "ClimateTales Rwanda"
                _write_workspace(workspace)
    if not _active_path().exists():
        set_active_workspace(DEFAULT_WORKSPACE_ID)


def list_workspaces() -> List[Dict[str, Any]]:
    ensure_default_workspaces()
    rows: List[Dict[str, Any]] = []
    for path in sorted(_workspace_root().glob(f"*/{WORKSPACE_FILE}")):
        try:
            data = _read_workspace(path)
        except Exception:
            continue
        rows.append(
            {
                "id": data["workspace_id"],
                "workspace_id": data["workspace_id"],
                "name": data.get("name", data["workspace_id"]),
                "description": data.get("description", ""),
                "domain": data.get("settings", {}).get("domain", ""),
                "countries": data.get("settings", {}).get("countries", []),
                "updated_at": data.get("updated_at"),
            }
        )
    return rows


def get_workspace(workspace_id: str) -> Dict[str, Any]:
    ensure_default_workspaces()
    path = _workspace_file(workspace_id)
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Workspace not found: {workspace_id}")
    try:
        data = _read_workspace(path)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Workspace cannot be read: {exc}") from exc
    return data


def get_active_workspace() -> Dict[str, Any]:
    ensure_default_workspaces()
    try:
        active = json.loads(_active_path().read_text(encoding="utf-8")).get("workspace_id", DEFAULT_WORKSPACE_ID)
    except Exception:
        active = DEFAULT_WORKSPACE_ID
    return get_workspace(active)


def set_active_workspace(workspace_id: str) -> Dict[str, Any]:
    path = _workspace_file(workspace_id)
    if not path.exists():
        if workspace_id in {DEFAULT_WORKSPACE_ID, "climatetales-rwanda"}:
            workspace = _write_workspace(default_workspace(workspace_id))
        else:
            raise HTTPException(status_code=404, detail=f"Workspace not found: {workspace_id}")
    else:
        workspace = _read_workspace(path)
    _active_path().write_text(json.dumps({"workspace_id": workspace["workspace_id"], "set_at": _now()}, indent=2), encoding="utf-8")
    append_audit_event("workspace_set_active", f"Active workspace set to {workspace['workspace_id']}.", {"workspace_id": workspace["workspace_id"]})
    return workspace


def create_workspace(req: WorkspaceCreateRequest) -> Dict[str, Any]:
    base = get_workspace(req.base_workspace_id) if req.base_workspace_id else default_workspace(DEFAULT_WORKSPACE_ID)
    workspace = deepcopy(base)
    workspace["workspace_id"] = _unique_workspace_id(_slug(req.name))
    workspace["name"] = req.name.strip()
    workspace["description"] = req.description.strip() or f"{req.name.strip()} NDIM workspace."
    workspace["created_at"] = _now()
    workspace["version"] = 1
    settings = workspace.setdefault("settings", {})
    settings["countries"] = [req.country]
    settings["domain"] = req.domain
    result = _write_workspace(workspace)
    append_audit_event("workspace_created", f"Workspace created: {result['name']}.", {"workspace_id": result["workspace_id"]})
    return result


def update_workspace(workspace_id: str, req: WorkspaceUpdateRequest) -> Dict[str, Any]:
    workspace = get_workspace(workspace_id)
    if req.name is not None:
        workspace["name"] = req.name.strip() or workspace["name"]
    if req.description is not None:
        workspace["description"] = req.description
    if req.settings is not None:
        merged = workspace.setdefault("settings", {})
        merged.update(req.settings)
    workspace["version"] = int(workspace.get("version", 1)) + 1
    result = _write_workspace(workspace)
    append_audit_event("workspace_updated", f"Workspace updated: {result['name']}.", {"workspace_id": result["workspace_id"]})
    return result


def _unique_workspace_id(base: str) -> str:
    candidate = base
    suffix = 2
    while _workspace_file(candidate).exists():
        candidate = f"{base}-{suffix}"
        suffix += 1
    return candidate


def duplicate_workspace(workspace_id: str, name: Optional[str] = None) -> Dict[str, Any]:
    original = get_workspace(workspace_id)
    workspace = deepcopy(original)
    workspace["workspace_id"] = _unique_workspace_id(_slug(name or f"{original.get('name', workspace_id)} copy"))
    workspace["name"] = name or f"{original.get('name', workspace_id)} Copy"
    workspace["created_at"] = _now()
    workspace["version"] = 1
    result = _write_workspace(workspace)
    source = _workspace_dir(workspace_id)
    target = _workspace_dir(result["workspace_id"])
    for folder in ["templates", "validation", "stress_test_corpus"]:
        src = source / folder
        dst = target / folder
        if src.exists():
            shutil.copytree(src, dst, dirs_exist_ok=True)
    append_audit_event("workspace_duplicated", f"Workspace duplicated from {workspace_id}.", {"source": workspace_id, "target": result["workspace_id"]})
    return result


ExportMode = Literal["template_only", "template_with_stress_test", "full_backup"]


def export_workspace(workspace_id: str, mode: ExportMode = "template_only") -> Path:
    workspace = get_workspace(workspace_id)
    folder = _workspace_dir(workspace_id)
    export_root = app_paths()["exports"]
    export_root.mkdir(parents=True, exist_ok=True)
    package = export_root / f"{workspace_id}-{mode}-{utc_stamp()}.ndim-workspace.zip"
    manifest = {
        "schema": "ndim-workspace-package-v1",
        "workspace_id": workspace_id,
        "workspace_name": workspace.get("name"),
        "export_mode": mode,
        "created_at": _now(),
        "sensitive_records_included": mode == "full_backup",
        "files": [],
    }
    files: List[tuple[Path, str]] = [(folder / WORKSPACE_FILE, WORKSPACE_FILE)]
    include_dirs = ["templates", "validation"]
    if mode in {"template_with_stress_test", "full_backup"}:
        include_dirs.append("stress_test_corpus")
    if mode == "full_backup":
        include_dirs.extend(["repository", "evidence", "exports"])
    for dirname in include_dirs:
        root = folder / dirname
        if not root.exists():
            continue
        for item in root.rglob("*"):
            if item.is_file():
                files.append((item, f"{dirname}/{item.relative_to(root).as_posix()}"))
    for path, archive_name in files:
        manifest["files"].append({"path": archive_name, "sha256": file_sha256(path), "bytes": path.stat().st_size})
    with zipfile.ZipFile(package, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("workspace_package_manifest.json", json.dumps(manifest, indent=2, sort_keys=True))
        zf.writestr("README.md", _workspace_readme(workspace, mode))
        for path, archive_name in files:
            zf.write(path, archive_name)
    append_audit_event("workspace_exported", f"Workspace exported as {mode}.", {"workspace_id": workspace_id, "package": str(package)})
    return package


def _workspace_readme(workspace: Dict[str, Any], mode: str) -> str:
    return f"""# {workspace.get('name', 'NDIM Workspace')}

This is an NDIM workspace package.

- Workspace ID: {workspace.get('workspace_id')}
- Export mode: {mode}
- Sensitive records included: {'yes' if mode == 'full_backup' else 'no'}

Import this package from NDIM's Workspace Manager.
"""


def import_workspace(file: UploadFile) -> Dict[str, Any]:
    validate_upload_file(file, [".zip", ".ndim-workspace"], "NDIM workspace package")
    import_root = _workspace_root() / "_imports"
    import_root.mkdir(parents=True, exist_ok=True)
    target = import_root / clean_filename(file.filename)
    with target.open("wb") as handle:
        shutil.copyfileobj(file.file, handle)
    with zipfile.ZipFile(target, "r") as zf:
        names = zf.namelist()
        if WORKSPACE_FILE not in names:
            raise HTTPException(status_code=400, detail=f"Workspace package is missing {WORKSPACE_FILE}.")
        workspace = json.loads(zf.read(WORKSPACE_FILE).decode("utf-8"))
        if workspace.get("schema") != WORKSPACE_SCHEMA:
            raise HTTPException(status_code=400, detail="Unsupported workspace schema.")
        workspace["workspace_id"] = _unique_workspace_id(_slug(workspace.get("workspace_id") or workspace.get("name") or "imported-workspace"))
        workspace["created_at"] = workspace.get("created_at") or _now()
        workspace["updated_at"] = _now()
        result = _write_workspace(workspace)
        folder = _workspace_dir(result["workspace_id"])
        for info in zf.infolist():
            if info.is_dir() or info.filename in {WORKSPACE_FILE, "workspace_package_manifest.json", "README.md"}:
                continue
            relative = validate_zip_member(info.filename)
            if relative.parts and relative.parts[0] in {"templates", "validation", "stress_test_corpus", "repository", "evidence"}:
                destination = folder / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                with zf.open(info, "r") as source, destination.open("wb") as output:
                    output.write(source.read())
    append_audit_event("workspace_imported", "Workspace imported from package.", {"workspace_id": result["workspace_id"], "sha256": sha256(target.read_bytes()).hexdigest()})
    return result

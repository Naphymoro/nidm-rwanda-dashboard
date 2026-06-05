from __future__ import annotations

import os
from typing import Any, Dict


def _clean(value: str | None) -> str:
    return (value or "").strip()


def google_repository_status() -> Dict[str, Any]:
    """Return the configured Google-backed research repository state.

    This intentionally does not upload data. The current research-phase design
    uses Drive for files and Sheets for the governed ledger when those IDs are
    configured, while the app can still produce downloadable SDMX/CSV packages
    when no Google repository is connected.
    """

    drive_folder_id = _clean(os.getenv("NDIM_GOOGLE_DRIVE_FOLDER_ID"))
    sheets_ledger_id = _clean(os.getenv("NDIM_GOOGLE_SHEETS_LEDGER_ID"))
    apps_script_url = _clean(os.getenv("NDIM_GOOGLE_APPS_SCRIPT_SYNC_URL"))
    root_name = _clean(os.getenv("NDIM_GOOGLE_REPOSITORY_ROOT_NAME")) or "NDIM Master Repository"
    owner = _clean(os.getenv("NDIM_GOOGLE_REPOSITORY_OWNER")) or "not configured"
    mode = _clean(os.getenv("NDIM_GOOGLE_REPOSITORY_MODE")) or "manual_package"

    drive_url = f"https://drive.google.com/drive/folders/{drive_folder_id}" if drive_folder_id else ""
    sheet_url = f"https://docs.google.com/spreadsheets/d/{sheets_ledger_id}/edit" if sheets_ledger_id else ""
    configured = bool(drive_folder_id and sheets_ledger_id)

    return {
        "phase": "research-phase Google repository",
        "mode": "google_drive_sheets" if configured else mode,
        "configured": configured,
        "storage_model": {
            "files": "Google Drive workspace folders",
            "ledger": "Google Sheets lightweight research ledger",
            "app_runtime": "Cloud Run web app or local NDIM instance",
            "database_warning": "Google Drive is file storage, not a full relational database. Google Sheets is suitable as a controlled phase ledger, not high-scale production storage.",
        },
        "root_name": root_name,
        "owner": owner,
        "drive_folder_id": drive_folder_id,
        "drive_url": drive_url,
        "sheets_ledger_id": sheets_ledger_id,
        "sheet_url": sheet_url,
        "apps_script_sync_configured": bool(apps_script_url),
        "sync_status": "configured" if configured else "not_configured",
        "safe_default": "download_sdmx_csv_json_package",
        "required_env": [
            "NDIM_GOOGLE_DRIVE_FOLDER_ID",
            "NDIM_GOOGLE_SHEETS_LEDGER_ID",
        ],
        "optional_env": [
            "NDIM_GOOGLE_APPS_SCRIPT_SYNC_URL",
            "NDIM_GOOGLE_REPOSITORY_ROOT_NAME",
            "NDIM_GOOGLE_REPOSITORY_OWNER",
            "NDIM_GOOGLE_REPOSITORY_MODE",
        ],
        "workspace_folder_plan": [
            "uploads",
            "approved_narratives",
            "rejected_narratives",
            "encoded_outputs",
            "model_outputs",
            "policy_briefs",
            "sdmx_exports",
            "backups",
            "audit_logs",
            "reports",
        ],
        "ledger_tabs": [
            "workspaces",
            "narratives",
            "approvals",
            "rejections",
            "encoding_results",
            "inoculation_scores",
            "model_runs",
            "digital_twin_runs",
            "policy_outputs",
            "audit_log",
            "user_actions",
            "sdmx_exports",
        ],
        "user_message": (
            "Google Drive and Sheets are configured for the master research repository."
            if configured
            else "Google Drive and Sheets are not configured yet. NDIM will prepare downloadable SDMX, CSV, and JSON packages for manual upload."
        ),
    }

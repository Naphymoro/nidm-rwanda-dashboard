from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable

from fastapi import HTTPException, UploadFile


LOCAL_ORIGIN_REGEX = r"^https?://(127\.0\.0\.1|localhost|\[::1\])(:[0-9]+)?$"
DEFAULT_MAX_UPLOAD_MB = 50


def max_upload_bytes() -> int:
    raw = os.getenv("NDIM_MAX_UPLOAD_MB", str(DEFAULT_MAX_UPLOAD_MB))
    try:
        mb = max(1, min(int(raw), 250))
    except ValueError:
        mb = DEFAULT_MAX_UPLOAD_MB
    return mb * 1024 * 1024


def clean_filename(filename: str | None) -> str:
    name = Path(filename or "upload").name.strip()
    return name or "upload"


def validate_upload_file(file: UploadFile, allowed_extensions: Iterable[str], purpose: str) -> None:
    filename = clean_filename(file.filename)
    suffix = Path(filename).suffix.lower()
    allowed = {ext.lower() if ext.startswith(".") else f".{ext.lower()}" for ext in allowed_extensions}
    if suffix not in allowed:
        raise HTTPException(
            status_code=415,
            detail=f"{purpose} must be one of: {', '.join(sorted(allowed))}. Received {suffix or 'no extension'}.",
        )

    stream = file.file
    stream.seek(0, os.SEEK_END)
    size = stream.tell()
    stream.seek(0)
    limit = max_upload_bytes()
    if size <= 0:
        raise HTTPException(status_code=400, detail=f"{purpose} appears to be empty.")
    if size > limit:
        raise HTTPException(
            status_code=413,
            detail=f"{purpose} is too large. Maximum upload size is {limit // (1024 * 1024)} MB.",
        )


def validate_zip_member(member_name: str) -> Path:
    member = Path(member_name)
    if member.is_absolute() or ".." in member.parts:
        raise ValueError(f"Unsafe archive member path: {member_name}")
    return member

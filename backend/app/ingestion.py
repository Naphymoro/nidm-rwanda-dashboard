import pandas as pd
from typing import List
from fastapi import UploadFile
from .schemas import NarrativeRecord, NarrativeMetadata
import uuid


def normalize_text_input(text: str) -> List[NarrativeRecord]:
    return [
        NarrativeRecord(
            narrative_id=str(uuid.uuid4()),
            text=text,
            metadata=NarrativeMetadata(source_type="text"),
        )
    ]


def normalize_csv(file: UploadFile) -> List[NarrativeRecord]:
    df = pd.read_csv(file.file)
    records = []
    for _, row in df.iterrows():
        narrative_text = ""
        for column in ["narrative", "text", "quote", "story", "content", "body"]:
            value = row.get(column)
            if pd.notna(value) and str(value).strip():
                narrative_text = str(value)
                break
        provenance = {
            key: row.get(key)
            for key in [
                "evidence_mode",
                "source_name",
                "period",
                "language",
                "knowledge_type",
                "community_validation",
                "sensitivity",
                "consent_tier",
                "visibility",
                "contributor_type",
                "validation_status",
            ]
            if key in row and pd.notna(row.get(key))
        }
        records.append(
            NarrativeRecord(
                narrative_id=str(row.get("narrative_id") or row.get("id") or uuid.uuid4()),
                text=narrative_text,
                metadata=NarrativeMetadata(
                    source_type=str(row.get("source_type") or "csv"),
                    source_name=str(row.get("source_name")) if pd.notna(row.get("source_name")) else None,
                    country=row.get("country"),
                    admin_unit=row.get("admin_unit") or row.get("district") or row.get("sector") or row.get("province"),
                    language=str(row.get("language")) if pd.notna(row.get("language")) else "en",
                    provenance=provenance,
                ),
            )
        )
    return records


def normalize_pdf(file: UploadFile) -> List[NarrativeRecord]:
    from pypdf import PdfReader

    reader = PdfReader(file.file)
    text = "\n".join([page.extract_text() or "" for page in reader.pages])

    return [
        NarrativeRecord(
            narrative_id=str(uuid.uuid4()),
            text=text,
            metadata=NarrativeMetadata(source_type="pdf"),
        )
    ]

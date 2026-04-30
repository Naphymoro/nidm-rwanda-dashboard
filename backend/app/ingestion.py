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
        records.append(
            NarrativeRecord(
                narrative_id=str(uuid.uuid4()),
                text=str(row.get("narrative", "")),
                metadata=NarrativeMetadata(
                    source_type="csv",
                    country=row.get("country"),
                    admin_unit=row.get("admin_unit"),
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

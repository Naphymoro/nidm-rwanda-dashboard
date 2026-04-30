from fastapi import FastAPI, UploadFile, File
from typing import List

from .schemas import NarrativeRecord, SimulationRequest, SimulationResult, EncodedNarrative
from .ingestion import normalize_text_input, normalize_csv, normalize_pdf
from .encoding import encode_narrative

app = FastAPI(title="NIDM API", version="0.3")

@app.get("/")
def root():
    return {"message": "NIDM backend running"}

@app.post("/ingest/text", response_model=List[NarrativeRecord])
def ingest_text(narrative: str):
    return normalize_text_input(narrative)

@app.post("/ingest/csv", response_model=List[NarrativeRecord])
def ingest_csv(file: UploadFile = File(...)):
    return normalize_csv(file)

@app.post("/ingest/pdf", response_model=List[NarrativeRecord])
def ingest_pdf(file: UploadFile = File(...)):
    return normalize_pdf(file)

@app.post("/encode", response_model=List[EncodedNarrative])
def encode(records: List[NarrativeRecord]):
    return [encode_narrative(r) for r in records]

@app.post("/simulate", response_model=SimulationResult)
def simulate(req: SimulationRequest):
    trajectory = []
    value = 0.1
    for t in range(req.horizon_days):
        value = min(1.0, value + 0.002)
        trajectory.append({"day": t, "adoption": value})

    return SimulationResult(
        model_mode=req.model_mode,
        trajectory=trajectory,
        assumptions={"note": "placeholder model"},
    )

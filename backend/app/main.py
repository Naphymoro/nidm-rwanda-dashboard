from fastapi import FastAPI, UploadFile, File, Depends
from typing import List
from sqlalchemy.orm import Session

from .schemas import NarrativeRecord, SimulationRequest, SimulationResult, EncodedNarrative
from .ingestion import normalize_text_input, normalize_csv, normalize_pdf
from .encoding import encode_narrative
from .database import Base, engine, get_db
from . import models
from .evaluation import evaluate_encoding, evaluate_simulation, EncodingEvaluationRequest, SimulationEvaluationRequest
from .modelling import run_digital_twin
from .pipeline import run_experiment_pipeline

Base.metadata.create_all(bind=engine)

app = FastAPI(title="NIDM API", version="0.7")

@app.get("/")
def root():
    return {"message": "NIDM backend running"}

@app.post("/ingest/text", response_model=List[NarrativeRecord])
def ingest_text(narrative: str, db: Session = Depends(get_db)):
    records = normalize_text_input(narrative)
    for r in records:
        db.add(models.Narrative(
            id=r.narrative_id,
            text=r.text,
            country=r.metadata.country,
            admin_unit=r.metadata.admin_unit,
            source_type=r.metadata.source_type,
        ))
    db.commit()
    return records

@app.post("/ingest/csv", response_model=List[NarrativeRecord])
def ingest_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    records = normalize_csv(file)
    for r in records:
        db.add(models.Narrative(
            id=r.narrative_id,
            text=r.text,
            country=r.metadata.country,
            admin_unit=r.metadata.admin_unit,
            source_type=r.metadata.source_type,
        ))
    db.commit()
    return records

@app.post("/ingest/pdf", response_model=List[NarrativeRecord])
def ingest_pdf(file: UploadFile = File(...), db: Session = Depends(get_db)):
    records = normalize_pdf(file)
    for r in records:
        db.add(models.Narrative(
            id=r.narrative_id,
            text=r.text,
            country=r.metadata.country,
            admin_unit=r.metadata.admin_unit,
            source_type=r.metadata.source_type,
        ))
    db.commit()
    return records

@app.post("/encode", response_model=List[EncodedNarrative])
def encode(records: List[NarrativeRecord], db: Session = Depends(get_db)):
    encoded = [encode_narrative(r) for r in records]
    for e in encoded:
        db.add(models.Encoding(
            narrative_id=e.narrative_id,
            themes=e.themes,
            sentiment=e.sentiment,
            adoption_barrier_score=e.adoption_barrier_score,
            trust_score=e.trust_score,
            confidence=e.confidence,
        ))
    db.commit()
    return encoded

@app.post("/simulate", response_model=SimulationResult)
def simulate(req: SimulationRequest, db: Session = Depends(get_db)):
    trajectory = run_digital_twin(req.model_mode, req.horizon_days, req.parameters)

    result = SimulationResult(
        model_mode=req.model_mode,
        trajectory=trajectory,
        assumptions={"note": "narrative-coupled digital twin"},
    )

    db.add(models.SimulationRun(
        model_mode=req.model_mode,
        parameters=req.parameters,
        result=trajectory,
    ))
    db.commit()

    return result

@app.post("/pipeline/run")
def run_pipeline(records: List[NarrativeRecord]):
    return run_experiment_pipeline(records)

@app.post("/evaluate/encoding")
def eval_encoding(req: EncodingEvaluationRequest):
    return evaluate_encoding(req)

@app.post("/evaluate/simulation")
def eval_simulation(req: SimulationEvaluationRequest):
    return evaluate_simulation(req)

@app.get("/narratives")
def get_narratives(db: Session = Depends(get_db)):
    return db.query(models.Narrative).all()

@app.get("/encodings")
def get_encodings(db: Session = Depends(get_db)):
    return db.query(models.Encoding).all()

@app.get("/simulations")
def get_simulations(db: Session = Depends(get_db)):
    return db.query(models.SimulationRun).all()

from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from typing import List
from sqlalchemy.orm import Session

from .schemas import EncodingMode, NarrativeRecord, SimulationRequest, SimulationResult, EncodedNarrative
from .ingestion import normalize_text_input, normalize_csv, normalize_pdf
from .encoding import encode_narrative
from .database import Base, engine, get_db
from . import models
from .evaluation import evaluate_encoding, evaluate_simulation, EncodingEvaluationRequest, SimulationEvaluationRequest
from .modelling import run_digital_twin
from .pipeline import run_experiment_pipeline
from .workflow_ui import MANUAL_HTML, WORKFLOW_UI_HTML

try:
    from .api_routes import router as analytics_router
    analytics_import_error = None
except ImportError as exc:
    analytics_router = None
    analytics_import_error = str(exc)

try:
    import multipart  # type: ignore  # noqa: F401
    multipart_available = True
except ImportError:
    multipart_available = False

Base.metadata.create_all(bind=engine)

app = FastAPI(title="NDIM Engine API", version="0.8")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if analytics_router:
    app.include_router(analytics_router, prefix="/analytics", tags=["analytics"])

@app.get("/", response_class=HTMLResponse)
def root():
    return HTMLResponse(
        WORKFLOW_UI_HTML,
        headers={
            "Cache-Control": "no-store, max-age=0",
            "Pragma": "no-cache",
        },
    )

@app.get("/api/status")
def api_status():
    return {"message": "NDIM Engine backend running"}

@app.get("/manual", response_class=HTMLResponse)
def manual():
    return HTMLResponse(
        MANUAL_HTML,
        headers={
            "Cache-Control": "no-store, max-age=0",
            "Pragma": "no-cache",
        },
    )

@app.get("/analytics/status")
def analytics_status():
    if analytics_router:
        return {"available": True}
    return {
        "available": False,
        "reason": analytics_import_error or "advanced analytics dependencies are unavailable",
    }

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

if multipart_available:
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
else:
    @app.post("/ingest/csv")
    def ingest_csv_unavailable():
        raise HTTPException(
            status_code=503,
            detail="CSV upload requires python-multipart. Use the React SDMX upload gate or install backend requirements.",
        )

    @app.post("/ingest/pdf")
    def ingest_pdf_unavailable():
        raise HTTPException(
            status_code=503,
            detail="PDF upload requires python-multipart. Use text ingestion or install backend requirements.",
        )

@app.post("/encode", response_model=List[EncodedNarrative])
def encode(
    records: List[NarrativeRecord],
    mode: EncodingMode = EncodingMode.ai,
    provider: str = "openai",
    db: Session = Depends(get_db),
):
    encoded = [encode_narrative(r, mode=mode) for r in records]
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
def run_pipeline(records: List[NarrativeRecord], mode: EncodingMode = EncodingMode.ai, provider: str = "openai"):
    return run_experiment_pipeline(records, encoding_mode=mode)

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

from datetime import datetime, timezone
import os
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from .schemas import EncodingMode, NarrativeRecord, SimulationRequest, SimulationResult, EncodedNarrative, InoculationEncoding
from .ingestion import normalize_text_input, normalize_csv, normalize_pdf
from .encoding import encode_narrative, llm_provider_status, supported_llm_providers
from .inoculation import diagnose_inoculation
from .database import Base, engine, get_db
from . import models
from .evaluation import evaluate_encoding, evaluate_simulation, EncodingEvaluationRequest, SimulationEvaluationRequest
from .modelling import model_assumptions, run_digital_twin
from .pipeline import run_experiment_pipeline
from .storage import app_paths, diagnostics, ensure_app_dirs, make_full_backup, make_support_bundle, resource_path
from .validation import VALIDATION_DATASET, evaluate_encoder_against_validation, validation_status
from .workflow_ui import MANUAL_HTML, WORKFLOW_UI_HTML

if os.getenv("NDIM_DESKTOP") == "1" or os.getenv("NDIM_DATA_DIR"):
    ensure_app_dirs()

STRESS_TEST_INSTRUCTIONS_PATH = resource_path("docs", "ndim_stress_test_corpus_instructions.html")

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


@app.get("/desktop/paths")
def desktop_paths():
    return {
        "paths": {key: str(value) for key, value in app_paths().items()},
        "diagnostics": diagnostics(create_dirs=False),
    }


@app.get("/desktop/support-bundle")
def desktop_support_bundle():
    bundle = make_support_bundle()
    return FileResponse(bundle, media_type="application/zip", filename=bundle.name)


@app.get("/desktop/full-backup")
def desktop_full_backup():
    bundle = make_full_backup()
    return FileResponse(bundle, media_type="application/zip", filename=bundle.name)

@app.get("/manual", response_class=HTMLResponse)
def manual():
    return HTMLResponse(
        MANUAL_HTML,
        headers={
            "Cache-Control": "no-store, max-age=0",
            "Pragma": "no-cache",
        },
    )

@app.get("/stress-test-corpus")
def stress_test_corpus():
    return RedirectResponse(url="/manual#stress-test-corpus", status_code=307)

@app.get("/analytics/status")
def analytics_status():
    if analytics_router:
        return {"available": True}
    return {
        "available": False,
        "reason": analytics_import_error or "advanced analytics dependencies are unavailable",
    }


@app.get("/llm/providers")
def llm_providers(provider: str = "openai"):
    return {
        "providers": supported_llm_providers(),
        "status": llm_provider_status(provider),
        "secret_policy": "API keys may be supplied per request via X-NDIM-LLM-Key. Secrets are not returned by this endpoint.",
    }


def _now():
    return datetime.now(timezone.utc).isoformat()


@app.post("/ledger/sync")
def sync_ledger(payload: Dict[str, Any], db: Session = Depends(get_db)):
    records = payload.get("records", [])
    ledger = payload.get("ledger", [])
    project = payload.get("project", {})
    settings = payload.get("settings", {})
    synced = 0
    for item in records:
        narrative_id = item.get("narrative_id")
        if not narrative_id:
            continue
        route_metadata = {
            key: item.get(key)
            for key in [
                "question_id",
                "knowledge_type",
                "knowledge_holder",
                "community_validation",
                "attribution",
                "location_precision",
                "contributor_type",
                "feed_sources",
                "citizen_confidence",
                "validation_status",
            ]
            if item.get(key) not in (None, "")
        }
        existing = db.get(models.EvidenceLedgerRecord, narrative_id)
        uncommit_history = existing.uncommit_history if existing and isinstance(existing.uncommit_history, list) else []
        governance = {
            "scan": item.get("scan"),
            "reviewer_signature": item.get("reviewer_signature"),
            "repository_mode": item.get("repository_mode"),
            "batch_digest": payload.get("batch_digest"),
            "master_repository": {
                "status": item.get("master_repository_status"),
                "anchor_hash": item.get("master_anchor_hash"),
                "event_hash": item.get("master_event_hash"),
                "decision_hash": item.get("master_decision_hash"),
                "reviewer": item.get("master_reviewer"),
                "reviewed_at": item.get("master_reviewed_at"),
                "blockchain_status": item.get("master_blockchain_status"),
                "package": payload.get("master_repository"),
            },
        }
        record = models.EvidenceLedgerRecord(
            narrative_id=narrative_id,
            text=item.get("text") or "",
            evidence_route=item.get("evidence_mode") or project.get("evidence_mode"),
            evidence_route_label=item.get("evidence_mode_label") or project.get("evidence_mode_label"),
            country=item.get("country") or project.get("country"),
            admin_unit=item.get("admin_unit") or project.get("admin_unit"),
            admin_path=project.get("admin_unit"),
            source_type=project.get("source_type"),
            source_name=item.get("source_name") or project.get("source_name"),
            language=project.get("language"),
            period=project.get("period"),
            consent_tier=item.get("consent") or settings.get("consent"),
            visibility_tier=item.get("visibility") or settings.get("visibility"),
            sensitivity_level=item.get("sensitivity"),
            content_hash=item.get("content_hash"),
            evidence_hash=item.get("evidence_hash"),
            review_status=item.get("status") or "pending_review",
            reviewer_name=item.get("reviewer") or settings.get("reviewer"),
            reviewer_role=settings.get("reviewer_role"),
            review_reason=item.get("review_reason"),
            repository_bucket=item.get("repository_bucket"),
            committed_at=item.get("committed_at"),
            uncommit_history=uncommit_history,
            route_metadata=route_metadata,
            governance=governance,
            created_at=existing.created_at if existing and existing.created_at else _now(),
            updated_at=_now(),
        )
        if existing and item.get("status") == "pending_review" and existing.review_status in {"accepted_committed", "rejected_committed"}:
            uncommit_history.append({"at": _now(), "from_status": existing.review_status, "reason": "synced uncommit"})
            record.uncommit_history = uncommit_history
        db.merge(record)
        synced += 1
    for event in ledger:
        event_hash = event.get("event_hash")
        if not event_hash or db.query(models.GovernanceLedgerEvent).filter_by(event_hash=event_hash).first():
            continue
        db.add(
            models.GovernanceLedgerEvent(
                event_hash=event_hash,
                previous_hash=event.get("previous_hash"),
                action=event.get("action"),
                detail=event.get("detail"),
                target_hash=event.get("target_hash"),
                actor=event.get("actor"),
                role=event.get("role"),
                occurred_at=event.get("at") or _now(),
                payload=event,
            )
        )
    db.commit()
    counts = {
        "active_review": db.query(models.EvidenceLedgerRecord).filter(~models.EvidenceLedgerRecord.review_status.in_(["approved_pending_commit", "rejected_pending_commit", "accepted_committed", "rejected_committed"])).count(),
        "pending_commit": db.query(models.EvidenceLedgerRecord).filter(models.EvidenceLedgerRecord.review_status.in_(["approved_pending_commit", "rejected_pending_commit"])).count(),
        "accepted": db.query(models.EvidenceLedgerRecord).filter_by(review_status="accepted_committed").count(),
        "rejected": db.query(models.EvidenceLedgerRecord).filter_by(review_status="rejected_committed").count(),
    }
    return {"synced_records": synced, "repository_counts": counts}


@app.get("/ledger/records")
def ledger_records(db: Session = Depends(get_db)):
    rows = db.query(models.EvidenceLedgerRecord).order_by(models.EvidenceLedgerRecord.updated_at.desc()).all()
    output = []
    for row in rows:
        master = {}
        if isinstance(row.governance, dict):
            master = row.governance.get("master_repository") or {}
        output.append(
            {
                "narrative_id": row.narrative_id,
                "evidence_route": row.evidence_route,
                "evidence_route_label": row.evidence_route_label,
                "country": row.country,
                "admin_unit": row.admin_unit,
                "source_name": row.source_name,
                "review_status": row.review_status,
                "repository_bucket": row.repository_bucket,
                "evidence_hash": row.evidence_hash,
                "consent_tier": row.consent_tier,
                "visibility_tier": row.visibility_tier,
                "sensitivity_level": row.sensitivity_level,
                "master_repository_status": master.get("status"),
                "master_anchor_hash": master.get("anchor_hash"),
                "master_decision_hash": master.get("decision_hash"),
                "master_blockchain_status": master.get("blockchain_status"),
                "updated_at": row.updated_at,
            }
        )
    return output


@app.get("/validation/status")
def get_validation_status():
    return validation_status()


@app.get("/validation/dataset")
def get_validation_dataset():
    return {"records": VALIDATION_DATASET}


@app.post("/validation/evaluate")
def evaluate_validation(predictions: List[Dict[str, Any]]):
    return evaluate_encoder_against_validation(predictions)


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
    x_ndim_llm_key: Optional[str] = Header(default=None, alias="X-NDIM-LLM-Key"),
    x_ndim_llm_provider: Optional[str] = Header(default=None, alias="X-NDIM-LLM-Provider"),
    x_ndim_llm_base_url: Optional[str] = Header(default=None, alias="X-NDIM-LLM-Base-URL"),
    x_ndim_llm_model: Optional[str] = Header(default=None, alias="X-NDIM-LLM-Model"),
    db: Session = Depends(get_db),
):
    selected_provider = x_ndim_llm_provider or provider
    encoded = [
        encode_narrative(
            r,
            mode=mode,
            provider=selected_provider,
            api_key=x_ndim_llm_key,
            base_url=x_ndim_llm_base_url,
            model=x_ndim_llm_model,
        )
        for r in records
    ]
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

@app.post("/inoculate", response_model=List[InoculationEncoding])
def inoculate(
    records: List[NarrativeRecord],
    provider: str = "openai",
    x_ndim_llm_key: Optional[str] = Header(default=None, alias="X-NDIM-LLM-Key"),
    x_ndim_llm_provider: Optional[str] = Header(default=None, alias="X-NDIM-LLM-Provider"),
    x_ndim_llm_base_url: Optional[str] = Header(default=None, alias="X-NDIM-LLM-Base-URL"),
    x_ndim_llm_model: Optional[str] = Header(default=None, alias="X-NDIM-LLM-Model"),
    db: Session = Depends(get_db),
):
    selected_provider = x_ndim_llm_provider or provider
    diagnoses = [
        diagnose_inoculation(
            record,
            provider=selected_provider,
            api_key=x_ndim_llm_key,
            base_url=x_ndim_llm_base_url,
            model=x_ndim_llm_model,
        )
        for record in records
    ]
    for item in diagnoses:
        db.add(
            models.InoculationDiagnosis(
                narrative_id=item.narrative_id,
                diagnosis_mode=item.diagnosis_mode,
                threat_type=item.threat_type,
                misinformation_mechanism=item.misinformation_mechanism,
                source_actor=item.source_actor,
                susceptible_group=item.susceptible_group,
                trusted_messenger=item.trusted_messenger,
                scores={
                    "threat_recognition": item.threat_recognition_score,
                    "misinformation_risk": item.misinformation_risk_score,
                    "identity_threat": item.identity_threat_score,
                    "reactance_risk": item.reactance_risk_score,
                    "cultural_sensitivity": item.cultural_sensitivity_score,
                    "refutability": item.refutability_score,
                    "trusted_messenger_fit": item.trusted_messenger_fit_score,
                    "narrative_resilience": item.narrative_resilience_score,
                },
                intervention_parameters=item.intervention_parameters,
                evidence_spans=item.evidence_spans,
                counter_narrative=item.counter_narrative,
                booster_strategy=item.booster_strategy,
                booster_needed="yes" if item.booster_needed else "no",
                confidence=item.confidence,
            )
        )
    db.commit()
    return diagnoses

@app.post("/simulate", response_model=SimulationResult)
def simulate(req: SimulationRequest, db: Session = Depends(get_db)):
    trajectory = run_digital_twin(req.model_mode, req.horizon_days, req.parameters)
    result = SimulationResult(
        model_mode=req.model_mode,
        trajectory=trajectory,
        assumptions=model_assumptions(req.model_mode, req.parameters),
    )
    db.add(models.SimulationRun(
        model_mode=req.model_mode,
        parameters=req.parameters,
        result=trajectory,
    ))
    db.commit()
    return result

@app.post("/pipeline/run")
def run_pipeline(
    records: List[NarrativeRecord],
    mode: EncodingMode = EncodingMode.ai,
    provider: str = "openai",
    x_ndim_llm_key: Optional[str] = Header(default=None, alias="X-NDIM-LLM-Key"),
    x_ndim_llm_provider: Optional[str] = Header(default=None, alias="X-NDIM-LLM-Provider"),
    x_ndim_llm_base_url: Optional[str] = Header(default=None, alias="X-NDIM-LLM-Base-URL"),
    x_ndim_llm_model: Optional[str] = Header(default=None, alias="X-NDIM-LLM-Model"),
):
    return run_experiment_pipeline(
        records,
        encoding_mode=mode,
        provider=x_ndim_llm_provider or provider,
        api_key=x_ndim_llm_key,
        base_url=x_ndim_llm_base_url,
        model=x_ndim_llm_model,
    )

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

@app.get("/inoculations")
def get_inoculations(db: Session = Depends(get_db)):
    return db.query(models.InoculationDiagnosis).all()

@app.get("/simulations")
def get_simulations(db: Session = Depends(get_db)):
    return db.query(models.SimulationRun).all()

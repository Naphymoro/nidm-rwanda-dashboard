from collections import Counter
from datetime import datetime, timezone
from typing import Dict, List

from sqlalchemy.orm import Session

from . import models

RETRAIN_THRESHOLD = 25


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def record_feedback(db: Session, payload: Dict) -> Dict:
    feedback = models.LearningFeedback(
        decision=payload.get("decision", "unspecified"),
        outcome=payload.get("outcome", "helpful"),
        note=payload.get("note", ""),
        context=payload.get("context", {}),
        created_at=_now_iso(),
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return {
        "id": feedback.id,
        "decision": feedback.decision,
        "outcome": feedback.outcome,
        "note": feedback.note,
        "context": feedback.context,
        "created_at": feedback.created_at,
    }


def learning_state(db: Session) -> Dict:
    rows: List[models.LearningFeedback] = db.query(models.LearningFeedback).all()
    counts = Counter([r.outcome for r in rows])
    total = len(rows)
    costly = counts.get("too_costly", 0)
    aggressive = counts.get("too_aggressive", 0)
    needs_data = counts.get("needs_data", 0)

    cost_caution = min(0.25, costly * 0.03)
    aggression_caution = min(0.20, aggressive * 0.025)
    data_caution = needs_data > 0
    retrain_ready = total >= RETRAIN_THRESHOLD or needs_data >= 5

    return {
        "feedback_count": total,
        "outcome_counts": dict(counts),
        "learning_adjustment": {
            "cost_caution": cost_caution,
            "aggression_caution": aggression_caution,
            "data_caution": data_caution,
        },
        "retraining": {
            "ready": retrain_ready,
            "threshold": RETRAIN_THRESHOLD,
            "remaining_feedback_items": max(0, RETRAIN_THRESHOLD - total),
            "reason": "enough feedback or repeated data-quality concerns" if retrain_ready else "not enough feedback yet",
        },
    }


def create_retraining_job(db: Session, reason: str = "manual_review") -> Dict:
    state = learning_state(db)
    job = models.RetrainingJob(
        status="queued" if state["retraining"]["ready"] else "blocked",
        reason=reason,
        metrics=state,
        created_at=_now_iso(),
        completed_at=None,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return {
        "id": job.id,
        "status": job.status,
        "reason": job.reason,
        "metrics": job.metrics,
        "created_at": job.created_at,
        "completed_at": job.completed_at,
        "note": "Queued for human-reviewed retraining." if job.status == "queued" else "Retraining blocked until enough evidence accumulates.",
    }


def complete_retraining_job(db: Session, job_id: int, metrics: Dict | None = None) -> Dict:
    job = db.query(models.RetrainingJob).filter(models.RetrainingJob.id == job_id).first()
    if job is None:
        raise ValueError("Retraining job not found")
    job.status = "completed"
    job.completed_at = _now_iso()
    job.metrics = {**(job.metrics or {}), "completion_metrics": metrics or {}}
    db.commit()
    db.refresh(job)
    return {
        "id": job.id,
        "status": job.status,
        "reason": job.reason,
        "metrics": job.metrics,
        "created_at": job.created_at,
        "completed_at": job.completed_at,
    }

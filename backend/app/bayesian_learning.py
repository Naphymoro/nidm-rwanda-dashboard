from datetime import datetime, timezone
from typing import Dict

from sqlalchemy.orm import Session

from . import models


def _now():
    return datetime.now(timezone.utc).isoformat()


def default_priors():
    return {
        "beta": {"mean": 0.30, "std": 0.05},
        "gamma": {"mean": 0.20, "std": 0.05},
        "delta": {"mean": 0.10, "std": 0.03},
    }


def get_latest_priors(db: Session) -> Dict:
    row = (
        db.query(models.BayesianPriorState)
        .order_by(models.BayesianPriorState.version.desc())
        .first()
    )
    return row.priors if row else default_priors()


def update_priors_from_feedback(db: Session) -> Dict:
    feedback = db.query(models.LearningFeedback).all()
    priors = get_latest_priors(db)

    # Aggregate signals
    cost_flags = sum(1 for f in feedback if f.outcome == "too_costly")
    aggressive_flags = sum(1 for f in feedback if f.outcome == "too_aggressive")
    helpful_flags = sum(1 for f in feedback if f.outcome == "helpful")

    # Bayesian-style heuristic update (posterior shift)
    # Cost concerns -> reduce gamma (intervention effectiveness assumption)
    priors["gamma"]["mean"] *= (1 - min(0.2, cost_flags * 0.02))

    # Aggression concerns -> increase delta (resistance)
    priors["delta"]["mean"] *= (1 + min(0.25, aggressive_flags * 0.03))

    # Helpful feedback -> strengthen beta slightly (confidence in diffusion)
    priors["beta"]["mean"] *= (1 + min(0.15, helpful_flags * 0.01))

    # Clamp bounds
    priors["beta"]["mean"] = max(0.05, min(1.0, priors["beta"]["mean"]))
    priors["gamma"]["mean"] = max(0.01, min(1.0, priors["gamma"]["mean"]))
    priors["delta"]["mean"] = max(0.001, min(1.0, priors["delta"]["mean"]))

    # Store new version
    latest = db.query(models.BayesianPriorState).order_by(models.BayesianPriorState.version.desc()).first()
    next_version = (latest.version + 1) if latest else 1

    record = models.BayesianPriorState(
        country="global",
        version=next_version,
        priors=priors,
        evidence_summary={
            "cost_flags": cost_flags,
            "aggressive_flags": aggressive_flags,
            "helpful_flags": helpful_flags,
        },
        created_at=_now(),
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return {
        "version": record.version,
        "priors": record.priors,
        "evidence": record.evidence_summary,
    }

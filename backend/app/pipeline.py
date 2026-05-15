from typing import Dict, List

from .encoding import encode_narrative
from .modelling import model_assumptions, run_digital_twin
from .schemas import EncodedNarrative, EncodingMode, ModelMode, NarrativeRecord


def aggregate_encoding_parameters(encoded: List[EncodedNarrative]) -> Dict[str, float]:
    if not encoded:
        return {
            "trust_score": 0.60,
            "barrier_score": 0.35,
            "narrative_influence": 0.35,
            "intervention_strength": 0.15,
        }

    trust_values = [e.trust_score for e in encoded if e.trust_score is not None]
    barrier_values = [e.adoption_barrier_score for e in encoded if e.adoption_barrier_score is not None]
    confidence_values = [e.confidence for e in encoded if e.confidence is not None]

    trust = sum(trust_values) / len(trust_values) if trust_values else 0.60
    barrier = sum(barrier_values) / len(barrier_values) if barrier_values else 0.35
    confidence = sum(confidence_values) / len(confidence_values) if confidence_values else 0.50

    return {
        "trust_score": trust,
        "barrier_score": barrier,
        "narrative_influence": 0.20 + 0.35 * confidence,
        "intervention_strength": 0.10 + 0.20 * trust,
        "confidence": confidence,
        "evidence_strength": confidence,
    }


def evidence_grade(records: List[NarrativeRecord], encoded: List[EncodedNarrative]) -> Dict[str, str | float]:
    count = len(records)
    confidence = sum((item.confidence or 0.0) for item in encoded) / len(encoded) if encoded else 0.0
    if count >= 20 and confidence >= 0.70:
        grade = "B"
        readiness = "policy_use_with_review"
    elif count >= 5 and confidence >= 0.55:
        grade = "C"
        readiness = "pilot_or_targeted_policy_only"
    else:
        grade = "D"
        readiness = "do_not_use_for_policy_yet"
    return {
        "grade": grade,
        "readiness": readiness,
        "accepted_records": float(count),
        "mean_encoder_confidence": confidence,
        "warning": "" if grade in {"B", "C"} else "Evidence is thin or low-confidence; use for learning, not final policy decisions.",
    }


def run_experiment_pipeline(
    records: List[NarrativeRecord],
    model_mode: ModelMode = ModelMode.hybrid,
    encoding_mode: EncodingMode = EncodingMode.ai,
    horizon_days: int = 180,
    provider: str = "openai",
    api_key: str | None = None,
    base_url: str | None = None,
    model: str | None = None,
) -> Dict:
    encoded = [
        encode_narrative(
            record,
            mode=encoding_mode,
            provider=provider,
            api_key=api_key,
            base_url=base_url,
            model=model,
        )
        for record in records
    ]
    parameters = aggregate_encoding_parameters(encoded)
    trajectory = run_digital_twin(model_mode, horizon_days, parameters)
    grade = evidence_grade(records, encoded)

    return {
        "narrative_count": len(records),
        "encoded": [e.model_dump() for e in encoded],
        "parameters": parameters,
        "model_mode": model_mode,
        "assumptions": model_assumptions(model_mode, parameters),
        "trajectory": trajectory,
        "summary": {
            "final_adoption": trajectory[-1]["adoption"] if trajectory else 0.0,
            "average_trust": parameters["trust_score"],
            "average_barrier": parameters["barrier_score"],
            "evidence_grade": grade["grade"],
            "policy_readiness": grade["readiness"],
            "evidence_warning": grade["warning"],
        },
    }

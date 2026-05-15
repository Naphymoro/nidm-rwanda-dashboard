from typing import Dict, List

from .encoding import encode_narrative
from .inoculation import aggregate_inoculation_parameters, diagnose_inoculation
from .modelling import model_assumptions, run_digital_twin
from .schemas import EncodedNarrative, EncodingMode, InoculationEncoding, ModelMode, NarrativeRecord


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


def apply_inoculation_parameters(parameters: Dict[str, float], diagnoses: List[InoculationEncoding]) -> Dict[str, float]:
    if not diagnoses:
        return parameters
    inoculation = aggregate_inoculation_parameters(diagnoses)
    updated = {**parameters}
    updated["misinformation_risk"] = inoculation.get("misinformation_risk", 0.0)
    updated["reactance_penalty"] = inoculation.get("reactance_penalty", 0.0)
    updated["trusted_messenger_fit"] = inoculation.get("trusted_messenger_fit", 0.0)
    updated["recommended_inoculation_strength"] = inoculation.get("inoculation_strength", 0.0)
    updated["misinformation_decay"] = inoculation.get("misinformation_decay", 0.0)
    updated["resistance_growth"] = inoculation.get("resistance_growth", 0.0)
    updated["trust_score"] = min(1.0, max(0.0, updated.get("trust_score", 0.60) + inoculation.get("trust_shift", 0.0) * 0.35))
    updated["barrier_score"] = min(1.0, max(0.0, updated.get("barrier_score", 0.35) + inoculation.get("barrier_shift", 0.0) * 0.35))
    return updated


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
    diagnoses = [
        diagnose_inoculation(
            record,
            encoded[index] if index < len(encoded) else None,
            provider=provider,
            api_key=api_key,
            base_url=base_url,
            model=model,
        )
        for index, record in enumerate(records)
    ]
    parameters = apply_inoculation_parameters(aggregate_encoding_parameters(encoded), diagnoses)
    trajectory = run_digital_twin(model_mode, horizon_days, parameters)
    grade = evidence_grade(records, encoded)
    inoculation_summary = aggregate_inoculation_parameters(diagnoses)

    return {
        "narrative_count": len(records),
        "encoded": [e.model_dump() for e in encoded],
        "inoculation_diagnoses": [item.model_dump() for item in diagnoses],
        "inoculation_summary": inoculation_summary,
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
            "mean_inoculation_strength": inoculation_summary.get("inoculation_strength", 0.0),
            "mean_misinformation_risk": inoculation_summary.get("misinformation_risk", 0.0),
            "booster_share": inoculation_summary.get("booster_share", 0.0),
        },
    }

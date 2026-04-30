from typing import Dict, List

from .encoding import encode_narrative
from .modelling import run_digital_twin
from .schemas import EncodedNarrative, ModelMode, NarrativeRecord


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
    }


def run_experiment_pipeline(
    records: List[NarrativeRecord],
    model_mode: ModelMode = ModelMode.hybrid,
    horizon_days: int = 180,
) -> Dict:
    encoded = [encode_narrative(record) for record in records]
    parameters = aggregate_encoding_parameters(encoded)
    trajectory = run_digital_twin(model_mode, horizon_days, parameters)

    return {
        "narrative_count": len(records),
        "encoded": [e.model_dump() for e in encoded],
        "parameters": parameters,
        "model_mode": model_mode,
        "trajectory": trajectory,
        "summary": {
            "final_adoption": trajectory[-1]["adoption"] if trajectory else 0.0,
            "average_trust": parameters["trust_score"],
            "average_barrier": parameters["barrier_score"],
        },
    }

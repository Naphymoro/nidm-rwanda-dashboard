from typing import Dict, List
from .schemas import ModelMode


def run_compartmental_model(horizon_days: int, parameters: Dict[str, float]) -> List[Dict[str, float]]:
    adoption = float(parameters.get("initial_adoption", 0.10))
    influence = float(parameters.get("narrative_influence", 0.35))
    trust = float(parameters.get("trust_score", 0.60))
    barrier = float(parameters.get("barrier_score", 0.35))
    intervention = float(parameters.get("intervention_strength", 0.15))

    trajectory = []
    for day in range(horizon_days):
        social_push = influence * trust * adoption * (1.0 - adoption)
        policy_push = intervention * (1.0 - barrier) * (1.0 - adoption)
        resistance = barrier * 0.03 * adoption
        adoption = max(0.0, min(1.0, adoption + social_push + policy_push - resistance))
        trajectory.append({"day": float(day), "adoption": adoption})
    return trajectory


def run_agent_based_proxy(horizon_days: int, parameters: Dict[str, float]) -> List[Dict[str, float]]:
    adoption = float(parameters.get("initial_adoption", 0.10))
    trust = float(parameters.get("trust_score", 0.60))
    barrier = float(parameters.get("barrier_score", 0.35))
    peer_effect = float(parameters.get("peer_effect", 0.08))
    media_effect = float(parameters.get("media_effect", 0.05))

    trajectory = []
    for day in range(horizon_days):
        local_contact = peer_effect * adoption * (1.0 - adoption)
        media_contact = media_effect * trust * (1.0 - adoption)
        friction = barrier * 0.025
        adoption = max(0.0, min(1.0, adoption + local_contact + media_contact - friction * adoption))
        trajectory.append({"day": float(day), "adoption": adoption})
    return trajectory


def run_hybrid_model(horizon_days: int, parameters: Dict[str, float]) -> List[Dict[str, float]]:
    comp = run_compartmental_model(horizon_days, parameters)
    abm = run_agent_based_proxy(horizon_days, parameters)
    return [
        {
            "day": comp[i]["day"],
            "adoption": 0.55 * comp[i]["adoption"] + 0.45 * abm[i]["adoption"],
        }
        for i in range(horizon_days)
    ]


def run_digital_twin(model_mode: ModelMode, horizon_days: int, parameters: Dict[str, float]) -> List[Dict[str, float]]:
    if model_mode == ModelMode.compartmental:
        return run_compartmental_model(horizon_days, parameters)
    if model_mode == ModelMode.agent_based:
        return run_agent_based_proxy(horizon_days, parameters)
    return run_hybrid_model(horizon_days, parameters)

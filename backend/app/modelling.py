from typing import Dict, List
from .schemas import ModelMode


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def _normalize_compartments(state: Dict[str, float]) -> Dict[str, float]:
    total = sum(max(0.0, value) for value in state.values()) or 1.0
    return {key: max(0.0, value) / total for key, value in state.items()}


def run_prototype_adoption_curve(horizon_days: int, parameters: Dict[str, float]) -> List[Dict[str, float]]:
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


def run_compartmental_model(horizon_days: int, parameters: Dict[str, float]) -> List[Dict[str, float]]:
    """Run the documented NDIM S/M/T/I/R compartment system.

    Compartments are normalized proportions:
    S susceptible, M misinformed, T truth-aligned, I inoculated, R durable
    adoption/resistance. The policy-facing adoption signal is T + I + R.
    """
    trust = _clamp(float(parameters.get("trust_score", 0.60)))
    barrier = _clamp(float(parameters.get("barrier_score", 0.35)))
    phi = _clamp(float(parameters.get("narrative_influence", parameters.get("phi", 0.38))))
    intervention = _clamp(float(parameters.get("intervention_strength", 0.15)))
    inoculation_strength = _clamp(float(parameters.get("inoculation_strength", 0.0)))
    misinformation_risk = _clamp(float(parameters.get("misinformation_risk", 0.0)))
    misinformation_decay = _clamp(float(parameters.get("misinformation_decay", 0.0)))
    resistance_growth = _clamp(float(parameters.get("resistance_growth", 0.0)))
    reactance_penalty = _clamp(float(parameters.get("reactance_penalty", 0.0)))
    messenger_fit = _clamp(float(parameters.get("trusted_messenger_fit", 0.0)))
    initial_adoption = _clamp(float(parameters.get("initial_adoption", 0.10)))

    state = _normalize_compartments(
        {
            "S": float(parameters.get("S0", max(0.05, 0.72 - initial_adoption * 0.30))),
            "M": float(parameters.get("M0", 0.10 + barrier * 0.12 + misinformation_risk * 0.08)),
            "T": float(parameters.get("T0", max(0.02, initial_adoption * 0.50))),
            "I": float(parameters.get("I0", 0.04 + inoculation_strength * 0.08)),
            "R": float(parameters.get("R0", max(0.02, initial_adoption * 0.50))),
        }
    )

    beta_t = float(parameters.get("beta_t", 0.035 * (1.0 + phi) * (0.65 + trust)))
    beta_m = float(parameters.get("beta_m", 0.030 * (0.55 + barrier + misinformation_risk * 0.35 + reactance_penalty * 0.18)))
    iota = float(parameters.get("iota", 0.006 + 0.020 * intervention + 0.030 * inoculation_strength + 0.010 * messenger_fit))
    rho = float(parameters.get("rho", 0.010 + 0.020 * trust + 0.012 * intervention + 0.010 * messenger_fit))
    sigma = float(parameters.get("sigma", 0.008 + 0.020 * inoculation_strength + 0.018 * misinformation_decay))
    mu = float(parameters.get("mu", 0.004 + 0.010 * barrier))
    gamma = float(parameters.get("gamma", 0.008 + 0.018 * intervention + 0.012 * trust + 0.012 * resistance_growth))
    eta = float(parameters.get("eta", 0.006 + 0.012 * trust + 0.006 * resistance_growth))
    waning = float(parameters.get("waning", 0.001 + 0.004 * max(0.0, barrier - trust)))

    uncertainty = 0.035 + 0.10 * (1.0 - _clamp(float(parameters.get("evidence_strength", parameters.get("confidence", 0.50)))))
    trajectory: List[Dict[str, float]] = []
    for day in range(horizon_days):
        S, M, T, I, R = state["S"], state["M"], state["T"], state["I"], state["R"]
        dS = -beta_m * S * M - beta_t * S * T - iota * S + waning * (M + T)
        dM = beta_m * S * M - rho * M - sigma * M * max(I, 0.001)
        dT = beta_t * S * T + rho * M - mu * T - eta * T
        dI = iota * S + sigma * M * max(I, 0.001) - gamma * I
        dR = gamma * I + eta * T
        state = _normalize_compartments(
            {
                "S": S + dS,
                "M": M + dM,
                "T": T + dT,
                "I": I + dI,
                "R": R + dR,
            }
        )
        adoption = _clamp(state["T"] + state["I"] + state["R"])
        trajectory.append(
            {
                "day": float(day),
                **state,
                "adoption": adoption,
                "misinformation": state["M"],
                "truth_aligned": state["T"],
                "inoculated": state["I"],
                "resistant": state["R"],
                "adoption_lower": _clamp(adoption - uncertainty),
                "adoption_upper": _clamp(adoption + uncertainty),
                "inoculation_strength": inoculation_strength,
                "misinformation_risk": misinformation_risk,
                "reactance_penalty": reactance_penalty,
            }
        )
    return trajectory


def run_agent_based_proxy(horizon_days: int, parameters: Dict[str, float]) -> List[Dict[str, float]]:
    adoption = float(parameters.get("initial_adoption", 0.10))
    trust = float(parameters.get("trust_score", 0.60))
    barrier = float(parameters.get("barrier_score", 0.35))
    peer_effect = float(parameters.get("peer_effect", 0.08))
    media_effect = float(parameters.get("media_effect", 0.05))
    inoculation_strength = _clamp(float(parameters.get("inoculation_strength", 0.0)))
    misinformation_risk = _clamp(float(parameters.get("misinformation_risk", 0.0)))
    reactance_penalty = _clamp(float(parameters.get("reactance_penalty", 0.0)))
    messenger_fit = _clamp(float(parameters.get("trusted_messenger_fit", 0.0)))

    trajectory = []
    for day in range(horizon_days):
        local_contact = peer_effect * adoption * (1.0 - adoption)
        media_contact = (media_effect + inoculation_strength * 0.035 + messenger_fit * 0.020) * trust * (1.0 - adoption)
        friction = barrier * 0.025 + misinformation_risk * 0.008 + reactance_penalty * 0.010
        adoption = max(0.0, min(1.0, adoption + local_contact + media_contact - friction * adoption))
        uncertainty = 0.045 + 0.08 * (1.0 - _clamp(float(parameters.get("evidence_strength", parameters.get("confidence", 0.50)))))
        trajectory.append({
            "day": float(day),
            "adoption": adoption,
            "adoption_lower": _clamp(adoption - uncertainty),
            "adoption_upper": _clamp(adoption + uncertainty),
            "peer_pressure": local_contact,
            "media_pressure": media_contact,
            "inoculation_pressure": inoculation_strength,
            "reactance_penalty": reactance_penalty,
        })
    return trajectory


def run_hybrid_model(horizon_days: int, parameters: Dict[str, float]) -> List[Dict[str, float]]:
    comp = run_compartmental_model(horizon_days, parameters)
    abm = run_agent_based_proxy(horizon_days, parameters)
    return [
        {
            "day": comp[i]["day"],
            "adoption": 0.55 * comp[i]["adoption"] + 0.45 * abm[i]["adoption"],
            "adoption_lower": 0.55 * comp[i].get("adoption_lower", comp[i]["adoption"]) + 0.45 * abm[i].get("adoption_lower", abm[i]["adoption"]),
            "adoption_upper": 0.55 * comp[i].get("adoption_upper", comp[i]["adoption"]) + 0.45 * abm[i].get("adoption_upper", abm[i]["adoption"]),
            "S": comp[i].get("S", 0.0),
            "M": comp[i].get("M", 0.0),
            "T": comp[i].get("T", 0.0),
            "I": comp[i].get("I", 0.0),
            "R": comp[i].get("R", 0.0),
        }
        for i in range(horizon_days)
    ]


def run_digital_twin(model_mode: ModelMode, horizon_days: int, parameters: Dict[str, float]) -> List[Dict[str, float]]:
    if parameters.get("model_family") == "prototype_adoption_curve":
        return run_prototype_adoption_curve(horizon_days, parameters)
    if model_mode == ModelMode.compartmental:
        return run_compartmental_model(horizon_days, parameters)
    if model_mode == ModelMode.agent_based:
        return run_agent_based_proxy(horizon_days, parameters)
    return run_hybrid_model(horizon_days, parameters)


def model_assumptions(model_mode: ModelMode, parameters: Dict[str, float]) -> Dict[str, object]:
    if parameters.get("model_family") == "prototype_adoption_curve":
        model_type = "prototype adoption curve fallback"
        compartments = []
    elif model_mode == ModelMode.compartmental:
        model_type = "Full NDIM compartment model"
        compartments = ["S", "M", "T", "I", "R"]
    elif model_mode == ModelMode.agent_based:
        model_type = "Agent-based proxy"
        compartments = []
    else:
        model_type = "Hybrid NDIM model"
        compartments = ["S", "M", "T", "I", "R"]
    return {
        "model_type": model_type,
        "compartments": compartments,
        "note": "NDIM model outputs include uncertainty bands when evidence strength is available.",
        "parameters": parameters,
        "inoculation_link": {
            "inoculation_strength": parameters.get("inoculation_strength", 0.0),
            "recommended_inoculation_strength": parameters.get("recommended_inoculation_strength", 0.0),
            "misinformation_risk": parameters.get("misinformation_risk", 0.0),
            "reactance_penalty": parameters.get("reactance_penalty", 0.0),
            "trusted_messenger_fit": parameters.get("trusted_messenger_fit", 0.0),
            "note": "When supplied by /inoculate, these parameters connect narrative diagnosis to the digital twin and policy intervention tests.",
        },
    }

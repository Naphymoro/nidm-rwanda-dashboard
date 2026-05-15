from __future__ import annotations

import math
import random
from typing import Dict, List

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .database import get_db


router = APIRouter()


class ScenarioRequest(BaseModel):
    base_params: Dict[str, float]
    scenarios: Dict[str, Dict[str, float]]
    horizon: int = 180


class PriorSimulationRequest(BaseModel):
    horizon: int = 180
    initial_adoption: float = 0.1
    draws: int = 200


def _advanced_imports():
    try:
        from .bayesian import run_bayesian_inference, adoption_forward, simulate_with_priors
        from .bayesian_learning import get_latest_priors, update_priors_from_feedback
        from .calibration import calibrate_parameters
        from .hierarchical_bayes import fit_hierarchical_countries
        from .optimization import (
            POLICY_CATALOG,
            map_intervention_to_policy_package,
            multi_objective_optimization,
            optimize_policy,
            q_learning_policy,
        )
        return {
            "available": True,
            "error": "",
            "run_bayesian_inference": run_bayesian_inference,
            "adoption_forward": adoption_forward,
            "simulate_with_priors": simulate_with_priors,
            "get_latest_priors": get_latest_priors,
            "update_priors_from_feedback": update_priors_from_feedback,
            "calibrate_parameters": calibrate_parameters,
            "fit_hierarchical_countries": fit_hierarchical_countries,
            "POLICY_CATALOG": POLICY_CATALOG,
            "map_intervention_to_policy_package": map_intervention_to_policy_package,
            "multi_objective_optimization": multi_objective_optimization,
            "optimize_policy": optimize_policy,
            "q_learning_policy": q_learning_policy,
        }
    except Exception as exc:
        return {"available": False, "error": str(exc)}


def _adoption_forward_py(beta: float, gamma: float, delta: float, horizon: int = 50, initial_adoption: float = 0.1) -> List[float]:
    adoption = float(initial_adoption)
    values = []
    for _ in range(horizon):
        adoption += beta * adoption * (1 - adoption) + gamma * (1 - adoption) - delta * adoption
        adoption = max(0.0, min(1.0, adoption))
        values.append(adoption)
    return values


def _fallback_bayesian(data: List[float], priors: Dict | None = None) -> Dict:
    if not data:
        data = [0.1, 0.12, 0.15]
    start = float(data[0])
    end = float(data[-1])
    growth = max(0.0, end - start)
    defaults = priors or {
        "beta": {"mean": 0.30, "std": 0.05},
        "gamma": {"mean": 0.20, "std": 0.05},
        "delta": {"mean": 0.10, "std": 0.03},
    }
    beta_mean = max(0.01, float(defaults["beta"]["mean"]) + growth * 0.35)
    gamma_mean = max(0.01, float(defaults["gamma"]["mean"]) + growth * 0.20)
    delta_mean = max(0.001, float(defaults["delta"]["mean"]) - growth * 0.10)
    trajectory = _adoption_forward_py(beta_mean, gamma_mean, delta_mean, len(data), start)
    band = 0.08 + 0.03 * (1 / max(1, len(data)))
    return {
        "parameters": {
            "beta": {"mean": beta_mean, "std": 0.07, "q05": max(0.001, beta_mean - band), "q50": beta_mean, "q95": beta_mean + band},
            "gamma": {"mean": gamma_mean, "std": 0.06, "q05": max(0.001, gamma_mean - band), "q50": gamma_mean, "q95": gamma_mean + band},
            "delta": {"mean": delta_mean, "std": 0.04, "q05": max(0.001, delta_mean - band), "q50": delta_mean, "q95": delta_mean + band},
        },
        "trajectory": {
            "mean": trajectory,
            "lower_90": [max(0.0, value - band) for value in trajectory],
            "upper_90": [min(1.0, value + band) for value in trajectory],
        },
        "diagnostics": {
            "fallback": True,
            "warning": "Pyro/Torch unavailable. Used deterministic moment-based posterior approximation.",
            "horizon": len(data),
        },
    }


def _fallback_rl(params: Dict[str, float]) -> Dict:
    actions = ["none", "demand_generation", "consumer_subsidy", "supply_chain"]
    q = {action: 0.0 for action in actions}
    episodes = int(params.get("episodes", 160))
    trust = float(params.get("trust_score", params.get("trust", 0.60)))
    barrier = float(params.get("barrier_score", params.get("barrier", 0.35)))
    costs = {"none": 0.0, "demand_generation": 0.08, "consumer_subsidy": 0.18, "supply_chain": 0.14}
    lifts = {"none": 0.0, "demand_generation": 0.12, "consumer_subsidy": 0.16, "supply_chain": 0.13}
    expected_reward = {
        action: lifts[action] + trust * 0.30 - barrier * 0.22 - costs[action]
        for action in actions
    }
    q = {action: expected_reward[action] * 0.25 for action in actions}
    history = []
    alpha = 0.18
    gamma = 0.90
    epsilon = 0.18
    for episode in range(1, episodes + 1):
        action = random.choice(actions) if random.random() < epsilon else max(q, key=q.get)
        reward = expected_reward[action]
        q[action] += alpha * (reward + gamma * max(q.values()) - q[action])
        if episode % max(1, episodes // 24) == 0 or episode == episodes:
            history.append({"episode": episode, "action": action, "reward": reward})
    for action in actions:
        q[action] = round((q[action] + expected_reward[action]) / 2, 6)
    best = max(expected_reward, key=expected_reward.get)
    return {
        "policy": {"best_action": best, "q_values": q},
        "actions": actions,
        "history": history,
        "note": "Fallback RL used because advanced optimization dependencies are unavailable. Validate before operational use.",
        "fallback": True,
    }


@router.get("/status")
def analytics_status():
    imports = _advanced_imports()
    return {
        "available": imports["available"],
        "fallback_available": True,
        "reason": "" if imports["available"] else imports["error"],
        "warning": "" if imports["available"] else "Advanced analytics are reachable through deterministic fallbacks until Torch/Pyro are installed.",
    }


@router.post("/calibrate")
def calibrate(data: list[float]):
    imports = _advanced_imports()
    if imports["available"]:
        return imports["calibrate_parameters"](data)
    if not data:
        return {"beta": 0.30, "gamma": 0.20, "delta": 0.10, "fallback": True}
    slope = (data[-1] - data[0]) / max(1, len(data) - 1)
    return {"beta": max(0.01, 0.30 + slope), "gamma": max(0.01, 0.20 + slope / 2), "delta": 0.10, "fallback": True}


@router.post("/bayesian")
def bayesian(data: list[float], db: Session = Depends(get_db)):
    imports = _advanced_imports()
    if imports["available"]:
        priors = imports["get_latest_priors"](db)
        return imports["run_bayesian_inference"](data, priors=priors)
    return _fallback_bayesian(data)


@router.get("/priors")
def priors(db: Session = Depends(get_db)):
    imports = _advanced_imports()
    if imports["available"]:
        return {"priors": imports["get_latest_priors"](db), "fallback": False}
    return {
        "priors": {
            "beta": {"mean": 0.30, "std": 0.05},
            "gamma": {"mean": 0.20, "std": 0.05},
            "delta": {"mean": 0.10, "std": 0.03},
        },
        "fallback": True,
    }


@router.post("/update-priors")
def update_priors(db: Session = Depends(get_db)):
    imports = _advanced_imports()
    if imports["available"]:
        return imports["update_priors_from_feedback"](db)
    return {"version": None, "priors": priors(db)["priors"], "note": "Fallback mode: no persistent Pyro posterior update was run."}


@router.post("/simulate-priors")
def simulate_priors(req: PriorSimulationRequest, db: Session = Depends(get_db)):
    imports = _advanced_imports()
    if imports["available"]:
        latest = imports["get_latest_priors"](db)
        return imports["simulate_with_priors"](
            priors=latest,
            horizon=req.horizon,
            initial_adoption=req.initial_adoption,
            draws=req.draws,
        )
    latest = priors(db)["priors"]
    return _fallback_bayesian([req.initial_adoption] * max(2, min(req.horizon, 30)), latest)


@router.post("/optimize")
def optimize(params: dict):
    imports = _advanced_imports()
    if imports["available"]:
        return imports["optimize_policy"](params)
    rl = _fallback_rl(params)
    return {"recommended_intervention": rl["policy"]["best_action"], "policy_note": rl["note"], "fallback": True}


@router.post("/multi-objective")
def multi_obj(params: dict):
    imports = _advanced_imports()
    if imports["available"]:
        return imports["multi_objective_optimization"](params)
    candidates = []
    for demand in [0.0, 0.5, 1.0]:
        for subsidy in [0.0, 0.5, 1.0]:
            for supply in [0.0, 0.5, 1.0]:
                cost = demand * 0.20 + subsidy * 0.45 + supply * 0.35
                final = min(1.0, 0.35 + demand * 0.15 + subsidy * 0.20 + supply * 0.17)
                equity = (subsidy + supply) / 2
                candidates.append({"allocation": {"demand_generation": demand, "consumer_subsidy": subsidy, "supply_chain": supply}, "cost": cost, "final_adoption": final, "equity_proxy": equity, "score": final - 0.25 * cost + 0.25 * equity})
    candidates.sort(key=lambda item: item["score"], reverse=True)
    return {"best": candidates[0], "pareto_candidates": candidates[:10], "fallback": True}


@router.post("/rl")
def rl(params: dict):
    imports = _advanced_imports()
    if imports["available"]:
        return imports["q_learning_policy"](params)
    return _fallback_rl(params)


@router.post("/policy-map")
def policy_map(allocation: dict):
    imports = _advanced_imports()
    if imports["available"]:
        return imports["map_intervention_to_policy_package"](allocation)
    packages = []
    for key, value in allocation.items():
        if value:
            packages.append({"policy_key": key, "recommended_intensity": value, "field_notes": "Fallback policy map; calibrate units before field use."})
    return {"packages": packages, "estimated_relative_cost": sum(float(v) for v in allocation.values() if isinstance(v, (int, float))), "fallback": True}


@router.post("/hierarchical")
def hierarchical(data: dict, db: Session = Depends(get_db)):
    imports = _advanced_imports()
    if imports["available"]:
        priors_state = imports["get_latest_priors"](db)
        return imports["fit_hierarchical_countries"](data, priors=priors_state)
    return {"fallback": True, "note": "Hierarchical model requires Torch/Pyro.", "groups": list(data.keys()) if isinstance(data, dict) else []}


@router.post("/scenario-simulate")
def scenario_simulate(req: ScenarioRequest):
    imports = _advanced_imports()
    if imports["available"]:
        adoption_forward = imports["adoption_forward"]
        catalog = imports["POLICY_CATALOG"]
    else:
        adoption_forward = None
        catalog = {
            "demand_generation": {"effect_on_gamma": 0.18, "effect_on_delta": -0.02, "cost_per_unit": 0.20},
            "consumer_subsidy": {"effect_on_gamma": 0.25, "effect_on_delta": -0.05, "cost_per_unit": 0.45},
            "supply_chain": {"effect_on_gamma": 0.16, "effect_on_delta": -0.08, "cost_per_unit": 0.35},
        }
    results = []
    beta = float(req.base_params.get("beta", 0.30))
    gamma_base = float(req.base_params.get("gamma", 0.20))
    delta_base = float(req.base_params.get("delta", 0.10))
    for name, allocation in req.scenarios.items():
        gamma = gamma_base
        delta = delta_base
        total_cost = 0.0
        for key, intensity in allocation.items():
            if key not in catalog:
                continue
            spec = catalog[key]
            gamma += float(spec["effect_on_gamma"]) * intensity
            delta += float(spec["effect_on_delta"]) * intensity
            total_cost += float(spec["cost_per_unit"]) * intensity
        if adoption_forward:
            trajectory = [float(x) for x in adoption_forward(beta, gamma, max(0.001, delta), horizon=req.horizon).tolist()]
        else:
            trajectory = _adoption_forward_py(beta, gamma, max(0.001, delta), req.horizon)
        results.append({"scenario": name, "allocation": allocation, "cost": total_cost, "final_adoption": trajectory[-1], "trajectory": trajectory, "fallback": not imports["available"]})
    return {"results": results}

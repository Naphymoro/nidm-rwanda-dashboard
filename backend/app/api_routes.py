from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, List

from .calibration import calibrate_parameters
from .bayesian import run_bayesian_inference, adoption_forward
from .optimization import optimize_policy, multi_objective_optimization, q_learning_policy, map_intervention_to_policy_package, POLICY_CATALOG
from .hierarchical_bayes import fit_hierarchical_countries

router = APIRouter()


class ScenarioRequest(BaseModel):
    base_params: Dict[str, float]
    scenarios: Dict[str, Dict[str, float]]
    horizon: int = 180


@router.post("/calibrate")
def calibrate(data: list[float]):
    return calibrate_parameters(data)


@router.post("/bayesian")
def bayesian(data: list[float]):
    return run_bayesian_inference(data)


@router.post("/optimize")
def optimize(params: dict):
    return optimize_policy(params)


@router.post("/multi-objective")
def multi_obj(params: dict):
    return multi_objective_optimization(params)


@router.post("/rl")
def rl(params: dict):
    return q_learning_policy(params)


@router.post("/policy-map")
def policy_map(allocation: dict):
    return map_intervention_to_policy_package(allocation)


@router.post("/hierarchical")
def hierarchical(data: dict):
    return fit_hierarchical_countries(data)


@router.post("/scenario-simulate")
def scenario_simulate(req: ScenarioRequest):
    results = []
    beta = float(req.base_params.get("beta", 0.30))
    gamma_base = float(req.base_params.get("gamma", 0.20))
    delta_base = float(req.base_params.get("delta", 0.10))

    for name, allocation in req.scenarios.items():
        gamma = gamma_base
        delta = delta_base
        total_cost = 0.0
        for key, intensity in allocation.items():
            if key not in POLICY_CATALOG:
                continue
            spec = POLICY_CATALOG[key]
            gamma += spec["effect_on_gamma"] * float(intensity)
            delta += spec["effect_on_delta"] * float(intensity)
            total_cost += spec["cost_per_unit"] * float(intensity)
        delta = max(0.001, delta)
        traj = adoption_forward(beta, gamma, delta, horizon=req.horizon)
        results.append({
            "scenario": name,
            "allocation": allocation,
            "cost": total_cost,
            "final_adoption": float(traj[-1].item()),
            "trajectory": [{"day": i + 1, "adoption": float(v)} for i, v in enumerate(traj.tolist())],
        })
    return {"scenarios": results}

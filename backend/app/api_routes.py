from fastapi import APIRouter
from .calibration import calibrate_parameters
from .bayesian import run_bayesian_inference
from .optimization import optimize_policy, multi_objective_optimization, q_learning_policy, map_intervention_to_policy_package
from .hierarchical_bayes import fit_hierarchical_countries

router = APIRouter()

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

from typing import Dict, List, Tuple
import random
import torch

from .bayesian import adoption_forward

POLICY_CATALOG = {
    "demand_generation": {
        "name": "Community trust and behavior-change campaign",
        "lever": "trust_score",
        "unit": "campaign intensity",
        "cost_per_unit": 0.20,
        "effect_on_gamma": 0.18,
        "effect_on_delta": -0.02,
        "notes": "Radio, CHW facilitation, demonstrations, peer champions.",
    },
    "consumer_subsidy": {
        "name": "Targeted clean-cooking consumer subsidy",
        "lever": "affordability",
        "unit": "subsidy intensity",
        "cost_per_unit": 0.45,
        "effect_on_gamma": 0.25,
        "effect_on_delta": -0.05,
        "notes": "Voucher, results-based financing, or staged appliance discount.",
    },
    "supply_chain": {
        "name": "Last-mile supply and maintenance strengthening",
        "lever": "fuel_access_and_reliability",
        "unit": "supply-side intensity",
        "cost_per_unit": 0.35,
        "effect_on_gamma": 0.16,
        "effect_on_delta": -0.08,
        "notes": "Retailer network, spare parts, fuel availability, technician coverage.",
    },
}


def _trajectory_from_policy(base_params: Dict[str, float], allocation: Dict[str, float], horizon: int) -> Tuple[List[float], Dict[str, float]]:
    beta = torch.tensor(float(base_params.get("beta", 0.30)))
    gamma = float(base_params.get("gamma", 0.20))
    delta = float(base_params.get("delta", 0.10))
    total_cost = 0.0

    for key, intensity in allocation.items():
        spec = POLICY_CATALOG[key]
        gamma += spec["effect_on_gamma"] * intensity
        delta += spec["effect_on_delta"] * intensity
        total_cost += spec["cost_per_unit"] * intensity

    delta = max(0.001, delta)
    trajectory = adoption_forward(beta, torch.tensor(gamma), torch.tensor(delta), horizon=horizon)
    return [float(x) for x in trajectory.tolist()], {"gamma": gamma, "delta": delta, "cost": total_cost}


def optimize_policy(
    base_params: Dict[str, float],
    horizon: int = 180,
    budget: float = 1.0,
    target_adoption: float = 0.75,
    steps: int = 250,
) -> Dict:
    beta = torch.tensor(float(base_params.get("beta", 0.30)))
    delta = torch.tensor(float(base_params.get("delta", 0.10)))
    raw_intervention = torch.nn.Parameter(torch.tensor(0.0))
    optimizer = torch.optim.Adam([raw_intervention], lr=0.05)
    history: List[Dict[str, float]] = []

    for step in range(steps):
        optimizer.zero_grad()
        intervention = budget * torch.sigmoid(raw_intervention)
        gamma = torch.tensor(float(base_params.get("gamma", 0.20))) + 0.35 * intervention
        trajectory = adoption_forward(beta, gamma, delta, horizon=horizon)
        final_adoption = trajectory[-1]
        shortfall = torch.relu(torch.tensor(target_adoption) - final_adoption)
        cost_penalty = 0.15 * intervention**2
        loss = shortfall**2 + cost_penalty - 0.05 * final_adoption
        loss.backward()
        optimizer.step()
        if step % 25 == 0 or step == steps - 1:
            history.append({"step": float(step), "intervention": float(intervention.item()), "final_adoption": float(final_adoption.item()), "loss": float(loss.item())})

    intervention = budget * torch.sigmoid(raw_intervention)
    gamma = torch.tensor(float(base_params.get("gamma", 0.20))) + 0.35 * intervention
    trajectory = adoption_forward(beta, gamma, delta, horizon=horizon)
    return {
        "recommended_intervention": float(intervention.item()),
        "expected_final_adoption": float(trajectory[-1].item()),
        "target_adoption": target_adoption,
        "budget": budget,
        "trajectory": [float(x) for x in trajectory.tolist()],
        "optimization_history": history,
        "policy_note": "Intervention intensity is normalized; calibrate to real subsidy, messaging, or supply-side program units before field use.",
    }


def multi_objective_optimization(base_params: Dict[str, float], horizon: int = 180, budget: float = 1.0, equity_weight: float = 0.25) -> Dict:
    """Grid-based Pareto search over policy levers: maximize adoption, minimize cost, improve equity proxy."""
    candidates = []
    grid = [0.0, 0.25, 0.5, 0.75, 1.0]
    for demand in grid:
        for subsidy in grid:
            for supply in grid:
                allocation = {"demand_generation": demand, "consumer_subsidy": subsidy, "supply_chain": supply}
                trajectory, derived = _trajectory_from_policy(base_params, allocation, horizon)
                if derived["cost"] > budget:
                    continue
                final_adoption = trajectory[-1]
                equity_proxy = 0.5 * subsidy + 0.5 * supply
                score = final_adoption - 0.25 * derived["cost"] + equity_weight * equity_proxy
                candidates.append({
                    "allocation": allocation,
                    "cost": derived["cost"],
                    "final_adoption": final_adoption,
                    "equity_proxy": equity_proxy,
                    "score": score,
                    "trajectory": trajectory,
                })
    candidates.sort(key=lambda x: x["score"], reverse=True)
    return {"best": candidates[0] if candidates else None, "pareto_candidates": candidates[:10], "policy_catalog": POLICY_CATALOG}


def q_learning_policy(base_params: Dict[str, float], episodes: int = 250, horizon: int = 60, budget: float = 1.0) -> Dict:
    """Lightweight reinforcement learning prototype for sequential intervention planning."""
    actions = ["none", "demand_generation", "consumer_subsidy", "supply_chain"]
    q = {}
    alpha, gamma_discount, epsilon = 0.2, 0.92, 0.2

    def bucket(a: float) -> int:
        return min(9, max(0, int(a * 10)))

    for _ in range(episodes):
        adoption = 0.10
        spend = 0.0
        for _t in range(horizon):
            state = (bucket(adoption), bucket(spend / max(budget, 1e-6)))
            q.setdefault(state, {a: 0.0 for a in actions})
            action = random.choice(actions) if random.random() < epsilon else max(q[state], key=q[state].get)
            allocation = {k: 0.0 for k in POLICY_CATALOG}
            if action != "none" and spend < budget:
                allocation[action] = 0.1
            traj, derived = _trajectory_from_policy(base_params, allocation, horizon=1)
            adoption = traj[-1]
            spend = min(budget, spend + derived["cost"])
            reward = adoption - 0.15 * spend
            next_state = (bucket(adoption), bucket(spend / max(budget, 1e-6)))
            q.setdefault(next_state, {a: 0.0 for a in actions})
            q[state][action] += alpha * (reward + gamma_discount * max(q[next_state].values()) - q[state][action])

    policy = {str(state): max(values, key=values.get) for state, values in q.items()}
    return {"policy": policy, "actions": actions, "note": "Prototype RL policy; validate with calibrated environment before operational use."}


def map_intervention_to_policy_package(allocation: Dict[str, float]) -> Dict:
    packages = []
    total_cost = 0.0
    for key, intensity in allocation.items():
        if key not in POLICY_CATALOG or intensity <= 0:
            continue
        spec = POLICY_CATALOG[key]
        total_cost += spec["cost_per_unit"] * intensity
        packages.append({
            "policy_key": key,
            "policy_name": spec["name"],
            "recommended_intensity": intensity,
            "implementation_unit": spec["unit"],
            "estimated_relative_cost": spec["cost_per_unit"] * intensity,
            "field_notes": spec["notes"],
        })
    return {"packages": packages, "estimated_relative_cost": total_cost}


def compare_policy_grid(base_params: Dict[str, float], horizon: int = 180) -> Dict:
    scenarios = []
    beta = torch.tensor(float(base_params.get("beta", 0.30)))
    delta = torch.tensor(float(base_params.get("delta", 0.10)))
    gamma_base = float(base_params.get("gamma", 0.20))
    for intervention in [0.0, 0.25, 0.5, 0.75, 1.0]:
        gamma = torch.tensor(gamma_base + 0.35 * intervention)
        trajectory = adoption_forward(beta, gamma, delta, horizon=horizon)
        scenarios.append({"intervention": intervention, "final_adoption": float(trajectory[-1].item()), "trajectory": [float(x) for x in trajectory.tolist()]})
    return {"scenarios": scenarios}

from typing import Dict, List
import torch

from .bayesian import adoption_forward


def optimize_policy(
    base_params: Dict[str, float],
    horizon: int = 180,
    budget: float = 1.0,
    target_adoption: float = 0.75,
    steps: int = 250,
) -> Dict:
    """
    Optimize intervention intensity under a simple budget constraint.

    Decision variable:
    - intervention: scalar in [0, budget]

    Objective:
    - maximize final adoption
    - penalize overspending and target shortfall
    """
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
            history.append({
                "step": float(step),
                "intervention": float(intervention.item()),
                "final_adoption": float(final_adoption.item()),
                "loss": float(loss.item()),
            })

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


def compare_policy_grid(base_params: Dict[str, float], horizon: int = 180) -> Dict:
    scenarios = []
    beta = torch.tensor(float(base_params.get("beta", 0.30)))
    delta = torch.tensor(float(base_params.get("delta", 0.10)))
    gamma_base = float(base_params.get("gamma", 0.20))

    for intervention in [0.0, 0.25, 0.5, 0.75, 1.0]:
        gamma = torch.tensor(gamma_base + 0.35 * intervention)
        trajectory = adoption_forward(beta, gamma, delta, horizon=horizon)
        scenarios.append({
            "intervention": intervention,
            "final_adoption": float(trajectory[-1].item()),
            "trajectory": [float(x) for x in trajectory.tolist()],
        })

    return {"scenarios": scenarios}

import torch
from typing import Dict, List


def simulate_adoption(params, horizon=100):
    beta, gamma, delta = params
    A = torch.tensor(0.1)
    trajectory = []
    for _ in range(horizon):
        dA = beta * A * (1 - A) + gamma * (1 - A) - delta * A
        A = A + dA
        trajectory.append(A)
    return torch.stack(trajectory)


def calibrate_parameters(observed: List[float], epochs: int = 200) -> Dict[str, float]:
    obs = torch.tensor(observed)

    params = torch.nn.Parameter(torch.tensor([0.3, 0.2, 0.1]))
    optimizer = torch.optim.Adam([params], lr=0.05)

    for _ in range(epochs):
        optimizer.zero_grad()
        pred = simulate_adoption(params, len(obs))
        loss = torch.mean((pred - obs) ** 2)
        loss.backward()
        optimizer.step()

    return {
        "beta": float(params[0].item()),
        "gamma": float(params[1].item()),
        "delta": float(params[2].item()),
        "loss": float(loss.item()),
    }


def monte_carlo_simulation(params: Dict[str, float], runs: int = 50, horizon: int = 100):
    results = []
    for _ in range(runs):
        noisy_params = torch.tensor([
            params["beta"] * torch.normal(1.0, 0.1, (1,)).item(),
            params["gamma"] * torch.normal(1.0, 0.1, (1,)).item(),
            params["delta"] * torch.normal(1.0, 0.1, (1,)).item(),
        ])
        traj = simulate_adoption(noisy_params, horizon)
        results.append(traj)

    stacked = torch.stack(results)
    return {
        "mean": stacked.mean(dim=0).tolist(),
        "std": stacked.std(dim=0).tolist(),
    }

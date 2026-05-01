import math
from typing import Dict, Optional

import torch
import pyro
import pyro.distributions as dist
from pyro.infer import MCMC, NUTS


def adoption_forward(beta, gamma, delta, horizon=50, initial_adoption=0.1):
    A = torch.as_tensor(initial_adoption, dtype=torch.float32)
    trajectory = []
    for _ in range(horizon):
        dA = beta * A * (1 - A) + gamma * (1 - A) - delta * A
        A = torch.clamp(A + dA, 0.0, 1.0)
        trajectory.append(A)
    return torch.stack(trajectory)


def _lognormal_params(mean: float, std: float):
    mean = max(float(mean), 1e-4)
    std = max(float(std), 1e-4)
    variance = std ** 2
    sigma2 = math.log(1 + variance / (mean ** 2))
    sigma = math.sqrt(max(sigma2, 1e-6))
    mu = math.log(mean) - 0.5 * sigma2
    return torch.tensor(mu, dtype=torch.float32), torch.tensor(sigma, dtype=torch.float32)


def _prior_distribution(name: str, priors: Optional[Dict]):
    defaults = {
        "beta": {"mean": 0.30, "std": 0.05},
        "gamma": {"mean": 0.20, "std": 0.05},
        "delta": {"mean": 0.10, "std": 0.03},
    }
    spec = (priors or {}).get(name, defaults[name])
    mean = spec.get("mean", defaults[name]["mean"])
    std = spec.get("std", spec.get("sd", defaults[name]["std"]))
    mu, sigma = _lognormal_params(mean, std)
    return dist.LogNormal(mu, sigma)


def adoption_model(observed=None, horizon=50, initial_adoption=0.1, priors: Optional[Dict] = None):
    beta = pyro.sample("beta", _prior_distribution("beta", priors))
    gamma = pyro.sample("gamma", _prior_distribution("gamma", priors))
    delta = pyro.sample("delta", _prior_distribution("delta", priors))
    sigma = pyro.sample("sigma", dist.HalfNormal(0.08))

    pred = adoption_forward(beta, gamma, delta, horizon, initial_adoption)

    if observed is not None:
        pyro.sample("obs", dist.Normal(pred, sigma).to_event(1), obs=torch.tensor(observed, dtype=torch.float32))

    return pred


def _summary(values):
    return {
        "mean": float(values.mean().item()),
        "std": float(values.std().item()),
        "sd": float(values.std().item()),
        "q05": float(torch.quantile(values, 0.05).item()),
        "q50": float(torch.quantile(values, 0.50).item()),
        "q95": float(torch.quantile(values, 0.95).item()),
    }


def run_bayesian_inference(observed_data, samples=300, warmup=100, priors: Optional[Dict] = None):
    pyro.clear_param_store()
    kernel = NUTS(adoption_model)
    mcmc = MCMC(kernel, num_samples=samples, warmup_steps=warmup)
    mcmc.run(
        observed=observed_data,
        horizon=len(observed_data),
        initial_adoption=float(observed_data[0]),
        priors=priors,
    )
    posterior = mcmc.get_samples()

    trajectories = []
    for beta, gamma, delta in zip(posterior["beta"], posterior["gamma"], posterior["delta"]):
        trajectories.append(adoption_forward(beta, gamma, delta, len(observed_data), float(observed_data[0])))
    draws = torch.stack(trajectories)

    return {
        "parameters": {
            "beta": _summary(posterior["beta"]),
            "gamma": _summary(posterior["gamma"]),
            "delta": _summary(posterior["delta"]),
            "sigma": _summary(posterior["sigma"]),
        },
        "trajectory": {
            "mean": draws.mean(dim=0).tolist(),
            "lower_90": torch.quantile(draws, 0.05, dim=0).tolist(),
            "upper_90": torch.quantile(draws, 0.95, dim=0).tolist(),
        },
        "diagnostics": {
            "samples": samples,
            "warmup": warmup,
            "horizon": len(observed_data),
            "prior_source": "learned_posterior" if priors else "default",
            "priors_used": priors,
        },
    }


def simulate_with_priors(priors: Dict, horizon: int = 180, initial_adoption: float = 0.1, draws: int = 200):
    trajectories = []
    beta_dist = _prior_distribution("beta", priors)
    gamma_dist = _prior_distribution("gamma", priors)
    delta_dist = _prior_distribution("delta", priors)
    for _ in range(draws):
        beta = beta_dist.sample()
        gamma = gamma_dist.sample()
        delta = delta_dist.sample()
        trajectories.append(adoption_forward(beta, gamma, delta, horizon, initial_adoption))
    stacked = torch.stack(trajectories)
    return {
        "trajectory": {
            "mean": stacked.mean(dim=0).tolist(),
            "lower_90": torch.quantile(stacked, 0.05, dim=0).tolist(),
            "upper_90": torch.quantile(stacked, 0.95, dim=0).tolist(),
        },
        "diagnostics": {
            "draws": draws,
            "horizon": horizon,
            "initial_adoption": initial_adoption,
            "priors_used": priors,
        },
    }

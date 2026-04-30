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


def adoption_model(observed=None, horizon=50, initial_adoption=0.1):
    beta = pyro.sample("beta", dist.LogNormal(-1.25, 0.35))
    gamma = pyro.sample("gamma", dist.LogNormal(-1.65, 0.35))
    delta = pyro.sample("delta", dist.LogNormal(-2.30, 0.35))
    sigma = pyro.sample("sigma", dist.HalfNormal(0.08))

    pred = adoption_forward(beta, gamma, delta, horizon, initial_adoption)

    if observed is not None:
        pyro.sample("obs", dist.Normal(pred, sigma).to_event(1), obs=torch.tensor(observed, dtype=torch.float32))

    return pred


def _summary(values):
    return {
        "mean": float(values.mean().item()),
        "sd": float(values.std().item()),
        "q05": float(torch.quantile(values, 0.05).item()),
        "q50": float(torch.quantile(values, 0.50).item()),
        "q95": float(torch.quantile(values, 0.95).item()),
    }


def run_bayesian_inference(observed_data, samples=300, warmup=100):
    pyro.clear_param_store()
    kernel = NUTS(adoption_model)
    mcmc = MCMC(kernel, num_samples=samples, warmup_steps=warmup)
    mcmc.run(observed=observed_data, horizon=len(observed_data), initial_adoption=float(observed_data[0]))
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
        },
    }

import torch
import pyro
import pyro.distributions as dist
from pyro.infer import MCMC, NUTS


def adoption_model(observed=None, horizon=50):
    beta = pyro.sample("beta", dist.Normal(0.3, 0.1))
    gamma = pyro.sample("gamma", dist.Normal(0.2, 0.1))
    delta = pyro.sample("delta", dist.Normal(0.1, 0.05))

    A = 0.1
    trajectory = []

    for t in range(horizon):
        dA = beta * A * (1 - A) + gamma * (1 - A) - delta * A
        A = A + dA
        trajectory.append(A)

    pred = torch.tensor(trajectory)

    if observed is not None:
        pyro.sample("obs", dist.Normal(pred, 0.05).to_event(1), obs=torch.tensor(observed))

    return pred


def run_bayesian_inference(observed_data, samples=200):
    kernel = NUTS(adoption_model)
    mcmc = MCMC(kernel, num_samples=samples, warmup_steps=50)
    mcmc.run(observed=observed_data, horizon=len(observed_data))

    posterior = mcmc.get_samples()

    return {
        "beta": posterior["beta"].mean().item(),
        "gamma": posterior["gamma"].mean().item(),
        "delta": posterior["delta"].mean().item(),
    }

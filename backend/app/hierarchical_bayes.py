from typing import Dict, List
import torch
import pyro
import pyro.distributions as dist
from pyro.infer import MCMC, NUTS

from .bayesian import adoption_forward


def hierarchical_country_model(country_series: Dict[str, List[float]]):
    beta_mu = pyro.sample("beta_mu", dist.LogNormal(-1.25, 0.35))
    gamma_mu = pyro.sample("gamma_mu", dist.LogNormal(-1.65, 0.35))
    delta_mu = pyro.sample("delta_mu", dist.LogNormal(-2.30, 0.35))

    beta_scale = pyro.sample("beta_scale", dist.HalfNormal(0.08))
    gamma_scale = pyro.sample("gamma_scale", dist.HalfNormal(0.08))
    delta_scale = pyro.sample("delta_scale", dist.HalfNormal(0.05))
    sigma = pyro.sample("sigma", dist.HalfNormal(0.08))

    for country, values in country_series.items():
        clean = torch.tensor(values, dtype=torch.float32)
        beta = pyro.sample(f"beta_{country}", dist.LogNormal(torch.log(beta_mu), beta_scale))
        gamma = pyro.sample(f"gamma_{country}", dist.LogNormal(torch.log(gamma_mu), gamma_scale))
        delta = pyro.sample(f"delta_{country}", dist.LogNormal(torch.log(delta_mu), delta_scale))
        pred = adoption_forward(beta, gamma, delta, horizon=len(clean), initial_adoption=float(clean[0]))
        pyro.sample(f"obs_{country}", dist.Normal(pred, sigma).to_event(1), obs=clean)


def _summary(x):
    return {
        "mean": float(x.mean().item()),
        "sd": float(x.std().item()),
        "q05": float(torch.quantile(x, 0.05).item()),
        "q50": float(torch.quantile(x, 0.50).item()),
        "q95": float(torch.quantile(x, 0.95).item()),
    }


def fit_hierarchical_countries(country_series: Dict[str, List[float]], samples: int = 200, warmup: int = 100):
    pyro.clear_param_store()
    kernel = NUTS(hierarchical_country_model)
    mcmc = MCMC(kernel, num_samples=samples, warmup_steps=warmup)
    mcmc.run(country_series=country_series)
    posterior = mcmc.get_samples()

    countries = list(country_series.keys())
    country_params = {}
    for country in countries:
        country_params[country] = {
            "beta": _summary(posterior[f"beta_{country}"]),
            "gamma": _summary(posterior[f"gamma_{country}"]),
            "delta": _summary(posterior[f"delta_{country}"]),
        }

    return {
        "global": {
            "beta_mu": _summary(posterior["beta_mu"]),
            "gamma_mu": _summary(posterior["gamma_mu"]),
            "delta_mu": _summary(posterior["delta_mu"]),
            "sigma": _summary(posterior["sigma"]),
        },
        "countries": country_params,
        "diagnostics": {"samples": samples, "warmup": warmup, "countries": countries},
    }

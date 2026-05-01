from typing import Dict, List, Optional
import math
import torch
import pyro
import pyro.distributions as dist
from pyro.infer import MCMC, NUTS

from .bayesian import adoption_forward


def _lognormal_params(mean: float, std: float):
    mean = max(float(mean), 1e-4)
    std = max(float(std), 1e-4)
    variance = std ** 2
    sigma2 = math.log(1 + variance / (mean ** 2))
    sigma = math.sqrt(max(sigma2, 1e-6))
    mu = math.log(mean) - 0.5 * sigma2
    return torch.tensor(mu, dtype=torch.float32), torch.tensor(sigma, dtype=torch.float32)


def _global_prior(name: str, priors: Optional[Dict]):
    defaults = {
        "beta": {"mean": 0.30, "std": 0.05},
        "gamma": {"mean": 0.20, "std": 0.05},
        "delta": {"mean": 0.10, "std": 0.03},
    }
    spec = (priors or {}).get(name, defaults[name])
    mu, sigma = _lognormal_params(spec.get("mean", defaults[name]["mean"]), spec.get("std", spec.get("sd", defaults[name]["std"])))
    return dist.LogNormal(mu, sigma)


def hierarchical_country_model(country_series: Dict[str, List[float]], priors: Optional[Dict] = None):
    beta_mu = pyro.sample("beta_mu", _global_prior("beta", priors))
    gamma_mu = pyro.sample("gamma_mu", _global_prior("gamma", priors))
    delta_mu = pyro.sample("delta_mu", _global_prior("delta", priors))

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
        "std": float(x.std().item()),
        "sd": float(x.std().item()),
        "q05": float(torch.quantile(x, 0.05).item()),
        "q50": float(torch.quantile(x, 0.50).item()),
        "q95": float(torch.quantile(x, 0.95).item()),
    }


def _country_forecast(posterior, country: str, values: List[float], horizon: int):
    draws = []
    initial = float(values[0])
    for beta, gamma, delta in zip(posterior[f"beta_{country}"], posterior[f"gamma_{country}"], posterior[f"delta_{country}"]):
        draws.append(adoption_forward(beta, gamma, delta, horizon=horizon, initial_adoption=initial))
    stacked = torch.stack(draws)
    return {
        "mean": stacked.mean(dim=0).tolist(),
        "lower_90": torch.quantile(stacked, 0.05, dim=0).tolist(),
        "upper_90": torch.quantile(stacked, 0.95, dim=0).tolist(),
    }


def fit_hierarchical_countries(
    country_series: Dict[str, List[float]],
    samples: int = 200,
    warmup: int = 100,
    priors: Optional[Dict] = None,
    forecast_horizon: int = 180,
):
    pyro.clear_param_store()
    kernel = NUTS(hierarchical_country_model)
    mcmc = MCMC(kernel, num_samples=samples, warmup_steps=warmup)
    mcmc.run(country_series=country_series, priors=priors)
    posterior = mcmc.get_samples()

    countries = list(country_series.keys())
    country_params = {}
    forecasts = {}
    for country in countries:
        country_params[country] = {
            "beta": _summary(posterior[f"beta_{country}"]),
            "gamma": _summary(posterior[f"gamma_{country}"]),
            "delta": _summary(posterior[f"delta_{country}"]),
        }
        forecasts[country] = _country_forecast(posterior, country, country_series[country], forecast_horizon)

    return {
        "global": {
            "beta_mu": _summary(posterior["beta_mu"]),
            "gamma_mu": _summary(posterior["gamma_mu"]),
            "delta_mu": _summary(posterior["delta_mu"]),
            "beta_scale": _summary(posterior["beta_scale"]),
            "gamma_scale": _summary(posterior["gamma_scale"]),
            "delta_scale": _summary(posterior["delta_scale"]),
            "sigma": _summary(posterior["sigma"]),
        },
        "countries": country_params,
        "forecasts": forecasts,
        "diagnostics": {
            "samples": samples,
            "warmup": warmup,
            "countries": countries,
            "forecast_horizon": forecast_horizon,
            "prior_source": "learned_posterior" if priors else "default",
            "priors_used": priors,
        },
    }

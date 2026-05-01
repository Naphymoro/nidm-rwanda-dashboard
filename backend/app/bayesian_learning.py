from datetime import datetime, timezone
from typing import Dict, List

import torch
import pyro
import pyro.distributions as dist
from pyro.infer import MCMC, NUTS
from sqlalchemy.orm import Session

from . import models


def _now():
    return datetime.now(timezone.utc).isoformat()


def default_priors():
    return {
        "beta": {"mean": 0.30, "std": 0.05},
        "gamma": {"mean": 0.20, "std": 0.05},
        "delta": {"mean": 0.10, "std": 0.03},
    }


def get_latest_priors(db: Session) -> Dict:
    row = (
        db.query(models.BayesianPriorState)
        .order_by(models.BayesianPriorState.version.desc())
        .first()
    )
    return row.priors if row else default_priors()


def _summarize(samples: torch.Tensor) -> Dict:
    return {
        "mean": float(samples.mean().item()),
        "std": float(samples.std().item()),
        "q05": float(torch.quantile(samples, 0.05).item()),
        "q50": float(torch.quantile(samples, 0.50).item()),
        "q95": float(torch.quantile(samples, 0.95).item()),
    }


def _feedback_counts(feedback: List[models.LearningFeedback]) -> Dict[str, int]:
    outcomes = [f.outcome for f in feedback]
    return {
        "helpful": outcomes.count("helpful"),
        "too_costly": outcomes.count("too_costly"),
        "too_aggressive": outcomes.count("too_aggressive"),
        "needs_data": outcomes.count("needs_data"),
        "total": len(outcomes),
    }


def feedback_posterior_model(counts: Dict[str, int], prior_state: Dict):
    beta_mu = torch.tensor(float(prior_state["beta"]["mean"]))
    gamma_mu = torch.tensor(float(prior_state["gamma"]["mean"]))
    delta_mu = torch.tensor(float(prior_state["delta"]["mean"]))

    beta_sd = torch.tensor(max(float(prior_state["beta"].get("std", 0.05)), 0.01))
    gamma_sd = torch.tensor(max(float(prior_state["gamma"].get("std", 0.05)), 0.01))
    delta_sd = torch.tensor(max(float(prior_state["delta"].get("std", 0.03)), 0.01))

    beta = pyro.sample("beta", dist.LogNormal(torch.log(beta_mu), beta_sd))
    gamma = pyro.sample("gamma", dist.LogNormal(torch.log(gamma_mu), gamma_sd))
    delta = pyro.sample("delta", dist.LogNormal(torch.log(delta_mu), delta_sd))

    # Feedback likelihood. Each feedback category is modeled as a binomial observation.
    # Helpful feedback becomes more probable when diffusion/intervention assumptions are strong.
    helpful_p = torch.sigmoid(3.0 * (beta + gamma - delta - 0.35))
    costly_p = torch.sigmoid(5.0 * (gamma - 0.22))
    aggressive_p = torch.sigmoid(5.0 * (delta + gamma - 0.28))
    needs_data_p = torch.sigmoid(4.0 * (0.16 - beta) + 2.0 * delta)

    total = int(max(counts.get("total", 0), 1))
    pyro.sample("obs_helpful", dist.Binomial(total_count=total, probs=helpful_p), obs=torch.tensor(float(counts.get("helpful", 0))))
    pyro.sample("obs_costly", dist.Binomial(total_count=total, probs=costly_p), obs=torch.tensor(float(counts.get("too_costly", 0))))
    pyro.sample("obs_aggressive", dist.Binomial(total_count=total, probs=aggressive_p), obs=torch.tensor(float(counts.get("too_aggressive", 0))))
    pyro.sample("obs_needs_data", dist.Binomial(total_count=total, probs=needs_data_p), obs=torch.tensor(float(counts.get("needs_data", 0))))


def update_priors_from_feedback(db: Session, samples: int = 300, warmup: int = 150) -> Dict:
    feedback = db.query(models.LearningFeedback).all()
    counts = _feedback_counts(feedback)
    prior_state = get_latest_priors(db)

    if counts["total"] == 0:
        return {
            "version": None,
            "priors": prior_state,
            "evidence": counts,
            "note": "No feedback available; priors unchanged.",
        }

    pyro.clear_param_store()
    kernel = NUTS(feedback_posterior_model)
    mcmc = MCMC(kernel, num_samples=samples, warmup_steps=warmup)
    mcmc.run(counts=counts, prior_state=prior_state)
    posterior = mcmc.get_samples()

    posterior_priors = {
        "beta": _summarize(posterior["beta"]),
        "gamma": _summarize(posterior["gamma"]),
        "delta": _summarize(posterior["delta"]),
    }

    latest = db.query(models.BayesianPriorState).order_by(models.BayesianPriorState.version.desc()).first()
    next_version = (latest.version + 1) if latest else 1

    record = models.BayesianPriorState(
        country="global",
        version=next_version,
        priors=posterior_priors,
        evidence_summary={
            **counts,
            "method": "pyro_mcmc_feedback_posterior",
            "samples": samples,
            "warmup": warmup,
        },
        created_at=_now(),
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return {
        "version": record.version,
        "priors": record.priors,
        "evidence": record.evidence_summary,
        "note": "Priors updated from full Pyro posterior over feedback likelihood.",
    }

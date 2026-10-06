"""Which assumptions drive the result? Variance-based global sensitivity analysis (Sobol indices) of the population model.

Each factor is varied over a range at once with all the others (not one at a time), and the variance of the output
(adoption at the end of the period) is split between them:

    first-order  S_i  = Var(E[Y | X_i]) / Var(Y)      the share explained by factor i alone
    total        ST_i = E[Var(Y | X_~i)] / Var(Y)     the share that involves factor i, including interactions

Estimated with Saltelli's sampling scheme (matrices A, B and A with column i taken from B), the Saltelli (2010)
first-order and Jansen total-order estimators, a scrambled Sobol sequence with a fixed seed (reproducible), and
bootstrap 90% intervals. scripts/test_sensitivity.py checks the estimators against the Ishigami function, whose
indices are known exactly.

Factors are of two kinds: the evidence inputs (trust, barrier, narrative influence, intervention strength), varied
around their values, and the tool's own assumptions (the rate constants), each scaled from half to double. The second
kind is the doubt the uncertainty band leaves out.
"""
from typing import Callable, Dict, List

import numpy as np
from scipy.stats import qmc

from .modelling import compartmental_path, compartmental_rates

# name, kind, plain label
FACTORS = [
    ('trust_score', 'evidence', 'trust score'),
    ('barrier_score', 'evidence', 'barrier score'),
    ('narrative_influence', 'evidence', 'narrative influence'),
    ('intervention_strength', 'evidence', 'intervention strength'),
    ('beta_t', 'assumption', 'word-of-mouth rate (β_t)'),
    ('beta_m', 'assumption', 'misinformation spread rate (β_m)'),
    ('iota', 'assumption', 'outreach and inoculation rate (ι)'),
    ('delta', 'assumption', 'adopter stop rate (δ)'),
    ('conversion', 'assumption', 'conversion rates (ρ, γ, η)'),
]
EVIDENCE_SPREAD = 0.15  # evidence inputs vary +/- this around their value, inside 0-1
ASSUMPTION_RANGE = (0.5, 2.0)  # rate constants are scaled by a factor in this range (log-uniform)
BASE_SAMPLES = 1024  # 11,264 model runs, about 4 s locally; 128 left first-order indices too noisy
SEED = 2026


def sobol_indices(model: Callable[[np.ndarray], np.ndarray], bounds: List[tuple], samples: int = BASE_SAMPLES,
                  seed: int = SEED, bootstrap: int = 200) -> Dict[str, np.ndarray]:
    """First-order and total Sobol indices of model (rows of inputs -> outputs) over independent uniform inputs."""
    k = len(bounds)
    base = qmc.Sobol(d=2 * k, scramble=True, seed=seed).random(samples)
    low, high = np.array([b[0] for b in bounds]), np.array([b[1] for b in bounds])
    a, b = low + base[:, :k] * (high - low), low + base[:, k:] * (high - low)
    ya, yb = model(a), model(b)
    yab = np.empty((k, samples))
    for i in range(k):
        mixed = a.copy()
        mixed[:, i] = b[:, i]
        yab[i] = model(mixed)

    def estimate(rows):
        fa, fb, fab = ya[rows], yb[rows], yab[:, rows]
        variance = np.var(np.concatenate([fa, fb]))
        if variance <= 0:
            return np.zeros(k), np.zeros(k)
        first = np.mean(fb * (fab - fa), axis=1) / variance  # Saltelli 2010
        total = 0.5 * np.mean((fa - fab) ** 2, axis=1) / variance  # Jansen 1999
        return first, total

    first, total = estimate(np.arange(samples))
    rng = np.random.default_rng(seed)
    draws = [estimate(rng.integers(0, samples, samples)) for _ in range(bootstrap)]
    first_ci = np.percentile([d[0] for d in draws], [5, 95], axis=0)
    total_ci = np.percentile([d[1] for d in draws], [5, 95], axis=0)
    return {'first': first, 'total': total, 'first_ci': first_ci, 'total_ci': total_ci,
            'variance': float(np.var(np.concatenate([ya, yb]))), 'mean': float(np.mean(np.concatenate([ya, yb]))),
            'runs': samples * (k + 2)}


def _bounds(parameters):
    bounds = []
    for name, kind, _ in FACTORS:
        if kind == 'evidence':
            value = float(parameters.get(name, {'trust_score': 0.6, 'barrier_score': 0.35, 'narrative_influence': 0.38,
                                                'intervention_strength': 0.15}[name]))
            bounds.append((max(0.0, value - EVIDENCE_SPREAD), min(1.0, value + EVIDENCE_SPREAD)))
        else:
            bounds.append((np.log(ASSUMPTION_RANGE[0]), np.log(ASSUMPTION_RANGE[1])))  # log-scale multiplier
    return bounds


def population_model(horizon_days: int, parameters: Dict[str, float]) -> Callable[[np.ndarray], np.ndarray]:
    """Rows of factor values -> adoption at the end of the period."""
    def run(rows: np.ndarray) -> np.ndarray:
        out = np.empty(len(rows))
        for index, row in enumerate(rows):
            values = dict(zip([f[0] for f in FACTORS], row))
            params = {key: value for key, value in parameters.items() if key not in compartmental_rates({})}
            params.update({name: values[name] for name, kind, _ in FACTORS if kind == 'evidence'})
            rates = compartmental_rates(params)  # the rates these evidence values give, then the assumption multipliers
            scale = {name: float(np.exp(values[name])) for name, kind, _ in FACTORS if kind == 'assumption'}
            params.update({'beta_t': rates['beta_t'] * scale['beta_t'], 'beta_m': rates['beta_m'] * scale['beta_m'],
                           'iota': rates['iota'] * scale['iota'], 'delta': rates['delta'] * scale['delta'],
                           'rho': rates['rho'] * scale['conversion'], 'gamma': rates['gamma'] * scale['conversion'],
                           'eta': rates['eta'] * scale['conversion']})
            out[index] = compartmental_path(horizon_days, params)[-1]['adoption']
        return out
    return run


def analyse(horizon_days: int, parameters: Dict[str, float], samples: int = BASE_SAMPLES) -> Dict[str, object]:
    bounds = _bounds(parameters)
    result = sobol_indices(population_model(horizon_days, parameters), bounds, samples)
    rows = []
    for index, (name, kind, label) in enumerate(FACTORS):
        low, high = bounds[index]
        rows.append({'factor': name, 'kind': kind, 'label': label,
                     'range': [round(float(np.exp(low)), 3), round(float(np.exp(high)), 3)] if kind == 'assumption' else [round(low, 3), round(high, 3)],
                     'range_meaning': 'multiplier on the rate' if kind == 'assumption' else 'value',
                     'first_order': round(float(result['first'][index]), 3), 'total': round(float(result['total'][index]), 3),
                     'first_order_90': [round(float(v), 3) for v in result['first_ci'][:, index]],
                     'total_90': [round(float(v), 3) for v in result['total_ci'][:, index]]})
    rows.sort(key=lambda row: -row['total'])
    return {'output': f'adoption at day {horizon_days}', 'mean': round(result['mean'], 4),
            'spread': round(float(np.sqrt(result['variance'])), 4), 'runs': result['runs'], 'factors': rows,
            'method': ('Sobol indices (Saltelli sampling, Saltelli 2010 first-order and Jansen total-order estimators, '
                       f'scrambled Sobol sequence, seed {SEED}, {samples} base samples, 200 bootstrap resamples for 90% '
                       'intervals). Evidence inputs vary ±0.15 around their values; the tool\'s rate constants are each '
                       'scaled between half and double.'),
            'sentences': sentences(rows, horizon_days, result)}


def sentences(rows, horizon_days, result):
    top = rows[0]
    assumptions = sum(row['total'] for row in rows if row['kind'] == 'assumption')
    evidence = sum(row['total'] for row in rows if row['kind'] == 'evidence')
    out = [f"When every input and assumption varies at once, adoption at day {horizon_days} averages {result['mean']:.3f} "
           f"with a spread (standard deviation) of {np.sqrt(result['variance']):.3f}.",
           f"The largest share of that variation involves the {top['label']} (total index {top['total']}, alone "
           f"{top['first_order']}).",
           (f"The tool's own rate assumptions account for more of it (total indices summing to {assumptions:.2f}) than the "
            f"evidence inputs ({evidence:.2f}): pinning down those rates with real data would sharpen the result more than "
            'adding notes.' if assumptions > evidence else
            f"The evidence inputs account for more of it (total indices summing to {evidence:.2f}) than the tool's rate "
            f"assumptions ({assumptions:.2f}): better evidence would sharpen the result most.")]
    # Only where the first-order interval lies clearly below the total: the first-order estimate is the noisier one.
    interacting = [row['label'] for row in rows if row['first_order_90'][1] < row['total'] - 0.02]
    if interacting:
        out.append('These act mostly together with other factors rather than alone: ' + ', '.join(interacting) + '.')
    return out

"""Network agent-based model: households on an assumed social network, adopting through media and neighbours.

Each household is adopting or not. Every day a non-adopter adopts with a hazard from media (as in the mean-field proxy)
plus a hazard from its neighbours, proportional to the share of its neighbours who already adopted, plus an outreach
hazard set by intervention_strength (read as the compartmental model reads it, see intervention_hazard); an adopter stops
with the proxy's friction hazard. On a fully mixed population the neighbour share is the population share, so the
expected curve is the old proxy's curve (run_agent_based_proxy); the network is what changes it.

The network is an assumption, not measured data. Every run draws its own network and its own chance events from a fixed
seed, so results are reproducible; the band is the spread across runs (chance only), not uncertainty in the scores.
"""
from typing import Dict, List, Tuple

import numpy as np

TOPOLOGIES = {
    'village': 'villages of clustered neighbours with a few ties between villages',
    'small_world': 'one clustered population with some long-range ties',
    'scale_free': 'a few highly connected households and many with few ties',
    'well_mixed': 'everyone equally in contact with everyone, with no network structure',
}
DEFAULTS = {'households': 1000, 'village_size': 100, 'neighbours': 8, 'rewire': 0.1, 'between_village_ties': 1.0,
            'replicates': 20, 'seed': 7}


def _ring_lattice(nodes: np.ndarray, k: int, rewire: float, rng: np.random.Generator) -> List[Tuple[int, int]]:
    """Watts-Strogatz: each node tied to its k nearest ring neighbours, each tie rewired with probability `rewire`."""
    n, edges = len(nodes), set()
    for i in range(n):
        for step in range(1, k // 2 + 1):
            a, b = nodes[i], nodes[(i + step) % n]
            if rng.random() < rewire:
                b = nodes[rng.integers(n)]
                if b == a:
                    continue
            edges.add((min(a, b), max(a, b)))
    return list(edges)


def build_network(topology: str, households: int, rng: np.random.Generator, village_size: int = 100, neighbours: int = 8,
                  rewire: float = 0.1, between_village_ties: float = 1.0) -> Tuple[np.ndarray, np.ndarray]:
    """Undirected network as (source, target) arrays listing every tie in both directions."""
    ids = np.arange(households)
    if topology == 'village':
        edges = []
        for start in range(0, households, village_size):
            edges += _ring_lattice(ids[start:start + village_size], neighbours, rewire, rng)
        villages = ids // village_size
        for _ in range(int(households * between_village_ties / 2)):
            a, b = rng.integers(households, size=2)
            if villages[a] != villages[b]:
                edges.append((min(a, b), max(a, b)))
    elif topology == 'small_world':
        edges = _ring_lattice(ids, neighbours, rewire, rng)
    elif topology == 'scale_free':
        m = max(1, neighbours // 2)  # Barabasi-Albert: each newcomer ties to m households, preferring well-connected ones
        edges, targets = [], list(range(m))
        for new in range(m, households):
            chosen = set()
            while len(chosen) < m:
                chosen.add(targets[rng.integers(len(targets))])
            edges += [(c, new) for c in chosen]
            targets += list(chosen) + [new] * m
    else:
        raise ValueError(f'Unknown topology {topology!r}; known: {", ".join(TOPOLOGIES)}')
    pairs = np.array(sorted(set(edges)), dtype=np.int64).reshape(-1, 2)
    return np.concatenate([pairs[:, 0], pairs[:, 1]]), np.concatenate([pairs[:, 1], pairs[:, 0]])


def describe(source: np.ndarray, target: np.ndarray, households: int) -> Dict[str, float]:
    """Mean ties per household and clustering (share of a household's neighbour pairs who are tied to each other)."""
    neighbours = [set() for _ in range(households)]
    for a, b in zip(source.tolist(), target.tolist()):
        neighbours[a].add(b)
    local = []
    for linked in neighbours:
        k = len(linked)
        if k >= 2:
            ties = sum(len(neighbours[a] & linked) for a in linked) / 2
            local.append(ties / (k * (k - 1) / 2))
    degrees = np.array([len(linked) for linked in neighbours])
    return {'mean_ties': round(float(degrees.mean()), 2), 'max_ties': int(degrees.max()),
            'clustering': round(float(np.mean(local)) if local else 0.0, 3)}


def settings(parameters: Dict[str, float]) -> Dict[str, object]:
    out = {key: parameters.get(f'network_{key}', value) for key, value in DEFAULTS.items()}
    out['topology'] = parameters.get('network_topology', 'village')
    out['contagion'] = parameters.get('network_contagion', 'simple')
    for key in ('households', 'village_size', 'neighbours', 'replicates', 'seed'):
        out[key] = int(out[key])
    return out


# intervention_strength in run_compartmental_model (modelling.py) opens two routes from not adopting into adopting
# (adoption there is T + I + R): susceptible -> inoculated, 0.020 x strength per day (part of iota), and misinformed ->
# truth-aligned, 0.012 x strength per day (part of rho). Its third use, 0.018 x strength in gamma, moves inoculated ->
# durable, which stays inside adoption. Households here are only adopting or not, so a non-adopter gets the two rates
# mixed by that model's starting split of non-adopters into susceptible (S0) and misinformed (M0). Strength 0 adds
# nothing. Missing strength counts as 0 here (the compartmental model assumes 0.15), so runs that never set it keep
# their earlier results.
INTERVENTION_RATES = {'susceptible': 0.020, 'misinformed': 0.012}


def intervention_hazard(parameters: Dict[str, float]) -> float:
    """Daily chance, per non-adopting household, of adopting through the intervention lever."""
    clamp = lambda value: max(0.0, min(1.0, float(value)))
    strength = clamp(parameters.get('intervention_strength', 0.0))
    if strength == 0.0:
        return 0.0
    initial, barrier = clamp(parameters.get('initial_adoption', 0.10)), clamp(parameters.get('barrier_score', 0.35))
    susceptible = max(0.0, float(parameters.get('S0', max(0.05, 0.72 - initial * 0.30))))
    misinformed = max(0.0, float(parameters.get('M0', 0.10 + barrier * 0.12
                                                + clamp(parameters.get('misinformation_risk', 0.0)) * 0.08)))
    share = susceptible / ((susceptible + misinformed) or 1.0)
    return strength * (INTERVENTION_RATES['susceptible'] * share + INTERVENTION_RATES['misinformed'] * (1.0 - share))


def rates(parameters: Dict[str, float]) -> Dict[str, float]:
    """The mean-field proxy's media and friction terms, so both models read the same parameters the same way, plus the
    intervention term (zero unless intervention_strength is set)."""
    clamp = lambda value: max(0.0, min(1.0, float(value)))
    inoculation = clamp(parameters.get('inoculation_strength', 0.0))
    messenger = clamp(parameters.get('trusted_messenger_fit', 0.0))
    return {
        'initial_adoption': float(parameters.get('initial_adoption', 0.10)),
        'peer': float(parameters.get('peer_effect', 0.08)),
        'media': (float(parameters.get('media_effect', 0.05)) + inoculation * 0.035 + messenger * 0.020)
                 * float(parameters.get('trust_score', 0.60)),
        'friction': float(parameters.get('barrier_score', 0.35)) * 0.025
                    + clamp(parameters.get('misinformation_risk', 0.0)) * 0.008
                    + clamp(parameters.get('reactance_penalty', 0.0)) * 0.010,
        'intervention': intervention_hazard(parameters),
    }


def simulate_runs(horizon_days: int, parameters: Dict[str, float]) -> Dict[str, np.ndarray]:
    """Per-run curves (runs x days). Runs are seeded the same way for any parameters, so two settings compared run for
    run share their networks and chance events."""
    s, r = settings(parameters), rates(parameters)
    n, runs = s['households'], s['replicates']
    adoption = np.zeros((runs, horizon_days))
    peer_flow = np.zeros((runs, horizon_days))
    media_flow = np.zeros((runs, horizon_days))
    root = np.random.default_rng(s['seed'])
    for run in range(runs):
        rng = np.random.default_rng(root.integers(2 ** 63))
        if s['topology'] == 'well_mixed':
            source = target = None
            degree = np.full(n, n - 1.0)
        else:
            source, target = build_network(s['topology'], n, rng, s['village_size'], s['neighbours'], s['rewire'],
                                           s['between_village_ties'])
            degree = np.maximum(np.bincount(source, minlength=n), 1).astype(float)
        adopted = rng.random(n) < r['initial_adoption']
        drop_probability = min(1.0, r['friction'])  # daily rates used as daily probabilities, as in the proxy
        for day in range(horizon_days):
            if source is None:
                adopting_neighbours = np.full(n, float(adopted.sum())) - adopted
            else:
                adopting_neighbours = np.bincount(source, weights=adopted[target].astype(float), minlength=n)
            peer_hazard = r['peer'] * adopting_neighbours / degree
            if s['contagion'] == 'complex':  # neighbours persuade only once at least two of them have adopted
                peer_hazard = np.where(adopting_neighbours >= 2, peer_hazard, 0.0)
            waiting = ~adopted
            adopt = waiting & (rng.random(n) < np.minimum(1.0, peer_hazard + r['media'] + r['intervention']))
            drop = adopted & (rng.random(n) < drop_probability)
            peer_flow[run, day] = float((peer_hazard * waiting).mean())
            media_flow[run, day] = r['media'] * float(waiting.mean())
            adopted = (adopted | adopt) & ~drop
            adoption[run, day] = adopted.mean()
    return {'adoption': adoption, 'peer': peer_flow, 'media': media_flow}


def run_network_model(horizon_days: int, parameters: Dict[str, float]) -> List[Dict[str, float]]:
    runs = simulate_runs(horizon_days, parameters)
    adoption = runs['adoption']
    mean, low, high = adoption.mean(axis=0), np.percentile(adoption, 10, axis=0), np.percentile(adoption, 90, axis=0)
    return [{'day': float(day), 'adoption': float(mean[day]), 'adoption_lower': float(low[day]),
             'adoption_upper': float(high[day]), 'peer_pressure': float(runs['peer'][:, day].mean()),
             'media_pressure': float(runs['media'][:, day].mean()),
             'inoculation_pressure': float(parameters.get('inoculation_strength', 0.0)),
             'reactance_penalty': float(parameters.get('reactance_penalty', 0.0))}
            for day in range(horizon_days)]


# Network variants a conclusion is checked against: every assumed shape, with one or two adopting neighbours needed.
VARIANTS = [('well_mixed', 'simple')] + [(topology, contagion) for topology in ('village', 'small_world', 'scale_free')
                                         for contagion in ('simple', 'complex')]
CONTAGION = {'simple': 'where one adopting neighbour can persuade', 'complex': 'where two adopting neighbours are needed'}
SPREAD_LIMIT = 0.10  # largest spread in average adoption across variants that still counts as "holds"
CLEAR_DIFFERENCE = 0.01  # smallest average difference between two settings that counts as a difference at all


def _half_day(curve: np.ndarray):
    reached = np.nonzero(curve >= 0.5)[0]
    return int(reached[0]) + 1 if len(reached) else None


def robustness(horizon_days: int, parameters: Dict[str, float], alternative: Dict[str, float] | None = None) -> Dict[str, object]:
    """Re-run one scenario (or a comparison of two settings) on every network variant and say whether it holds.

    The measure is average adoption over the period: final adoption often saturates near the same level, while the
    average still shows how fast adoption came. With `alternative` (parameter changes), each variant compares the two
    settings run for run, on the same networks and chance events."""
    rows = []
    for topology, contagion in VARIANTS:
        base_params = {**parameters, 'network_topology': topology, 'network_contagion': contagion}
        base = simulate_runs(horizon_days, base_params)['adoption']
        row = {'topology': topology, 'contagion': contagion,
               'label': f"{TOPOLOGIES[topology]}, {CONTAGION[contagion]}" if topology != 'well_mixed' else TOPOLOGIES[topology],
               'average_adoption': round(float(base.mean()), 4), 'final_adoption': round(float(base[:, -1].mean()), 4),
               'half_adopted_day': _half_day(base.mean(axis=0))}
        if alternative:
            other = simulate_runs(horizon_days, {**base_params, **alternative})['adoption']
            per_run = other.mean(axis=1) - base.mean(axis=1)
            low, high = float(np.percentile(per_run, 10)), float(np.percentile(per_run, 90))
            mean = float(per_run.mean())
            direction = ('higher' if low > 0 and mean >= CLEAR_DIFFERENCE else
                         'lower' if high < 0 and mean <= -CLEAR_DIFFERENCE else 'no clear difference')
            row.update({'alternative_average_adoption': round(float(other.mean()), 4), 'difference': round(mean, 4),
                        'difference_band': [round(low, 4), round(high, 4)], 'direction': direction})
        rows.append(row)
    averages = [row['average_adoption'] for row in rows]
    out = {'measure': 'average adoption over the period (0 to 1)', 'horizon_days': horizon_days, 'variants': rows,
           'spread': round(max(averages) - min(averages), 4), 'spread_limit': SPREAD_LIMIT,
           'lowest': min(rows, key=lambda row: row['average_adoption'])['label'],
           'highest': max(rows, key=lambda row: row['average_adoption'])['label'],
           'status': 'assumed networks, not measured; a check of the model, not of the world'}
    out['level_verdict'] = 'holds' if out['spread'] <= SPREAD_LIMIT else 'depends on the network shape'
    if alternative:
        directions = {row['direction'] for row in rows}
        differences = [row['difference'] for row in rows]
        out['alternative'] = alternative
        out['difference_range'] = [min(differences), max(differences)]
        only = next(iter(directions)) if len(directions) == 1 else None
        out['comparison_verdict'] = ('holds: no clear difference in any network variant' if only == 'no clear difference' else
                                     f'holds: {only} in every network variant' if only else
                                     'flips: higher in some network variants and lower in others'
                                     if {'higher', 'lower'} <= directions else 'depends on the network shape: '
                                     + ', '.join(sorted(directions)))
    return out


def network_assumptions(parameters: Dict[str, float]) -> Dict[str, object]:
    """What the model assumed, with the measured shape of one network drawn the way the runs draw theirs."""
    s = settings(parameters)
    shape = {'mean_ties': float(s['households'] - 1), 'max_ties': s['households'] - 1, 'clustering': 1.0}
    if s['topology'] != 'well_mixed':
        rng = np.random.default_rng(np.random.default_rng(s['seed']).integers(2 ** 63))
        shape = describe(*build_network(s['topology'], s['households'], rng, s['village_size'], s['neighbours'],
                                        s['rewire'], s['between_village_ties']), s['households'])
    hazard = intervention_hazard(parameters)
    intervention = {'intervention_strength': float(parameters.get('intervention_strength', 0.0)),
                    'daily_adoption_chance_per_non_adopter': round(hazard, 6),
                    'mapping': 'intervention_strength enters as in the compartmental model: 0.020 x strength per day for '
                               'households counted as not yet persuaded and 0.012 x strength for those counted as '
                               'misinformed, mixed by that model\'s starting split; 0 adds nothing. An abstract lever, '
                               'not a description of any real programme.'}
    return {**s, 'topology_meaning': TOPOLOGIES[s['topology']], **shape, 'intervention': intervention,
            'band': f"10th to 90th percentile across {s['replicates']} runs: chance only, not uncertainty in the scores "
                    'or in the network shape',
            'status': 'assumed network, not measured; illustrative, not a forecast'}


def robustness_sentences(result: Dict[str, object]) -> List[str]:
    """Fixed wording for the check, so it is quoted rather than retold."""
    averages = [row['average_adoption'] for row in result['variants']]
    days, count = result['horizon_days'], len(result['variants'])
    if result['level_verdict'] == 'holds':
        sentences = [f"Checked on {count} assumed network shapes, average adoption over the {days} days stays between "
                     f"{min(averages)} and {max(averages)}: the level holds across network shapes (spread "
                     f"{result['spread']}, limit {result['spread_limit']})."]
    else:
        sentences = [f"Checked on {count} assumed network shapes, average adoption over the {days} days ranges from "
                     f"{min(averages)} ({result['lowest']}) to {max(averages)} ({result['highest']}): the level depends "
                     'on the network shape, so it should not be read as one number.']
    if 'comparison_verdict' in result:
        low, high = result['difference_range']
        directions = sorted({row['direction'] for row in result['variants']})
        lead = 'Compared with the baseline, the alternative setting'
        if directions in (['higher'], ['lower']):
            sentences.append(f"{lead} gives {directions[0]} average adoption in every network shape, so the direction "
                             f"holds; the size of the change ranges from {low} to {high}.")
        elif directions == ['no clear difference']:
            sentences.append(f"{lead} makes no clear difference in any network shape (changes from {low} to {high}).")
        elif {'higher', 'lower'} <= set(directions):
            sentences.append(f"{lead} gives higher average adoption in some network shapes and lower in others ({low} "
                             f"to {high}): the direction depends on how people are connected.")
        else:
            sentences.append(f"{lead} gives {' or '.join(directions)} average adoption depending on the network shape "
                             f"(changes from {low} to {high}).")
    return sentences

"""Network agent-based model: households on an assumed social network, adopting through media and neighbours.

Each household is adopting or not. Every day a non-adopter adopts with a hazard from media (as in the mean-field proxy)
plus a hazard from its neighbours, proportional to the share of its neighbours who already adopted; an adopter stops
with the proxy's friction hazard. On a fully mixed population the neighbour share is the population share, so the
expected curve is the old proxy's curve (run_agent_based_proxy); the network is what changes it.

Messenger seeding (optional, off by default): a campaign recruits a share of households as messengers, chosen by a
strategy (random, best connected, or holders of bridging ties). Messengers adopt at the start, keep using for the whole
period, and their adoption counts for more with their neighbours: 1 + 2 x trusted_messenger_fit ordinary neighbours.
With no seeding the model is exactly the one above.

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
            'replicates': 20, 'seed': 7, 'messenger_share': 0.02}

# Messenger seeding: who a campaign recruits, and how much a recruited messenger's adoption counts with neighbours.
SEEDING = {
    'none': 'no messengers recruited',
    'random': 'messengers recruited at random',
    'well_connected': 'the households with the most ties recruited as messengers',
    'bridges': 'the households with the most ties to other villages (on networks without villages, the most bridging '
               'ties: ties to households they share no neighbour with) recruited as messengers',
}
MESSENGER_WEIGHT = 2.0  # a messenger counts as 1 + MESSENGER_WEIGHT * trusted_messenger_fit ordinary adopting neighbours


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
    out['seeding'] = parameters.get('network_seeding', 'none')
    if out['seeding'] not in SEEDING:
        raise ValueError(f"Unknown seeding strategy {out['seeding']!r}; known: {', '.join(SEEDING)}")
    out['messenger_share'] = max(0.0, min(1.0, float(out['messenger_share'])))
    for key in ('households', 'village_size', 'neighbours', 'replicates', 'seed'):
        out[key] = int(out[key])
    return out


def rates(parameters: Dict[str, float]) -> Dict[str, float]:
    """The mean-field proxy's media and friction terms, so both models read the same parameters the same way."""
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
    }


def messenger_weight(parameters: Dict[str, float]) -> float:
    """How many ordinary adopting neighbours one messenger's adoption counts as: 1 + 2 x trusted_messenger_fit.

    trusted_messenger_fit (0 to 1, from the inoculation diagnosis) is read as how far the recruited messengers are people
    their neighbours already trust on this topic (a community health worker or a cooperative or church leader). At 0 a
    messenger persuades like any adopting neighbour; at 1, like three. An assumption of the tool, not an estimate."""
    return 1.0 + MESSENGER_WEIGHT * max(0.0, min(1.0, float(parameters.get('trusted_messenger_fit', 0.0))))


def local_bridges(source: np.ndarray, target: np.ndarray, households: int) -> np.ndarray:
    """Per household, the number of its ties that are local bridges: the two households share no neighbour.

    A cheap stand-in for betweenness (no shortest paths are computed): a local bridge is the only short route between
    the two sides it joins, so the households holding most of them sit between groups. On village networks these are
    mostly the ties between villages (and the few rewired ties inside a village); on the small-world network the
    long-range ties; on the scale-free network, with almost no clustering, most ties qualify, so it leans towards
    the well-connected households. Fully mixed, no tie is a local bridge. Bridge recruiting uses village membership
    first where villages exist, because rewired ties inside a village are local bridges too."""
    half = source < target
    a, b = source[half], target[half]
    linked = np.zeros((households, households), dtype=bool)
    linked[source, target] = True
    bridging = np.zeros(len(a), dtype=bool)
    for start in range(0, len(a), 2048):  # chunks keep the memory small on the Cloudflare container
        stop = start + 2048
        bridging[start:stop] = ~(linked[a[start:stop]] & linked[b[start:stop]]).any(axis=1)
    return np.bincount(a[bridging], minlength=households) + np.bincount(b[bridging], minlength=households)


def choose_messengers(strategy: str, count: int, degree: np.ndarray, rng: np.random.Generator,
                      source: np.ndarray | None = None, target: np.ndarray | None = None,
                      groups: np.ndarray | None = None) -> np.ndarray:
    """Indices of the `count` households a campaign recruits. Ties in the ranking are broken at random.

    Bridge recruiting ranks households by their ties to other villages when villages are known (`groups`), then by
    local bridges (see local_bridges), then by ties; without villages, by local bridges, then by ties."""
    n = len(degree)
    count = min(count, n)
    if strategy == 'none' or count <= 0:
        return np.zeros(0, dtype=np.int64)
    chance = rng.random(n)
    if strategy == 'random':
        order = np.argsort(chance)
    elif strategy == 'well_connected':
        order = np.lexsort((chance, -degree))
    elif strategy == 'bridges':
        bridges = np.zeros(n) if source is None else local_bridges(source, target, n)
        between = (np.zeros(n) if source is None or groups is None else
                   np.bincount(source[groups[source] != groups[target]], minlength=n))
        order = np.lexsort((chance, -degree, -bridges, -between))
    else:
        raise ValueError(f'Unknown seeding strategy {strategy!r}; known: {", ".join(SEEDING)}')
    return order[:count]


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
        committed = None
        if s['seeding'] != 'none':  # its own random stream, so every strategy shares the run's network and chance events
            chosen = choose_messengers(s['seeding'], int(round(s['messenger_share'] * n)), degree,
                                       np.random.default_rng([s['seed'], run, 1]), source, target,
                                       np.arange(n) // s['village_size'] if s['topology'] == 'village' else None)
            committed = np.zeros(n, dtype=bool)
            committed[chosen] = True
            adopted = adopted | committed
            influence_weight = np.where(committed, messenger_weight(parameters), 1.0)
        drop_probability = min(1.0, r['friction'])  # daily rates used as daily probabilities, as in the proxy
        for day in range(horizon_days):
            influence = adopted if committed is None else adopted * influence_weight
            if source is None:
                adopting_neighbours = np.full(n, float(influence.sum())) - influence
            else:
                adopting_neighbours = np.bincount(source, weights=influence[target].astype(float), minlength=n)
            peer_hazard = r['peer'] * adopting_neighbours / degree
            if s['contagion'] == 'complex':  # neighbours persuade only once at least two of them have adopted
                peer_hazard = np.where(adopting_neighbours >= 2, peer_hazard, 0.0)
            waiting = ~adopted
            adopt = waiting & (rng.random(n) < np.minimum(1.0, peer_hazard + r['media']))
            drop = adopted & (rng.random(n) < drop_probability)
            if committed is not None:  # messengers keep using for the whole campaign
                drop &= ~committed
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
    return {**s, 'topology_meaning': TOPOLOGIES[s['topology']], **shape,
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


# Messenger seeding comparison: every strategy on every network variant, on the same networks and chance events.
STRATEGIES = ('none', 'random', 'well_connected', 'bridges')
STRATEGY_LABELS = {'none': 'no messengers', 'random': 'random recruiting', 'well_connected': 'best-connected recruiting',
                   'bridges': 'bridge recruiting'}


def _variant_label(topology: str, contagion: str) -> str:
    return f"{TOPOLOGIES[topology]}, {CONTAGION[contagion]}" if topology != 'well_mixed' else TOPOLOGIES[topology]


SHAPES = {'village': 'village networks', 'small_world': 'small-world networks',
          'scale_free': 'networks with a few highly connected households'}


def _shapes(rows: List[Dict[str, object]]) -> str:
    """Short names for a set of networked variants: a shape with both contagion rules is named once."""
    parts = []
    for topology in SHAPES:
        rules = [row['contagion'] for row in rows if row['topology'] == topology]
        if len(rules) == 2:
            parts.append(SHAPES[topology])
        elif rules:
            parts.append(f"{SHAPES[topology]} {CONTAGION[rules[0]]}")
    return parts[0] if len(parts) == 1 else ', '.join(parts[:-1]) + ' and ' + parts[-1]


def _join(names: List[str]) -> str:
    labels = [STRATEGY_LABELS[name] for name in names]
    return labels[0] if len(labels) == 1 else ', '.join(labels[:-1]) + ' and ' + labels[-1]


def selection_overlap(parameters: Dict[str, float], topology: str) -> float | None:
    """Share of households both best-connected and bridge recruiting pick, on the first run's network of a shape."""
    s = settings({**parameters, 'network_topology': topology})
    if topology == 'well_mixed':
        return None
    rng = np.random.default_rng(np.random.default_rng(s['seed']).integers(2 ** 63))
    source, target = build_network(topology, s['households'], rng, s['village_size'], s['neighbours'], s['rewire'],
                                   s['between_village_ties'])
    degree = np.maximum(np.bincount(source, minlength=s['households']), 1).astype(float)
    count = int(round(s['messenger_share'] * s['households']))
    if count == 0:
        return None
    groups = np.arange(s['households']) // s['village_size'] if topology == 'village' else None
    picks = [set(choose_messengers(name, count, degree, np.random.default_rng([s['seed'], 0, 1]), source, target,
                                   groups).tolist())
             for name in ('well_connected', 'bridges')]
    return round(len(picks[0] & picks[1]) / count, 3)


def ranking_verdict(networked: List[Dict[str, object]], recruiting: List[str]) -> Tuple[str, str, List[str]]:
    """Whether the leading group of strategies is the same on every networked variant: (code, verdict, always leading)."""
    groups = {tuple(sorted(row['leading'])) for row in networked}
    always = [name for name in recruiting if all(name in row['leading'] for row in networked)]
    if all(not row['behind'] for row in networked):
        return 'no clear difference', 'no clear difference: no strategy is clearly behind another in any network shape', always
    if len(groups) == 1:
        return ('holds', f"holds: {_join(networked[0]['leading'])} lead in every network shape, clearly ahead of "
                         f"{_join(networked[0]['behind'])}", always)
    return 'depends on the network shape', 'depends on the network shape: the leading strategies differ between shapes', always


def seeding_comparison(horizon_days: int, parameters: Dict[str, float], strategies=STRATEGIES) -> Dict[str, object]:
    """Run each seeding strategy on each network variant and say whether their ranking holds across network shapes.

    Strategies are compared run for run (same networks, same chance events; only who is recruited differs). One
    strategy is clearly behind another when the gap is positive in at least 90% of runs and at least CLEAR_DIFFERENCE
    on average. Per variant, the leading group is the strategy with the highest average adoption and every strategy not
    clearly behind it. The verdict reads the networked variants only: fully mixed, who is recruited cannot matter (all
    strategies recruit alike there), so that row is a check of the setup."""
    strategies = list(dict.fromkeys(strategies))
    unknown = [name for name in strategies if name not in SEEDING]
    if unknown:
        raise ValueError(f'Unknown seeding strategy {unknown[0]!r}; known: {", ".join(SEEDING)}')
    recruiting = [name for name in strategies if name != 'none']
    if len(recruiting) < 2:
        raise ValueError('Compare at least two strategies that recruit messengers (random, well_connected, bridges).')
    s = settings(parameters)

    def clearly_behind(gap: np.ndarray) -> bool:
        return bool(np.percentile(gap, 10) > 0 and gap.mean() >= CLEAR_DIFFERENCE)

    rows = []
    for topology, contagion in VARIANTS:
        variant = {**parameters, 'network_topology': topology, 'network_contagion': contagion}
        per_run = {name: simulate_runs(horizon_days, {**variant, 'network_seeding': name})['adoption'].mean(axis=1)
                   for name in strategies}
        ranking = sorted(recruiting, key=lambda name: -per_run[name].mean())
        leader = ranking[0]
        leading = [name for name in ranking if name == leader or not clearly_behind(per_run[leader] - per_run[name])]
        behind = [name for name in ranking if name not in leading]
        row = {'topology': topology, 'contagion': contagion, 'label': _variant_label(topology, contagion),
               'average_adoption': {name: round(float(per_run[name].mean()), 4) for name in strategies},
               'ranking': ranking, 'leading': leading, 'behind': behind}
        if behind:  # how far the leading group is ahead: its lowest member against the best of the rest
            gap = per_run[leading[-1]] - per_run[behind[0]]
            row['gap'] = round(float(gap.mean()), 4)
            row['gap_band'] = [round(float(np.percentile(gap, 10)), 4), round(float(np.percentile(gap, 90)), 4)]
        if 'none' in strategies:
            row['gain_over_none'] = {name: round(float((per_run[name] - per_run['none']).mean()), 4) for name in recruiting}
        if {'well_connected', 'bridges'} <= set(strategies):
            row['same_households_share'] = selection_overlap(parameters, topology)
        rows.append(row)
    networked = [row for row in rows if row['topology'] != 'well_mixed']
    code, verdict, always = ranking_verdict(networked, recruiting)
    gaps = [row['gap'] for row in networked if 'gap' in row]
    out = {'measure': 'average adoption over the period (0 to 1)', 'horizon_days': horizon_days, 'strategies': strategies,
           'strategy_meaning': {name: SEEDING[name] for name in strategies},
           'messengers': int(round(s['messenger_share'] * s['households'])), 'messenger_share': s['messenger_share'],
           'households': s['households'], 'messenger_weight': round(messenger_weight(parameters), 3),
           'trusted_messenger_fit': round((messenger_weight(parameters) - 1.0) / MESSENGER_WEIGHT, 3),
           'variants': rows, 'verdict': code, 'ranking_verdict': verdict,
           'always_leading': always, 'same_order_everywhere': len({tuple(row['ranking']) for row in networked}) == 1,
           'gap_range': [min(gaps), max(gaps)] if gaps else None,
           'status': 'assumed networks, not measured; illustrative, not a forecast; options for discussion, not '
                     'recommendations'}
    if 'none' in strategies:
        out['gain_over_none_range'] = {name: [min(row['gain_over_none'][name] for row in networked),
                                              max(row['gain_over_none'][name] for row in networked)] for name in recruiting}
    return out


def seeding_sentences(result: Dict[str, object]) -> List[str]:
    """Fixed wording for the seeding comparison, so it is quoted rather than retold."""
    networked = [row for row in result['variants'] if row['topology'] != 'well_mixed']
    days = result['horizon_days']
    sentences = [f"On {len(networked)} assumed network shapes (assumed networks, not measured), a campaign recruiting "
                 f"{result['messengers']} messengers ({round(100 * result['messenger_share'], 1)}% of "
                 f"{result['households']} households), each counting as {result['messenger_weight']} ordinary neighbours, "
                 'was simulated with each recruiting strategy on the same networks and chance events. Illustrative, not '
                 'a forecast.']
    code = result['verdict']
    if code == 'holds':
        low, high = result['gap_range']
        leading, behind = networked[0]['leading'], networked[0]['behind']
        level = ', level with each other,' if len(leading) > 1 else ''
        sentences.append(f"{_join(leading).capitalize()}{level} {'have' if len(leading) > 1 else 'has'} the highest average "
                         f"adoption over the {days} days in every network shape, ahead of {_join(behind)} by {low} to "
                         f"{high}: the ranking holds across these assumed shapes.")
    elif code == 'depends on the network shape':
        low, high = result['gap_range']
        always = result['always_leading']
        others = []
        for name in [n for n in result['strategies'] if n != 'none' and n not in always]:
            level = [row for row in networked if name in row['leading']]
            behind = [row for row in networked if name not in row['leading']]
            others.append(f"{STRATEGY_LABELS[name]} is level with them on {_shapes(level)} and clearly behind on "
                          f"{_shapes(behind)}" if level else f"{STRATEGY_LABELS[name]} is clearly behind on {_shapes(behind)}")
        if always:
            lead = (f"{_join(always).capitalize()} {'are' if len(always) > 1 else 'is'} among the strategies with the highest "
                    f"average adoption over the {days} days on every network shape, while " + '; '.join(others))
        else:
            lead = (f"No strategy has the highest average adoption over the {days} days on every network shape: "
                    + '; '.join(f"{_join(row['leading'])} lead on {_shapes([row])}" for row in networked))
        sentences.append(f"{lead} (gaps from {low} to {high} where one is clearly behind). So whether it matters who is "
                         'recruited depends on how people are actually connected, which the model does not know.')
    else:
        sentences.append(f"No recruiting strategy is clearly ahead of the others in any network shape, in average adoption "
                         f"over the {days} days.")
    if 'gain_over_none_range' in result:
        parts = ', '.join(f"{lo} to {hi} with {STRATEGY_LABELS[name]}" for name, (lo, hi) in result['gain_over_none_range'].items())
        sentences.append(f'Compared with no messengers, average adoption is higher by {parts}, across the network shapes.')
    sentences.append('These are options for discussion, not recommendations: the messenger weight and the networks are '
                     'assumptions of the tool.')
    return sentences

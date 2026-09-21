"""Sweep design: pure functions so the same evidence text is planned identically for every run."""
import itertools

MAX_SWEEP_RUNS = 24
MAX_VALUES_PER_FACTOR = 12
FACTOR_BOUNDS = {'narrative_influence': (0.0, 1.0), 'initial_adoption': (0.0, 1.0),
                 'intervention_strength': (0.0, 1.0), 'horizon_days': (7, 365)}


def _label(varied):
    return ', '.join(f'{key}={value:g}' for key, value in varied.items()) or 'base'


def design(base, vary, mode):
    """Return [{'label', 'varied', 'values'}]; the first item is the base run in one_at_a_time mode."""
    if not vary:
        raise ValueError('vary must name at least one factor.')
    for factor, values in vary.items():
        if factor not in FACTOR_BOUNDS:
            raise ValueError(f'Cannot vary {factor!r}; choose from {sorted(FACTOR_BOUNDS)}.')
        if not values or len(values) > MAX_VALUES_PER_FACTOR or len(set(values)) != len(values):
            raise ValueError(f'{factor}: give 1-{MAX_VALUES_PER_FACTOR} distinct values.')
        low, high = FACTOR_BOUNDS[factor]
        if any(not low <= value <= high for value in values):
            raise ValueError(f'{factor}: every value must be between {low} and {high}.')
        if factor == 'horizon_days' and any(value != int(value) for value in values):
            raise ValueError('horizon_days must be whole days.')
    if mode == 'grid':
        names = list(vary)
        varied_sets = [dict(zip(names, combo)) for combo in itertools.product(*(vary[name] for name in names))]
    else:
        varied_sets = [{}] + [{factor: value} for factor, values in vary.items() for value in values
                              if value != base[factor]]
    if len(varied_sets) > MAX_SWEEP_RUNS:
        raise ValueError(f'This design needs {len(varied_sets)} runs; the limit is {MAX_SWEEP_RUNS}. '
                         'Use fewer values, or one_at_a_time mode.')
    return [{'label': _label(varied), 'varied': varied,
             'values': {**base, **{k: int(v) if k == 'horizon_days' else v for k, v in varied.items()}}}
            for varied in varied_sets]

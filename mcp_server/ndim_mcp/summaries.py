"""Pure functions that shrink engine runs into agent-sized, caveat-carrying summaries."""

NOTICE = ('Illustrative, uncalibrated model output from keyword-based encodings. Not a forecast, not a confidence '
          'interval, not empirical validation. Report it as exploratory and pending researcher review.')
TERMINAL = {'completed', 'failed', 'cancelled', 'interrupted'}
COMPARTMENTS = ('S', 'M', 'T', 'I', 'R')
REQUEST_FIELDS = ('model', 'horizon_days', 'intervention_strength', 'initial_adoption', 'narrative_influence',
                  'language', 'consent', 'profile')
# Factors that make two runs a controlled comparison only when exactly the varied one differs.
COMPARE_FACTORS = ('model', 'horizon_days', 'intervention_strength', 'initial_adoption', 'narrative_influence')


def trajectory_stats(trajectory):
    if not trajectory:
        return {'points': 0}
    last = trajectory[-1]
    peak = max(trajectory, key=lambda row: row['adoption'])
    stats = {'points': len(trajectory), 'initial_adoption': round(trajectory[0]['adoption'], 4),
             'final_adoption': round(last['adoption'], 4), 'peak_adoption': round(peak['adoption'], 4),
             'peak_day': peak['day']}
    if 'adoption_lower' in last:
        stats['final_heuristic_band'] = [round(last['adoption_lower'], 4), round(last['adoption_upper'], 4)]
    if all(name in last for name in COMPARTMENTS):
        stats['final_compartments'] = {name: round(last[name], 4) for name in COMPARTMENTS}
    return stats


def _scalars(output, keep_lists=('themes',)):
    """Small, human-readable fields only; drops long free text and nested structures."""
    return {key: value for key, value in output.items()
            if isinstance(value, (int, float, bool)) or value is None
            or (isinstance(value, str) and len(value) <= 300) or key in keep_lists}


def _simulations(run):
    return [(step, run['outputs'][step['id']]) for step in run['plan']
            if step['tool'] == 'simulate' and step['id'] in run['outputs']]


def _comparison(run):
    outputs = run['outputs']
    sims = {step['id']: output for step, output in _simulations(run)}
    result = {}
    if 'baseline' in sims and 'intervention' in sims:
        base = sims['baseline']['trajectory'][-1]['adoption']
        alt = sims['intervention']['trajectory'][-1]['adoption']
        result['baseline_vs_intervention'] = {
            'intervention_strength': sims['intervention']['parameters']['intervention_strength'],
            'baseline_final_adoption': round(base, 4), 'intervention_final_adoption': round(alt, 4),
            'delta_final_adoption': round(alt - base, 4),
            'note': 'Difference between two illustrative model endpoints; not an estimated treatment effect.'}
    sweep = [(step, output) for step, output in _simulations(run) if step['id'].startswith('sweep_')]
    if sweep:
        result['sensitivity_curve'] = [{'intervention_strength': output['parameters']['intervention_strength'],
                                        'final_adoption': round(output['trajectory'][-1]['adoption'], 4)}
                                       for _, output in sweep]
        result['sensitivity_note'] = 'Deterministic one-parameter grid; it shows sensitivity, not uncertainty.'
    return result if outputs else {}


def summarize_plan(run):
    execution = run['execution']
    request = run['request']
    blockers = run['blockers']
    return {
        'run_id': run['run_id'], 'workspace_id': run['workspace_id'], 'status': run['status'],
        'question': run['title'], 'workflow': run['skill'],
        'request': {key: request[key] for key in REQUEST_FIELDS if key in request},
        'steps': [{key: step[key] for key in ('id', 'tool', 'title', 'strength') if key in step} for step in run['plan']],
        'sensitivity_grid': execution['sensitivity_grid'], 'execution_profile': execution['profile'],
        'warnings': run['warnings'], 'blockers': blockers,
        'provenance': {'source_sha256': run['provenance']['source_sha256'],
                       'code_version': run['provenance']['code_version'], 'planner': run['provenance']['planner']},
        'next': ('BLOCKED: this plan cannot run. Explain the blocker to the researcher and create a corrected plan.'
                 if blockers else 'Show this plan to the researcher and obtain explicit approval before calling '
                                  'ndim_start_experiment. Do not approve on their behalf.')}


def summarize_run(run, include_trajectories=False):
    outputs = run['outputs']
    summary = {
        'run_id': run['run_id'], 'workspace_id': run['workspace_id'], 'status': run['status'],
        'question': run['title'], 'workflow': run['skill'],
        'progress': {'completed_steps': len(outputs), 'total_steps': len(run['plan']),
                     'pending': [step['id'] for step in run['plan'] if step['id'] not in outputs]},
        'request': {key: run['request'][key] for key in REQUEST_FIELDS if key in run['request']},
        'provenance': {'source_sha256': run['provenance']['source_sha256'],
                       'code_version': run['provenance']['code_version']},
        'recent_events': [{'type': event['type'], 'message': event['message'], 'tool_id': event.get('tool_id')}
                          for event in run['events'][-6:]],
        'review': run['review'], 'warnings': run['warnings'], 'notice': NOTICE,
    }
    if run['status'] not in TERMINAL and run['status'] != 'planned':
        summary['next'] = 'Still in progress: call ndim_wait_for_run.'
    elif run['status'] in {'failed', 'interrupted', 'cancelled'}:
        summary['next'] = ('Saved checkpoints are retained. Ask the researcher whether to resume with '
                           'ndim_resume_experiment, or create a new plan.')
    elif run['status'] == 'completed' and not run['review']:
        summary['next'] = ('Present the results with their limitations. The researcher, not the agent, records the '
                           'review that certifies the run was read.')
    if 'encode' in outputs:
        summary['encoding'] = _scalars(outputs['encode'])
    if 'diagnose' in outputs:
        summary['inoculation_diagnosis'] = _scalars(outputs['diagnose'])
    simulations = []
    for step, output in _simulations(run):
        entry = {'step_id': step['id'], 'intervention_strength': output['parameters']['intervention_strength'],
                 'model': output['model'], 'method_status': output['method_status'],
                 'stats': trajectory_stats(output['trajectory'])}
        if include_trajectories:
            entry['trajectory'] = output['trajectory']
        simulations.append(entry)
    if simulations:
        summary['simulations'] = simulations
        summary['model_parameters'] = _simulations(run)[0][1]['parameters'] | {'intervention_strength': 'per step'}
    if comparison := _comparison(run):
        summary['comparison'] = comparison
    if 'check' in outputs:
        summary['numerical_checks'] = {'passed': outputs['check']['passed'], 'checks': outputs['check']['checks'],
                                       'interpretation': outputs['check']['interpretation']}
    summary['brief_available'] = 'brief' in outputs and run['status'] == 'completed'
    return summary


def _headline(run):
    """Primary comparison metric: the intervention step when present, else the last simulation."""
    sims = _simulations(run)
    if not sims:
        return None
    step, output = next(((s, o) for s, o in sims if s['id'] == 'intervention'), sims[-1])
    stats = trajectory_stats(output['trajectory'])
    base = next((o for s, o in sims if s['id'] == 'baseline'), None)
    row = {'step_id': step['id'], 'final_adoption': stats['final_adoption'], 'peak_adoption': stats['peak_adoption'],
           'peak_day': stats['peak_day']}
    if base is not None and step['id'] != 'baseline':
        base_final = base['trajectory'][-1]['adoption']
        row['baseline_final_adoption'] = round(base_final, 4)
        # Subtract unrounded values so this agrees with summarize_run's comparison.
        row['delta_final_adoption'] = round(output['trajectory'][-1]['adoption'] - base_final, 4)
    return row


def compare_runs(runs, reference_id=None):
    rows, excluded = [], []
    for run in runs:
        headline = _headline(run) if run['status'] == 'completed' else None
        if headline is None:
            excluded.append({'run_id': run['run_id'], 'status': run['status'],
                             'reason': 'Only completed runs with a simulation step can be compared.'})
            continue
        encoded = run['outputs'].get('encode', {})
        rows.append({'run_id': run['run_id'], 'workflow': run['skill'],
                     **{key: run['request'][key] for key in COMPARE_FACTORS if key in run['request']},
                     'trust_score': encoded.get('trust_score'), 'barrier_score': encoded.get('adoption_barrier_score'),
                     'source_sha256': run['provenance']['source_sha256'][:12],
                     'code_version': run['provenance']['code_version'][:19], **headline})
    notes = []
    if len(rows) >= 2:
        varied = [key for key in COMPARE_FACTORS if len({row.get(key) for row in rows}) > 1]
        if len({row['source_sha256'] for row in rows}) > 1:
            notes.append('Runs use different source evidence, so encoded trust and barrier inputs differ. '
                         'This is not a controlled comparison of the varied parameters alone.')
        if len({row['code_version'] for row in rows}) > 1:
            notes.append('Runs were produced by different scientific code versions and should not be compared.')
        if len(varied) > 1:
            notes.append(f'More than one factor varies ({", ".join(varied)}); differences cannot be attributed to any one of them.')
        if len({row['model'] for row in rows}) > 1:
            notes.append('Runs use different model families; their endpoints are not directly comparable.')
        reference = next((row for row in rows if row['run_id'] == reference_id), None) if reference_id else None
        if reference_id and reference is None:
            notes.append('The reference run is not among the completed runs; comparing without a reference.')
        if reference is not None:
            # One-at-a-time design: every run may differ from the reference in exactly one factor.
            notes = [note for note in notes if not note.startswith('More than one factor')]
            for row in rows:
                row['varied_vs_reference'] = [key for key in COMPARE_FACTORS if row.get(key) != reference.get(key)]
            if any(len(row['varied_vs_reference']) > 1 for row in rows):
                notes.append('At least one run differs from the reference in more than one factor.')
            controlled = not notes and all(len(row['varied_vs_reference']) <= 1 for row in rows)
        else:
            controlled = not notes and len(varied) == 1
        comparability = {'varied_factors': varied, 'notes': notes, 'controlled': controlled,
                         'reference_run_id': reference['run_id'] if reference is not None else None}
    else:
        comparability = {'varied_factors': [], 'notes': ['Fewer than two comparable runs.'], 'controlled': False,
                         'reference_run_id': None}
    columns = ['run_id', *COMPARE_FACTORS, 'final_adoption', 'peak_adoption', 'peak_day', 'delta_final_adoption']
    table = ['| ' + ' | '.join(columns) + ' |', '|' + '---|' * len(columns)]
    for row in rows:
        table.append('| ' + ' | '.join('' if row.get(col) is None else str(row[col])[:8] if col == 'run_id' else str(row[col])
                                       for col in columns) + ' |')
    return {'rows': rows, 'excluded': excluded, 'comparability': comparability, 'markdown_table': '\n'.join(table),
            'notice': NOTICE}

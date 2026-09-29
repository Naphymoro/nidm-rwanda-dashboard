"""Pure functions that shrink engine runs into agent-sized, caveat-carrying summaries."""

NOTICE = ('Illustrative, uncalibrated model output from keyword-based encodings. Not a forecast, not a confidence '
          'interval, not empirical validation. Report it as exploratory and pending researcher review.')
# Keep in step with the skill's references/interpreting-results.md, "Allowed and forbidden wording".
REPORTING_RULES = ('When reporting: lead a scenario with comparison.baseline_vs_intervention.headline, quoted word for '
                   'word, then the evidence signals behind it, then the limitations, and close with its conclusion, '
                   'quoted word for word, as your only conclusion. Say "in the illustrative model, endpoint '
                   'adoption is X at day N", never "adoption will reach X". Call a delta the difference between two model '
                   'endpoints, never an effect of the intervention, and give it in adoption units or percentage points, '
                   'never as a percent. Never write that the intervention causes, drives, contributes to, improves, '
                   'increases or influences adoption, not even with "may", "could" or "suggests": the model cannot show '
                   'it. Write no recommendations, policy advice or programme suggestions; offer further analyses instead '
                   '(a sensitivity run, a shorter horizon, calibration against field data). Call scores what "the keyword heuristic scored this '
                   'narrative", never measured trust in a community. Never write validated, calibrated, confirmed, '
                   'significant or robust. Scope claims to this narrative and this model. Only speak of a peak when '
                   'stats.shape is "peaks_before_end"; when adoption rises to the last day there is no peak, so report '
                   'fastest_growth_day (when adoption grew fastest) instead. If both arms end near 1.0, say the model '
                   'saturated.')
TERMINAL = {'completed', 'failed', 'cancelled', 'interrupted'}
# Statuses from which each approval-gated action can proceed; checked before an approval is written to the audit log.
ELIGIBLE = {'start': {'planned'}, 'resume': {'failed', 'interrupted', 'cancelled'}}
# A live agent answered a new question with an old run's brief from ndim_list_runs, then "started" that completed run.
# The researcher chose to meet an old run with its matching tutorial, never with the old run itself.
EXISTING_RUNS = ('These are existing runs, possibly from other conversations or researchers. Never present one as the '
                 'answer to the researcher\'s question, and never show its results or brief (run ids are withheld here '
                 'for that reason; a researcher can paste one from the web app). When one matches their '
                 'question, offer its matching_tutorial instead: name the lesson, say in one sentence what it teaches, '
                 'and give its link. To answer their own question, plan a new experiment on their evidence '
                 '(ndim_plan_experiment). Never call ndim_start_experiment on a run you did not plan and show in this '
                 'conversation.')
COMPARTMENTS = ('S', 'M', 'T', 'I', 'R')
# The engine's own names (modelling.run_compartmental_model). Given only the letters, a live agent invented
# "Messenger", "Trust", "Influenced" and "Retained".
COMPARTMENT_NAMES = {'S': 'susceptible', 'M': 'misinformed', 'T': 'truth-aligned', 'I': 'inoculated',
                     'R': 'durable adoption belief'}
REQUEST_FIELDS = ('model', 'horizon_days', 'intervention_strength', 'initial_adoption', 'narrative_influence',
                  'language', 'consent', 'profile')
# Factors that make two runs a controlled comparison only when exactly the varied one differs.
COMPARE_FACTORS = ('model', 'horizon_days', 'intervention_strength', 'initial_adoption', 'narrative_influence')


def trajectory_stats(trajectory):
    """Endpoint statistics, plus a peak only where one exists.

    Adoption in these models usually rises to the horizon, so the maximum is the last day and a "peak" there is
    just the endpoint restated. The peak is reported only when adoption tops out before the end (at the 4-decimal
    precision reported); otherwise fastest_growth_day is the informative timing."""
    if not trajectory:
        return {'points': 0}
    last = trajectory[-1]
    final = round(last['adoption'], 4)
    peak = max(trajectory, key=lambda row: row['adoption'])  # first maximum on ties
    stats = {'points': len(trajectory), 'initial_adoption': round(trajectory[0]['adoption'], 4), 'final_adoption': final}
    levels = [round(row['adoption'], 4) for row in trajectory]
    if max(levels) == min(levels):
        stats['shape'] = 'flat'
    elif round(peak['adoption'], 4) > final:
        stats['shape'] = 'peaks_before_end'
        stats['peak_adoption'] = round(peak['adoption'], 4)
        stats['peak_day'] = peak['day']
    else:
        stats['shape'] = 'rises_to_end'
    steps = [(trajectory[i]['adoption'] - trajectory[i - 1]['adoption'], i) for i in range(1, len(trajectory))]
    if steps and (fastest := max(steps, key=lambda step: step[0]))[0] > 0:  # first day on ties
        stats['fastest_growth_day'] = trajectory[fastest[1]]['day']
        stats['fastest_growth'] = round(fastest[0], 4)
    if 'adoption_lower' in last:
        stats['final_heuristic_band'] = [round(last['adoption_lower'], 4), round(last['adoption_upper'], 4)]
    if all(name in last for name in COMPARTMENTS):
        stats['final_compartments'] = {name: round(last[name], 4) for name in COMPARTMENTS}
        stats['compartment_names'] = COMPARTMENT_NAMES
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
        last = sims['baseline']['trajectory'][-1]
        base, alt = last['adoption'], sims['intervention']['trajectory'][-1]['adoption']
        strength = sims['intervention']['parameters']['intervention_strength']
        delta = round(alt - base, 4)
        result['baseline_vs_intervention'] = {
            'intervention_strength': strength,
            'baseline_final_adoption': round(base, 4), 'intervention_final_adoption': round(alt, 4),
            'delta_final_adoption': delta,
            # A ready-made sentence: live agents paraphrased the numbers into causal claims and percents.
            'headline': (f'In the illustrative, uncalibrated model, endpoint adoption at day {last["day"]:g} is '
                         f'{base:.4f} in the baseline arm and {alt:.4f} in the intervention arm (intervention_strength '
                         f'{strength:g}). The difference between these two model endpoints is {delta:+.4f} '
                         f'({delta * 100:+.2f} percentage points); it is not an estimated effect of the intervention.'),
            # Agents given only the headline still closed with "X could lead to higher adoption"; give them the close too.
            'conclusion': ('This model cannot say whether the intervention would change real adoption. Within this '
                           'illustrative model and this one narrative, the only finding is the difference between two '
                           'model endpoints; testing it in reality would need field data and calibration.'),
            'note': 'Difference between two illustrative model endpoints; not an estimated treatment effect.'}
    sweep = [(step, output) for step, output in _simulations(run) if step['id'].startswith('sweep_')]
    if sweep:
        result['sensitivity_curve'] = [{'intervention_strength': output['parameters']['intervention_strength'],
                                        'final_adoption': round(output['trajectory'][-1]['adoption'], 4)}
                                       for _, output in sweep]
        result['sensitivity_note'] = 'Deterministic one-parameter grid; it shows sensitivity, not uncertainty.'
    return result if outputs else {}


DEFAULT_STRENGTH = 0.3  # the engine's own default for intervention_strength


def strength_note(run, strength_reason=None):
    """Why the plan uses this intervention_strength, phrased so it is true whoever picked the value.

    Live agents never said why they used 0.3. Asked to report who chose it, they answered inconsistently and once told
    the researcher it was their own choice when it was the default, so the note never attributes the value."""
    value = run['request']['intervention_strength']
    # Paraphrases keep a sentence's opening and drop its asides, so the default, when it applies, comes first.
    text = (f'Intervention strength {value:g} is ' + ('the tool\'s default, described only as "moderate": ' if value == DEFAULT_STRENGTH
            else '') + 'an assumption, not derived from the evidence or measured from the intervention.')
    if strength_reason:
        text += f' Reasoning given when planning: {strength_reason.rstrip(".")}.'
    return text + ' Confirm this value or give another before approving; a sensitivity run would show how the result depends on it.'


def intervention_mapping(run, strength_reason=None):
    """How the researcher's intervention enters the engine, and why its strength; None for evidence."""
    if run['skill'] not in {'scenario', 'sensitivity'}:
        return None
    lever = f'intervention_strength = {run["request"]["intervention_strength"]:g}'
    if grid := run['execution'].get('sensitivity_grid'):
        lever += ', plus a grid of ' + ', '.join(f'{value:g}' for value in grid)
    text = (f'The intervention in "{run["title"]}" is represented only by {lever}, an abstract 0-1 lever where 0 is '
            'the baseline. The engine does not model what the intervention actually is (for example how many health '
            'workers, prices, channels, reach or duration).')
    return text + ' ' + strength_note(run, strength_reason)


def summarize_plan(run, strength_reason=None):
    execution = run['execution']
    request = run['request']
    blockers = run['blockers']
    mapping = intervention_mapping(run, strength_reason)
    note = strength_note(run, strength_reason) if mapping else None
    # Live agents skipped this step when it lived only in SKILL.md, so the plan result states it and demands it; told
    # to relay the mapping "in your own words", one dropped why the strength was used, so that sentence is spelled out.
    ask = ('Show this plan to the researcher, quoting the question field exactly so they can confirm it is their '
           'question; if it differs from their words at all, say what changed and create a new plan. ' +
           ('Before asking for approval, tell them intervention_mapping in your own words' if mapping else '') +
           (f', and include this sentence copied character for character: "{note}" ' if note else '') +
           'Obtain explicit approval before calling ndim_start_experiment. Do not approve on their behalf.')
    return {
        'run_id': run['run_id'], 'workspace_id': run['workspace_id'], 'status': run['status'],
        'question': run['title'], 'workflow': run['skill'],
        'request': {key: request[key] for key in REQUEST_FIELDS if key in request},
        'steps': [{key: step[key] for key in ('id', 'tool', 'title', 'strength') if key in step} for step in run['plan']],
        'sensitivity_grid': execution['sensitivity_grid'], 'execution_profile': execution['profile'],
        'intervention_mapping': mapping, 'warnings': run['warnings'], 'blockers': blockers,
        'provenance': {'source_sha256': run['provenance']['source_sha256'],
                       'code_version': run['provenance']['code_version'], 'planner': run['provenance']['planner']},
        'next': ('BLOCKED: this plan cannot run. Explain the blocker to the researcher and create a corrected plan.'
                 if blockers else ask)}


def evidence_signals(outputs):
    """One sentence on the encoded inputs that drive the simulation, or None before encoding has run."""
    encoded, diagnosed = outputs.get('encode'), outputs.get('diagnose') or {}
    if not encoded or encoded.get('trust_score') is None or encoded.get('adoption_barrier_score') is None:
        return None
    text = (f'The keyword heuristic scored this narrative {encoded["trust_score"]:.3f} on trust and '
            f'{encoded["adoption_barrier_score"]:.3f} on adoption barriers')
    if diagnosed.get('misinformation_risk_score') is not None:
        text += f', and the inoculation heuristic scored its misinformation risk {diagnosed["misinformation_risk_score"]:.3f}'
        if diagnosed.get('threat_type'):
            text += f' (flagged threat: {diagnosed["threat_type"].replace("_", " ")}, pending human review)'
    text += '.'
    if encoded.get('themes'):
        text += ' Themes found: ' + ', '.join(theme.replace('_', ' ') for theme in encoded['themes']) + '.'
    return text + (' These scores come from keywords in one English text, not from measurements in a community, and '
                   'they set the same trust, barrier and misinformation inputs for every simulated arm.')


def _verbatim(run):
    """The report's fixed content, spelled out inside the instruction itself.

    Live agents told to quote comparison.baseline_vs_intervention.headline paraphrased it instead, and skipped the
    evidence signals the rules asked for; text placed in the instruction gets copied, a field reference gets reworded.
    Only the headline and conclusion must be exact: demanding a third, number-heavy quote made agents turn it into
    bullets and loosen the other two as well, so the evidence may be reformatted as long as numbers and caveat stay."""
    comparison = _comparison(run).get('baseline_vs_intervention')
    signals = evidence_signals(run['outputs'])
    parts = []
    if comparison:
        parts.append(f'Open your report with this sentence, copied character for character: "{comparison["headline"]}"')
    if signals:
        parts.append(f'{"Then" if comparison else "First"} report the evidence signals behind it (a list is fine), keeping '
                     f'every number and the caveat that they come from keywords in one English text: {signals}')
    if comparison:
        parts.append(f'End your report with this sentence, copied character for character: "{comparison["conclusion"]}" '
                     'Do not reword, round or shorten the opening or closing sentence.')
    return ' '.join(parts) + ' ' if parts else ''


def _created(run):
    return f'on {run["created_at"][:16].replace("T", " ")} UTC' if run.get('created_at') else 'earlier'


def tutorial(lesson, workspace_id, public_url):
    """The engine lesson that teaches a workflow, with a link the researcher can open."""
    return {'lesson_id': lesson['id'], 'title': f'Lesson {lesson["number"]}: {lesson["title"]}',
            'teaches': lesson['subtitle'], 'duration': lesson['duration'],
            'link': f'{public_url}/academy?workspace={workspace_id}&lesson={lesson["id"]}'}


def tutorial_offer(found):
    if not found:
        return 'Offer to plan a new experiment on their own evidence.'
    return (f'Offer the matching tutorial instead, "{found["title"]}" ({found["teaches"]}, {found["duration"]}): '
            f'{found["link"]} . You can also run it here: plan it with lesson_id="{found["lesson_id"]}" on the synthetic '
            'sample from ndim_list_lessons. Then offer to plan a new experiment on their own evidence.')


def existing_run_note(run, found=None):
    return (f'This is run {run["run_id"]}, created {_created(run)} for the question "{run["title"]}". Unless it was '
            'planned and approved in this conversation, do not present it or its brief as an answer: tell the researcher '
            f'only that an earlier run exists (from that date). {tutorial_offer(found)}')


def ineligible(run, action, found=None):
    """Why an approval-gated action cannot proceed on this run, and what to do instead."""
    status = run['status']
    if status == 'completed':
        return (f'Run {run["run_id"]} already completed ({_created(run)}); nothing was started and no approval was '
                'recorded. Do not present that earlier run as an answer. ' + tutorial_offer(found))
    if action == 'start' and status in ELIGIBLE['resume']:
        return (f'Run {run["run_id"]} is {status}; nothing was started and no approval was recorded. Ask the researcher '
                'whether to resume it with ndim_resume_experiment, or create a new plan.')
    if action == 'resume' and status == 'planned':
        return (f'Run {run["run_id"]} has not run yet, so it cannot be resumed; no approval was recorded. Start it '
                'with ndim_start_experiment once the researcher has approved it.')
    if status not in TERMINAL and status != 'planned':
        return f'Run {run["run_id"]} is already {status}; call ndim_wait_for_run. No approval was recorded.'
    return (f'Run {run["run_id"]} is {status}, so this action is not possible; no approval was recorded. '
            'Create a new plan with ndim_plan_experiment.')


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
                           'review that certifies the run was read. ' + _verbatim(run) + REPORTING_RULES)
    if 'encode' in outputs:
        summary['encoding'] = _scalars(outputs['encode'])
        summary['evidence_signals'] = evidence_signals(outputs)
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
    row = {'step_id': step['id'], 'final_adoption': stats['final_adoption'], 'shape': stats['shape'],
           'peak_adoption': stats.get('peak_adoption'), 'peak_day': stats.get('peak_day'),
           'fastest_growth_day': stats.get('fastest_growth_day')}
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
    columns = ['run_id', *COMPARE_FACTORS, 'final_adoption', 'shape', 'peak_day', 'fastest_growth_day',
               'delta_final_adoption']
    table = ['| ' + ' | '.join(columns) + ' |', '|' + '---|' * len(columns)]
    for row in rows:
        table.append('| ' + ' | '.join('' if row.get(col) is None else str(row[col])[:8] if col == 'run_id' else str(row[col])
                                       for col in columns) + ' |')
    return {'rows': rows, 'excluded': excluded, 'comparability': comparability, 'markdown_table': '\n'.join(table),
            'notice': NOTICE}

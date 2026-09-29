"""Agent-sized views of the engine's 13-stage journey, and the guidance that walks a researcher through it.

The engine returns full curves and every record; these functions keep the numbers a researcher needs, the limits
that go with them, and a `next` instruction that makes the agent explain each stage and ask before moving on.
"""
from .summaries import trajectory_stats

# What each stage's numbers are, in the words an agent should pass on. Keep in step with the engine's STAGES.
LIMITS = {
    'intake': 'Records are stored as given; nothing has been scored yet.',
    'gate': 'The gate checks metadata and patterns only. It does not judge whether a record is true or representative.',
    'repository': 'Only accepted records reach any model. Decisions are frozen once encoding runs.',
    'encoding': 'Scores come from English keywords in each record: interpretations for review, not measurements of '
                'trust or barriers in a community.',
    'compartmental': 'Illustrative, uncalibrated curve driven by the keyword scores. Not a forecast.',
    'agents': 'A deterministic proxy for household behaviour, not a simulation of real households. Not a forecast.',
    'digital': 'Re-runs the hybrid model from the researcher\'s field observations. It is still uncalibrated: one '
               'observed level does not fit the model to reality.',
    'bayes': 'The signal update treats keyword scores as pseudo-observations; the number of pseudo-trials is a tool '
             'convention. An adoption curve is fitted only to an observed series the researcher supplied.',
    'rl': 'The ranking restates the tool\'s fixed assumed lifts and costs; no data estimated them. It is not advice '
          'on which action to take.',
    'regional': 'Averages of keyword scores per place. A place with one or two records says little about the place. '
                'The rule of thumb is a threshold rule, not a model result.',
    'graph': 'Links show that a place, a theme and a signal occur together in the records. They are not causal.',
    'inoculation': 'Message drafts need human review before any use with people. The before/during/after curves use a '
                   'fixed lift formula; they do not model message effects.',
    'policy': 'A draft for the research team\'s review: options for discussion, not recommendations. The evidence grade '
              'and readiness come from the number of records and encoder confidence only.',
}

# The experiment REPORTING_RULES, minus the scenario headline these stages do not have, plus the stages that look like advice.
JOURNEY_RULES = ('When reporting a stage: say "in the illustrative model, adoption is X at day N", never "adoption will '
                 'reach X". Never write that anything causes, drives, contributes to, improves, increases or influences '
                 'adoption, not even with "may", "could" or "suggests": the models cannot show it. Write no '
                 'recommendations or policy advice. The RL ranking, the regional rule of thumb and the policy output are '
                 'the tool\'s assumptions and options for discussion; say so, and never present them as what to do. Call '
                 'scores what "the keyword heuristic scored these records", never measured trust in a community. Never '
                 'write validated, calibrated, confirmed, significant or robust. Never call any stage\'s output "recommendations", '
                 'including the policy output: it is a draft of options for discussion. Only speak of a peak when stats.shape is '
                 '"peaks_before_end"; otherwise report fastest_growth_day. If adoption ends near 1.0, say the model '
                 'saturated, so the curve says little about differences.')

GUIDE = ('Guide the researcher one stage at a time. After each stage, explain in plain words what it did, the key '
         'numbers and their limits, then name the next stage and what it does, and ask whether to continue. Do not run '
         'the next stage until they say so. Stages marked researcher_decision need the researcher\'s own words '
         '(approval_statement) and, for the digital twin, their own field observations: ask for them, never invent or '
         'default them.')

# The phases in words that claim nothing the stages cannot do (no "validate", no "actionable").
JOURNEY_PHASES = ('1. Evidence: your field notes are stored as given, checked for metadata and personal data, and you '
                  'accept or reject each one. 2. Encode: an English keyword heuristic scores trust, barriers and '
                  'themes. 3. Model: illustrative, uncalibrated adoption curves from those scores. 4. Twin: the model '
                  're-run from your own field observations, then a signal update and a ranking of actions under the '
                  'tool\'s fixed assumptions. 5. Strategy: place summaries, a map of which themes occur together, and '
                  'message drafts for your review. 6. Export: a policy draft of options for your team to discuss, not '
                  'recommendations.')

SATURATED = 0.9  # final adoption at or above this: the curve has little room left to show differences


def _curve(output):
    view = {'model': output['model'], 'horizon_days': output['horizon_days'], 'method_status': output['method_status'],
            'stats': trajectory_stats(output['trajectory'])}
    if view['stats'].get('final_adoption', 0) >= SATURATED:
        # A live agent reported 0.93 and 0.91 endpoints without saying the model had saturated.
        view['saturation'] = (f"Adoption ends at {view['stats']['final_adoption']} of 1.0: the model has saturated, so this "
                              'curve says little about differences between settings. A shorter horizon_days would show more.')
    return view


def stage_view(stage, output):
    """Compact view of one stage's output."""
    if stage == 'encoding':
        diagnoses = {item['narrative_id']: item for item in output['diagnoses']}
        return {'mean': {key: None if value is None else round(value, 3) for key, value in output['mean'].items()},
                'themes': output['themes'],
                'records': [{'record_id': item['narrative_id'], 'trust': item['trust_score'], 'barrier': item['adoption_barrier_score'],
                             'confidence': item['confidence'], 'themes': item['themes'],
                             'threat_type': diagnoses.get(item['narrative_id'], {}).get('threat_type'),
                             'misinformation_risk': diagnoses.get(item['narrative_id'], {}).get('misinformation_risk_score')}
                            for item in output['encoded']],
                'method': output['method']}
    if stage in {'compartmental', 'agents'}:
        return _curve(output) | {'inputs': {key: round(output['parameters'][key], 4) for key in
                                            ('trust_score', 'barrier_score', 'narrative_influence', 'intervention_strength')}}
    if stage == 'digital':
        return _curve(output) | {'feedback': output['feedback']}
    if stage == 'bayes':
        view = {key: output[key] for key in ('priors', 'pseudo_trials', 'signal_update_note')}
        view |= {'trust_mean': round(output['trust_mean'], 4), 'barrier_mean': round(output['barrier_mean'], 4)}
        if output['adoption_fit']:
            fit = output['adoption_fit']
            view['adoption_fit'] = {'final_mean': round(fit['trajectory']['mean'][-1], 4),
                                    'final_band': [round(fit['trajectory']['lower_90'][-1], 4), round(fit['trajectory']['upper_90'][-1], 4)],
                                    'method': fit['method']}
        else:
            view['adoption_fit'] = None
            view['adoption_fit_note'] = output['adoption_fit_note']
        return view
    if stage == 'rl':
        return {key: output[key] for key in ('ranking', 'top_action', 'formula', 'method')} | {
            'trust_used': round(output['trust_used'], 4), 'barrier_used': round(output['barrier_used'], 4)}
    if stage in {'regional', 'graph'}:
        return output
    if stage == 'inoculation':
        view = {key: output[key] for key in ('audience', 'tone', 'messenger', 'drafts', 'review_status', 'curve_method')}
        view['estimated_strength'] = round(output['estimated_strength'], 4)
        view['curves'] = {model: {phase: trajectory_stats(rows)['final_adoption'] for phase, rows in phases.items()}
                          for model, phases in output['curves'].items()}
        view['curves_note'] = 'Final adoption per model before, during and after the message, from the fixed lift formula.'
        if any(value >= SATURATED for phases in view['curves'].values() for value in phases.values()):
            view['curves_note'] += (' The curves are saturated (0.9 or more), so the gaps between them are small by '
                                    'construction; do not read them as a small message effect.')
        if output.get('twin'):
            view['twin_with_inoculation'] = _curve(output['twin'])
        return view
    if stage == 'policy':
        return {key: output[key] for key in ('evidence_grade', 'summary', 'status', 'limits', 'code_version')} | {
            'numerical_checks_passed': output['checks']['passed']}
    return output


def journey_view(body):
    """Progress, records and (when present) one stage's result, with the instruction for the agent."""
    stages = {row['id']: row for row in body['stages']}
    view = {key: body[key] for key in ('journey_id', 'workspace_id', 'question', 'country', 'created_at', 'next_stage')}
    view['progress'] = [f"{row['number']:>2}. {row['title']} ({row['phase']}): {row['status']}"
                        + (' [optional]' if row['optional'] else '') + (' [researcher decision]' if row['researcher_decision'] else '')
                        for row in body['stages']]
    view['records'] = [{key: record[key] for key in ('record_id', 'admin_unit', 'source_name', 'period', 'consent', 'excerpt')}
                       | {'gate': record['gate']['gate'], 'gate_flags': record['gate']['blockers'] + record['gate']['warnings']
                          + record['gate']['pii_flags'] + record['gate']['quality_flags'],
                          'decision': (record['review'] or {}).get('decision')}
                       for record in body['records']]
    parts = []
    if stage := body.get('stage'):
        view['stage'] = stage
        view['result'] = stage_view(stage, body['output'])
        view['limits'] = LIMITS[stage]
        if body.get('cleared_later_stages'):
            view['cleared_later_stages'] = body['cleared_later_stages']
            parts.append('Re-running this stage cleared these later stages, which must be run again: '
                         + ', '.join(body['cleared_later_stages']) + '.')
        parts.append(f"Explain the {stages[stage]['title']} result in plain words with its limits (the limits field).")
    if undecided := body.get('undecided'):
        parts.append(f'{len(undecided)} record(s) still need an accept or reject decision from the researcher before '
                     'the repository is complete.')
    nxt = body.get('next_stage')
    if nxt:
        row = stages[nxt]
        parts.append(f"Next stage: {row['number']}. {row['title']}." + (
            ' It is a researcher decision: ask for their decision or observations in their own words.' if row['researcher_decision'] else '')
            + ' Ask the researcher whether to continue before running it.')
        if nxt == 'intake':
            parts.append('Ask for their field notes or stories, each with place (admin_unit), source, period, language and '
                         'whether they have permission to use it (consent), then call ndim_journey_add_evidence.')
        if nxt == 'policy':
            parts.append('Tell the researcher it assembles a draft for their team\'s review (options for discussion, not '
                         'recommendations), then ask exactly: "Do you approve exporting the policy draft?" Run it only on a '
                         'yes, and pass that reply verbatim as approval_statement.')
        if nxt == 'digital':
            parts.append('Ask for their field observations: the adoption share they observed (0-1), any change in trust and '
                         'in barriers (-1 to 1; 0 if none), and optionally an observed adoption series. Never fill these in.')
        if nxt == 'repository':
            parts.append('Show each record with its gate result and flags, and ask the researcher to accept or reject '
                         'each one, then call ndim_journey_record_decisions with their words. Never decide for them.')
    elif any(row['status'] == 'done' for row in body['stages'] if row['id'] == 'policy'):
        parts.append('All required stages are done. The optional regional analysis can still be run.'
                     if stages['regional']['status'] != 'done' else 'All stages are done.')
    parts.append(GUIDE)
    if stage and stage not in {'intake', 'gate', 'repository'}:
        parts.append(JOURNEY_RULES)
    view['next'] = ' '.join(parts)
    return view

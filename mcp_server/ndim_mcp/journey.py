"""Agent-sized views of the engine's 13-stage journey, and the guidance that walks a researcher through it.

The engine returns full curves and every record; these functions keep the numbers a researcher needs, pass the
engine's fixed wording (its `presentation`) through unchanged, and add a `next` instruction that makes the agent quote
that wording, explain each stage around it and ask before moving on. No journey wording is kept here: live agents
reworded it into overclaims, and a second copy could drift from the engine's.
"""
from .client import EngineError
from .summaries import trajectory_stats

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

GUIDE = ('Guide the researcher one stage at a time. After each stage, give its sentences, explanation and limits '
         'fields word for word (the engine\'s own wording: never reword, shorten or add to them), answer questions only '
         'from them and the result field, then name the next stage and what it does, and ask whether to continue. Do not run '
         'the next stage until they say so. Stages marked researcher_decision need the researcher\'s own words '
         '(approval_statement) and, for the digital twin, their own field observations: ask for them, never invent or '
         'default them.')

NO_WORDING = ('The NDIM engine did not send the journey wording (presentation), so this journey cannot be shown as '
              'written. The engine is older than this tool: ask the operator to update it. Do not describe the journey '
              'or its results in your own words in the meantime.')


def presentation(body):
    """The engine's fixed wording for this journey (intro, opening, and per finished stage its sentences, explanation
    and limits). The engine owns it so that no agent, and no copy here, can drift from it; an engine too old to send it
    is refused rather than worded here, because wording composed outside the engine is what this replaced."""
    shown = body.get('presentation')
    if not isinstance(shown, dict) or not {'intro', 'opening', 'stages'} <= shown.keys():
        raise EngineError(NO_WORDING)
    return shown


def _curve(output):
    return {'model': output['model'], 'horizon_days': output['horizon_days'], 'method_status': output['method_status'],
            'stats': trajectory_stats(output['trajectory'])}


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
                       | ({'translation_checked_by': record['translation_checked_by']} if record.get('translation_checked_by') else {})
                       for record in body['records']]
    shown = presentation(body)
    parts = []
    if stage := body.get('stage'):
        if not (text := shown['stages'].get(stage)):
            raise EngineError(f'The NDIM engine sent no wording for the {stage} stage it ran. Do not describe the result in '
                              'your own words; call ndim_journey_status, and if the wording is still missing, tell the '
                              'researcher the tool needs attention.')
        view['stage'] = stage
        view |= {key: text[key] for key in ('sentences', 'explanation', 'limits')}
        view['result'] = stage_view(stage, body['output'])
        if body.get('cleared_later_stages'):
            view['cleared_later_stages'] = body['cleared_later_stages']
            parts.append('Re-running this stage cleared these later stages, which must be run again: '
                         + ', '.join(body['cleared_later_stages']) + '.')
        fields = [f'the {key} field' for key in ('sentences', 'explanation', 'limits') if text[key]]
        parts.append(f"Report the {stages[stage]['title']} result by quoting, word for word and in this order, "
                     + ', '.join(fields[:-1]) + (' and ' if len(fields) > 1 else '') + fields[-1] + ': they are the '
                     'engine\'s wording, so never reword them. Take every number you mention from them or from the result field.')
        if stage == 'inoculation':
            # A live agent read saturated before/during/after curves as "marginal effects due to saturation".
            parts.append('The first of the sentences reports the before, during and after curves: add nothing else '
                         'about what the messages would do (no "marginal", "small", "limited" or "suggests").')
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
            # A live agent told the researcher to "confirm by stating" this question, as if it were a phrase for them to say.
            parts.append('Tell the researcher it assembles a draft for their team\'s review (options for discussion, not '
                         'recommendations), then end your message by asking them, in these words: "Do you approve '
                         'exporting the policy draft?" It is your question to them, not a phrase for them to repeat. Run '
                         'it only on a yes, and pass their reply verbatim as approval_statement.')
        if nxt == 'graph' and stages['regional']['status'] != 'done':
            # The engine never makes an optional stage next_stage, so a live agent went from 9 to 11 without a word.
            parts.append('Stage 10, Regional analysis, is optional and has not been run: tell the researcher it averages '
                         'the keyword scores per place, and ask whether to run it before the knowledge graph or skip it.')
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

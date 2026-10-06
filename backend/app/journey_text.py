"""Fixed wording for the 13-stage journey: what the app shows as written, so no assistant can reword it.

Live chat agents reworded these sentences in ways that changed their meaning ("adoption will reach", "the message
increases adoption slightly", "personal data removed"). The engine now owns the wording; the research assistant's
journey card and the ndim-mcp tools both show it unchanged, and the agents only explain around it.
"""
from .network_model import robustness_sentences, seeding_sentences

SATURATED = 0.9  # final adoption at or above this: the curve has little room left to show differences

LIMITS = {
    'intake': 'Records are stored as given; nothing has been scored yet.',
    'gate': 'The gate checks metadata and patterns only. It does not judge whether a record is true or representative.',
    'repository': 'Only accepted records reach any model. Decisions are frozen once encoding runs.',
    'encoding': 'Scores come from English keywords in each record: interpretations for review, not measurements of '
                'trust or barriers in a community.',
    'compartmental': 'Illustrative, uncalibrated curve computed from the keyword scores. Not a forecast.',
    'agents': 'Simulated households on an assumed network (villages of clustered neighbours), not real households or a '
              'measured network. The band shows chance across runs only; the network check compares assumed shapes, '
              'not real ones. Not a forecast.',
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
                   'fixed lift formula; they do not model message effects. The messenger comparison recruits simulated '
                   'households on assumed networks, with an assumed persuasion weight; it compares strategies inside the '
                   'model, not in any community, and is not advice on whom to recruit.',
    'policy': 'A draft for the research team\'s review: options for discussion, not recommendations. The evidence grade '
              'and readiness come from the number of records and encoder confidence only.',
}

INTRO = ('**The journey, in six phases**\n\n'
         '1. Evidence: your field notes are stored as given, checked for metadata and personal data, and you accept or '
         'reject each one.\n'
         '2. Encode: an English keyword heuristic scores trust, barriers and themes.\n'
         '3. Model: illustrative, uncalibrated adoption curves from those scores.\n'
         '4. Twin: the model re-run from your own field observations, then a signal update and a ranking of actions under '
         'the tool\'s fixed assumptions.\n'
         '5. Strategy: place summaries, a map of which themes occur together, and message drafts for your review.\n'
         '6. Export: a policy draft of options for your team to discuss, not recommendations.\n\n'
         '**You decide at three points**\n\n'
         '- Accepting or rejecting each record (stage 3)\n'
         '- Giving your own field observations for the digital twin (stage 7)\n'
         '- Approving the policy export (stage 13)')

MODEL_NAMES = {'compartmental': 'compartmental', 'agents': 'agent-based', 'agent_based': 'agent-based', 'hybrid': 'hybrid'}


def opening(journey):
    return (f'The journey has started with your question, exactly as you confirmed it: "{journey["question"]}" '
            f'The setting is {journey["country"]}.')


def final_adoption(trajectory):
    return round(trajectory[-1]['adoption'], 4) if trajectory else None


def curve_sentences(output):
    """The endpoint as the illustrative model's, never as a forecast, and saturation said out loud."""
    final, day = final_adoption(output['trajectory']), int(round(output['trajectory'][-1]['day']))
    name = MODEL_NAMES.get(output['model'], output['model'])
    sentences = [f'In the illustrative {name} model, adoption is {final} at day {day}.']
    if final >= SATURATED:
        sentences.append(f'Adoption ends at {final} of 1.0: the model has saturated, so this curve says little about '
                         'differences between settings.')
    return sentences


def curves_sentence(curves):
    """The one thing the before/during/after curves can support. Told not to read saturated curves as a small message
    effect, live agents still wrote "suggest marginal effects" and "increases slightly after the message"."""
    finals = {model: {phase: final_adoption(rows) for phase, rows in phases.items()} for model, phases in curves.items()}
    parts = [f"{phases['before']}, {phases['during']} and {phases['after']} ({MODEL_NAMES.get(model, model)})"
             for model, phases in finals.items()]
    sentence = ('In the illustrative models, final adoption before, during and after the message is '
                + ' and '.join(parts) + '. These gaps come from the tool\'s fixed lift formula, not from any model of how '
                'messages work, so they say nothing about what the messages would do.')
    saturated = [MODEL_NAMES.get(model, model) for model, phases in finals.items() if min(phases.values()) >= SATURATED]
    if saturated:
        sentence += f" The {' and '.join(saturated)} curves have also saturated (0.9 or more of 1.0)."
    return sentence


def stage_sentences(stage, output):
    """Sentences the app shows for a finished stage, word for word."""
    if stage == 'encoding':
        mean = output['mean']
        return [f"The keyword heuristic scored the accepted records: mean trust {round(mean['trust'], 3)}, mean barrier "
                f"{round(mean['barrier'], 3)}, mean confidence {round(mean['confidence'], 3)}."]
    if stage == 'agents':
        return curve_sentences(output) + robustness_sentences(output['robustness'])[:1]
    if stage in ('compartmental', 'digital'):
        return curve_sentences(output)
    if stage == 'bayes':
        return [output['signal_update_note'], output.get('adoption_fit_note') or 'An adoption curve was fitted to the '
                'observed series the researcher supplied.']
    if stage == 'rl':
        return [f"Under the tool's fixed assumed lifts and costs, the top-ranked action is {output['top_action'].replace('_', ' ')}."]
    if stage == 'regional':
        return [output['note']]
    if stage == 'graph':
        return [output['note']]
    if stage == 'inoculation':
        sentences = [curves_sentence(output['curves']), 'The message drafts need human review before any use with people.']
        if output.get('twin'):
            sentences += curve_sentences(output['twin'])
        if output.get('messenger_seeding'):  # setup, verdict, and the options-not-recommendations line
            seeding = seeding_sentences(output['messenger_seeding'])
            sentences += [seeding[0], seeding[1], seeding[-1]]
        return sentences
    if stage == 'policy':
        return ['This is a draft of options for the research team to discuss, not recommendations.']
    return []


def _num(value, digits=3):
    return round(value, digits) if isinstance(value, (int, float)) else value


def _places(journey):
    return {record['record_id']: record['admin_unit'] for record in journey['records']}


def _fastest_day(trajectory):
    steps = [(trajectory[i]['adoption'] - trajectory[i - 1]['adoption'], trajectory[i]['day']) for i in range(1, len(trajectory))]
    return int(round(max(steps)[1])) if steps else None


def _curve_story(output, intro):
    rows = output['trajectory']
    initial, final, day = round(rows[0]['adoption'], 4), final_adoption(rows), int(round(rows[-1]['day']))
    fastest = _fastest_day(rows)
    timing = 'at the start' if fastest is not None and fastest <= 5 else f'around day {fastest}'
    text = (f'{intro} In this illustrative model, adoption starts at {initial} and is {final} at day {day} '
            f'(0 means nobody, 1 means everyone); it grows fastest {timing}.')
    if final >= SATURATED:
        text += (' Because it ends close to 1.0, the curve has run out of room: it cannot show differences between '
                 'settings, and a shorter time horizon would show more.')
    return text


def accepted_records(journey):
    """The records the researcher accepted (as journey.accepted, which this module cannot import)."""
    return [record for record in (journey or {}).get('records', []) if (record.get('review') or {}).get('decision') == 'accept']


def explanation(stage, output, journey):
    """Plain-language explanation of a finished stage, written by the engine from its own numbers.

    Small local models explained stages with numbers and effects no tool produced; these explanations are what the
    card shows instead, and what the assistant's corrections and fine-tuning examples are measured against."""
    outputs = {key: entry['output'] for key, entry in journey['stages'].items()}
    if stage == 'encoding':
        places = _places(journey)
        rows = [(places.get(e['narrative_id'], 'a record'), e['trust_score'], e['adoption_barrier_score']) for e in output['encoded']]
        most_trust, most_barrier = max(rows, key=lambda r: r[1]), max(rows, key=lambda r: r[2])
        mean = output['mean']
        if most_trust[0] == most_barrier[0]:
            where = (f'Both trust and barrier words scored highest in {most_trust[0]} (trust {_num(most_trust[1])}, barrier '
                     f'{_num(most_barrier[2])})')
        else:
            where = (f'Trust words scored highest in {most_trust[0]} ({_num(most_trust[1])}) and barrier words highest in '
                     f'{most_barrier[0]} ({_num(most_barrier[2])})')
        themes = ', '.join(theme.replace('_', ' ') for theme in output['themes']) or 'none'
        text = (f"The English keyword heuristic read {len(rows)} accepted record(s). {where}, on a scale from 0 (none) to 1 "
                f"(strong). Across all records the average trust score is {_num(mean['trust'])}, barrier "
                f"{_num(mean['barrier'])}, with encoder confidence {_num(mean['confidence'])}. The themes found most often: "
                f'{themes}. These are counts of keywords in the text, not measurements of what people think.')
        if output.get('translated'):
            text += (f" For {output['translated']} of these record(s) the keywords were read in the English translation a "
                     'researcher checked, not in the original wording; sentiment was read in the original.')
        counts = (output.get('sentiment') or {}).get('counts')
        if counts:
            text += (f" Sentiment, read by a classifier trained on African-language tweets (it reads Kinyarwanda too): "
                     f"{counts['positive']} positive, {counts['neutral']} neutral, {counts['negative']} negative. It is a "
                     'reading for review, not a measurement of how people feel.')
        return text
    if stage == 'compartmental':
        text = _curve_story(output, 'The compartmental model treats everyone as one population moving between states: '
                                    'not yet persuaded, misinformed, truth-aligned, inoculated, and adopting.')
        last, notes = output['trajectory'][-1], len(accepted_records(journey))
        return text + (f" Its band runs from {_num(last['adoption_lower'])} to {_num(last['adoption_upper'])} at the end "
                       f"(10th to 90th percentile): how far the curve moves when trust and barrier vary as much as "
                       f"{notes} accepted note{'s' if notes != 1 else ''} allow. It does not include doubt about the "
                       'model\'s own rules, which are assumptions.')
    if stage == 'agents':
        net = output['assumptions']['network']
        text = _curve_story(output, f"The agent-based model simulates {net['households']} households on an assumed "
                                    f"network: {net['topology_meaning']}, with {_num(net['mean_ties'])} ties per household "
                                    'on average. Each day a household may adopt through media, through neighbours who '
                                    'already adopted' + (f", or through the abstract intervention lever (strength "
                                    f"{_num(net['intervention']['intervention_strength'])}, read as in the compartmental "
                                    'model)' if net.get('intervention', {}).get('intervention_strength') else '')
                                    + ', and may stop because of barriers.')
        last = output['trajectory'][-1]
        text += (f" Across {net['replicates']} runs with different chance events, final adoption ranges from "
                 f"{_num(last['adoption_lower'])} to {_num(last['adoption_upper'])} (10th to 90th percentile).")
        check = output['robustness']
        text += (f" The same scenario was re-run on {len(check['variants'])} assumed network shapes, this one included (clustered or "
                 'not, a few highly connected households or none, and whether one or two adopting neighbours are needed '
                 'to persuade a household). ' + ('Average adoption over the period barely changed between them, so this '
                 'level does not hinge on the network assumption.' if check['level_verdict'] == 'holds' else
                 f"Average adoption over the period was lowest with {check['lowest']} and highest with {check['highest']}, "
                 'so this level hinges on how people are actually connected, which the model does not know.'))
        if outputs.get('compartmental'):
            text += f" For comparison, the compartmental model ends at {final_adoption(outputs['compartmental']['trajectory'])}."
        return text
    if stage == 'digital':
        fb = output['feedback']
        return _curve_story(output, f"You reported an observed adoption of {fb['observed_adoption']}, a trust change of "
                                    f"{fb['trust_shift']} and a barrier change of {fb['barrier_shift']}. The digital twin "
                                    'restarted the model from your observed adoption and shifted the scores by your '
                                    'observations.') + ' One observed level does not fit the model to reality.'
    if stage == 'bayes':
        text = (f"The signal update combined the tool's starting assumptions with the keyword scores, counted as "
                f"{output['pseudo_trials']} pseudo-observations (a tool convention). Trust is now {_num(output['trust_mean'], 4)} "
                f"and barrier {_num(output['barrier_mean'], 4)}; later stages use these values.")
        return text + (' An adoption curve was also fitted to the series you supplied.' if output.get('adoption_fit') else
                       ' No adoption curve was fitted, because you gave no observed series over time.')
    if stage == 'rl':
        ranking = '; '.join(f"{i}. {r['action'].replace('_', ' ')} ({_num(r['score'], 4)})" for i, r in enumerate(output['ranking'], 1))
        return (f"Under the tool's fixed assumed lifts and costs, the actions rank: {ranking}. Each score is "
                f"{output['formula']}, using trust {_num(output['trust_used'], 4)} and barrier {_num(output['barrier_used'], 4)}. "
                'No data estimated these lifts and costs, so the ranking restates the assumptions; it is not advice '
                'on what to do.')
    if stage == 'regional':
        rows = '; '.join(f"{r['region']}: {r['count']} record(s), trust {r['trust']}, barrier {r['barrier']}, rule of thumb: "
                         f"{r['rule_of_thumb'].split(' (')[0]}" for r in output['rows'])
        return (f'Average keyword scores per place: {rows}. A place with one or two records says little about the place, '
                'and the rule of thumb is a threshold rule, not a model result.')
    if stage == 'graph':
        places = [n['label'] for n in output['nodes'] if n['kind'] == 'location']
        themes = [n['label'].replace('_', ' ') for n in output['nodes'] if n['kind'] == 'theme']
        signals = [n['label'] for n in output['nodes'] if n['kind'] == 'signal']
        return (f"The graph links {len(places)} place(s) ({', '.join(places)}) with {len(themes)} theme(s) "
                f"({', '.join(themes)}) and the signals {', '.join(signals)}, through {len(output['edges'])} link(s). A link "
                'means they occur together in the records; it says nothing about cause.')
    if stage == 'inoculation':
        titles = '; '.join(f"{d['type']}: {d['title']}" for d in output['drafts'])
        text = (f"Three message drafts for {output['audience'].replace('_', ' ')}, to be delivered by {output['messenger'].replace('_', ' ')}: "
                f'{titles}. They need your team\'s review before any use with people. ' + curves_sentence(output['curves']))
        seeding = output.get('messenger_seeding')
        if seeding:
            text += (f" The agent-based model was also re-run with a campaign that recruits {seeding['messengers']} of its "
                     f"{seeding['households']} simulated households as messengers: chosen at random, the households with the "
                     'most ties, or the households with the most ties to other villages (on networks without villages, '
                     'the most ties to households they share no neighbour with). Messengers use from the start and keep using; each one\'s adoption '
                     f"counts as {seeding['messenger_weight']} ordinary neighbours, from the trusted-messenger fit of "
                     f"{seeding['trusted_messenger_fit']} in the diagnosis (an assumption of the tool). "
                     + ' '.join(seeding_sentences(seeding)[1:]))
        return text
    if stage == 'policy':
        summary, grade = output['summary'], output['evidence_grade']
        return (f"The draft brings together {summary['accepted_records']} accepted and {summary['rejected_records']} rejected "
                f"record(s); evidence grade {grade['grade']} ({grade['readiness'].replace('_', ' ')}), which depends only on "
                f"the number of records and encoder confidence; the twin's final adoption of {_num(summary['final_twin_adoption'], 4)} "
                f"({summary['twin_model']} model); and {summary['top_ranked_action_under_assumptions'].replace('_', ' ')} as the "
                "top-ranked action under the tool's assumptions. It is a draft of options for your team to discuss, not "
                'recommendations.')
    return ''


def presentation(journey):
    """Everything the app shows as written: the intro, the opening and, per finished stage, its sentences and limits."""
    stages = {}
    for stage, entry in journey['stages'].items():
        computed = stage not in ('intake', 'gate', 'repository')
        stages[stage] = {'limits': LIMITS[stage],
                         'sentences': stage_sentences(stage, entry['output']) if computed else [],
                         'explanation': explanation(stage, entry['output'], journey) if computed else ''}
    return {'intro': INTRO, 'opening': opening(journey), 'stages': stages}

"""Fixed wording for the 13-stage journey: what the app shows as written, so no assistant can reword it.

Live chat agents reworded these sentences in ways that changed their meaning ("adoption will reach", "the message
increases adoption slightly", "personal data removed"). The engine now owns the wording; the research assistant's
journey card and the ndim-mcp tools both show it unchanged, and the agents only explain around it.
"""

SATURATED = 0.9  # final adoption at or above this: the curve has little room left to show differences

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
    if stage in ('compartmental', 'agents', 'digital'):
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
        return sentences
    if stage == 'policy':
        return ['This is a draft of options for the research team to discuss, not recommendations.']
    return []


def presentation(journey):
    """Everything the app shows as written: the intro, the opening and, per finished stage, its sentences and limits."""
    stages = {}
    for stage, entry in journey['stages'].items():
        stages[stage] = {'limits': LIMITS[stage],
                         'sentences': stage_sentences(stage, entry['output']) if stage not in ('intake', 'gate', 'repository') else []}
    return {'intro': INTRO, 'opening': opening(journey), 'stages': stages}

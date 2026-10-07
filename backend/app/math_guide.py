"""How NDIM computes, step by step: the formulas the journey really runs, each with a worked example the engine works out.

Every formula here was written from the code it describes, and the worked examples call that code (the encoder, the
compartmental rates, the network rates), so an example cannot disagree with the engine. scripts/test_math_guide.py checks
the arithmetic shown against the engine's own results. The research assistant reads these sections through the library
(agent_library, source "guide"); Studio shows them in the How it works panel.
"""
from functools import lru_cache
import re

from .encoding import BARRIER_BASE, BARRIER_PRESSURE, BARRIER_RELIEF, KEYWORDS, TRUST_BASE, TRUST_WEIGHTS, encode_rule_based, keyword_counts
from .inoculation import diagnose_inoculation_rule_based
from .modelling import compartmental_rates
from .network_model import INTERVENTION_RATES, SPREAD_LIMIT, VARIANTS, rates as network_rates
from .schemas import NarrativeMetadata, NarrativeRecord

EXAMPLE_NOTE = ('Households in Niboye say the improved stoves save charcoal and they trust the health worker who showed them, '
                'but the price is too high and some neighbours heard a rumour that the smoke makes food taste bad.')
EXAMPLE_PLACE = 'Kicukiro / Niboye'
LABELS = {'trust_positive': 'trust words', 'trust_negative': 'distrust words', 'misinformation': 'rumour words',
          'health': 'health words', 'social': 'social words', 'local_grounding': 'local grounding',
          'affordability': 'cost words', 'fuel_access': 'fuel and repair words', 'safety': 'safety words', 'habit': 'habit words',
          'negative_stance': 'refusal words', 'positive_stance': 'benefit words', 'emotion': 'feeling words'}
PRIORS = {'trust_a': 6.0, 'trust_b': 4.0, 'barrier_a': 4.0, 'barrier_b': 6.0}  # journey.PRIORS
ACTIONS = {'none': (0.0, 0.0), 'demand_generation': (0.12, 0.08), 'consumer_subsidy': (0.16, 0.18), 'supply_chain': (0.13, 0.14)}


def r(value, digits=3):
    return round(float(value), digits)


def example_record():
    return NarrativeRecord(narrative_id='guide-example', text=EXAMPLE_NOTE, metadata=NarrativeMetadata(
        source_type='interview', source_name='Guide example', country='Rwanda', admin_unit=EXAMPLE_PLACE, language='en',
        provenance={}))


@lru_cache(maxsize=1)
def example():
    """The example note encoded by the real encoder, and the counts behind its scores."""
    record = example_record()
    encoded = encode_rule_based(record, sentiment_text=None)
    counts = keyword_counts(EXAMPLE_NOTE.lower())
    counts['local_grounding'] += 2  # the encoder adds 1 for a country and 1 for a place
    text = EXAMPLE_NOTE.lower()
    found = {name: [w for w in words if re.search(rf'\b{re.escape(w)}\b', text)] for name, words in KEYWORDS.items()}
    return {'encoded': encoded, 'counts': counts, 'found': found, 'diagnosis': diagnose_inoculation_rule_based(record, encoded)}


def _terms(base, weights, counts):
    parts = [f'{base}']
    for name, weight in weights.items():
        if counts[name]:
            parts.append(f'{"+" if weight > 0 else "−"} {abs(weight)} × {counts[name]} ({LABELS[name]})')
    return ' '.join(parts)


def encoding_section():
    ex = example()
    c, e = ex['counts'], ex['encoded']
    trust_line = _terms(TRUST_BASE, TRUST_WEIGHTS, c)
    barrier_weights = {**BARRIER_PRESSURE, **{k: -v for k, v in BARRIER_RELIEF.items()}}
    barrier_line = _terms(BARRIER_BASE, barrier_weights, c)
    seen = [f'{LABELS[k]}: {", ".join(v)}' for k, v in ex['found'].items() if v]
    return {
        'id': 'guide-encoding', 'number': 1, 'stages': ['encoding'], 'title': 'From words to scores (the keyword encoder: trust and barrier)',
        'why': 'How the trust score and the barrier score of each note are computed. NDIM cannot read meaning, so it counts words. Each accepted note is lower-cased and checked against fixed '
               'word lists (trust words, cost words, rumour words and so on). The counts are turned into a trust score '
               'and a barrier score, each kept between 0.05 and 0.95. A word can count in more than one list, and the note\'s '
               'country and place each add 1 to local grounding. A trust or benefit word with "not", "no", "never" or '
               'similar among the three words before it counts the other way ("I do not trust" is distrust). A journey\'s '
               'topic (vaccines, AI in the classroom, just transition) adds a short list of that topic\'s words.',
        'formulas': [
            r'\text{trust} = \operatorname{clamp}\big(0.48 + 0.060\,T^{+} + 0.025\,H + 0.010\,S + 0.018\,L - 0.070\,T^{-} - 0.025\,R\big)',
            r'\text{barrier} = \operatorname{clamp}\big(0.30 + 0.095\,A + 0.075\,F + 0.07\,S_a + 0.055\,B + 0.06\,N + 0.025\,R - 0.035\,P - 0.015\,H\big)',
            r'\operatorname{clamp}(x) = \min(0.95, \max(0.05, x))'],
        'symbols': [['T⁺, T⁻', 'trust and distrust words'], ['H', 'health words (smoke, cough, children…)'],
                    ['S', 'social words (neighbour, group, village…)'], ['L', 'local grounding (place words, +1 country, +1 place)'],
                    ['R', 'rumour words (rumour, heard, claim, myth…)'], ['A', 'cost words'], ['F', 'fuel and repair words'],
                    ['Sₐ', 'safety words'], ['B', 'habit words'], ['N', 'refusal words'], ['P', 'benefit words']],
        'example': [
            f'Note: “{EXAMPLE_NOTE}” (place: {EXAMPLE_PLACE}).',
            'Words found: ' + '; '.join(seen) + '.',
            f'trust = {trust_line} = {r(e.trust_score)}',
            f'barrier = {barrier_line} = {r(e.adoption_barrier_score)}',
            f'The engine\'s encoder gives trust {r(e.trust_score)} and barrier {r(e.adoption_barrier_score)} for this note.'],
        'limits': 'A keyword count, not understanding: negation is caught only within three words, and “many buyers believe '
                  'the rumour” still counts “believe” as trust. The weights are the '
                  'tool\'s conventions, not estimated from data. English only (a checked translation is read for '
                  'non-English notes). Sentiment comes from a separate classifier and does not enter these scores.',
    }


def settings_section():
    e = example()['encoded']
    trust, confidence = r(e.trust_score), r(e.confidence)
    influence = min(0.9, 0.2 + 0.35 * confidence)
    strength = min(0.9, 0.1 + 0.2 * trust)
    return {
        'id': 'guide-settings', 'number': 2, 'stages': ['compartmental', 'agents'], 'title': 'From scores to model settings',
        'why': 'The models do not read the notes, only a few numbers made from the scores: the average trust and barrier '
               'over the accepted notes, a narrative influence from the encoder\'s confidence, and an intervention strength. '
               'In the journey the intervention strength is worked out from trust, not typed in. Later stages change these '
               'numbers: the digital twin shifts trust and barrier, the signal update replaces them, the action ranking adds a '
               'small bonus and the inoculation lab adds its applied strength.',
        'formulas': [
            r'\text{narrative influence} = \min(0.9,\; 0.2 + 0.35\,\bar{c} + 0.12\,a)',
            r'\text{intervention strength} = \min(0.9,\; 0.1 + 0.2\,\overline{\text{trust}} + b + 0.28\,a)'],
        'symbols': [['c̄', 'average encoder confidence'], ['a', 'inoculation strength applied in stage 12 (0 before it)'],
                    ['b', 'bonus from the action ranking (stage 9), 0 before it']],
        'example': [f'With only the example note: trust {trust}, confidence {confidence}, before stages 9 and 12 (a = b = 0).',
                    f'narrative influence = min(0.9, 0.2 + 0.35 × {confidence}) = {r(influence)}',
                    f'intervention strength = min(0.9, 0.1 + 0.2 × {trust}) = {r(strength)}'],
        'limits': 'These links between scores and settings are fixed rules of the tool, chosen for illustration.',
    }


def compartmental_section():
    e = example()['encoded']
    params = {'trust_score': r(e.trust_score), 'barrier_score': r(e.adoption_barrier_score),
              'narrative_influence': r(min(0.9, 0.2 + 0.35 * r(e.confidence))), 'intervention_strength': r(min(0.9, 0.1 + 0.2 * r(e.trust_score)))}
    rate = compartmental_rates(params)
    return {
        'id': 'guide-compartmental', 'number': 3, 'stages': ['compartmental'], 'title': 'The population model (compartmental S/M/T/I/R equations)',
        'why': 'The population is split into five shares that always add up to 1: S not yet reached, M holding a '
               'misinformed view, T convinced by trustworthy information, I inoculated (prepared against the rumour) and R '
               'settled adopters. Each day people move between the shares at the rates below. Adoption is T + I + R. '
               'Word of mouth comes from everyone who uses it (T and R), and adopters can stop and fall back to S at the '
               'same daily rate as in the household model, so the long-run level depends on trust and barriers, not only '
               'the speed. The model takes one-day steps and rescales the shares to add up to 1 after each step.',
        'formulas': [
            r'\Delta S = -\beta_m S M - \beta_t S (T + R) - \iota S + w(M + T) + \delta (T + R)',
            r'\Delta M = \beta_m S M - \rho M - \sigma M I',
            r'\Delta T = \beta_t S (T + R) + \rho M - \mu T - \eta T - \delta T',
            r'\Delta I = \iota S + \sigma M I - \gamma I',
            r'\Delta R = \gamma I + \eta T - \delta R \qquad \text{adoption} = T + I + R',
            r'\delta = 0.025\,\text{barrier} + 0.008\,m + 0.010\,x \quad \text{(the household model\'s daily stop rate)}',
            r'\beta_t = 0.035\,(1 + \phi)(0.65 + \text{trust}) \qquad \beta_m = 0.030\,(0.55 + \text{barrier} + 0.35\,m + 0.18\,x)',
            r'\iota = 0.006 + 0.020\,s + 0.030\,i + 0.010\,f \qquad \rho = 0.010 + 0.020\,\text{trust} + 0.012\,s + 0.010\,f',
            r'\gamma = 0.008 + 0.018\,s + 0.012\,\text{trust} + 0.012\,g \qquad \eta = 0.006 + 0.012\,\text{trust} + 0.006\,g',
            r'\sigma = 0.008 + 0.020\,i + 0.018\,d \qquad \mu = 0.004 + 0.010\,\text{barrier} \qquad w = 0.001 + 0.004\max(0, \text{barrier} - \text{trust})'],
        'symbols': [['φ', 'narrative influence'], ['s', 'intervention strength'], ['i', 'inoculation strength'],
                    ['m', 'misinformation risk'], ['x', 'reactance (backlash) risk'], ['f', 'trusted-messenger fit'],
                    ['g', 'resistance growth'], ['d', 'misinformation decay'], ['σ M I', 'uses at least 0.001 for I']],
        'example': [f'Settings from the example note: trust {params["trust_score"]}, barrier {params["barrier_score"]}, '
                    f'φ {params["narrative_influence"]}, s {params["intervention_strength"]}, nothing else yet.',
                    f'β_t = 0.035 × (1 + {params["narrative_influence"]}) × (0.65 + {params["trust_score"]}) = {r(rate["beta_t"], 4)} a day',
                    f'β_m = 0.030 × (0.55 + {params["barrier_score"]}) = {r(rate["beta_m"], 4)} a day',
                    f'ι = {r(rate["iota"], 4)}, ρ = {r(rate["rho"], 4)}, γ = {r(rate["gamma"], 4)}, η = {r(rate["eta"], 4)}, '
                    f'μ = {r(rate["mu"], 4)}, w = {r(rate["waning"], 4)}, δ = 0.025 × {params["barrier_score"]} = {r(rate["delta"], 4)} a day.',
                    'Trust raises β_t (word of mouth), barrier raises β_m (the misinformed view) and δ (stopping). In the long run '
                    'the level is roughly 1 − δ/β_t: more trust raises it, more barrier lowers it.'],
        'limits': 'Illustrative and uncalibrated: the rates are rules of the tool, not measured. The band around the curve '
                  'is the 10th to 90th percentile of 50 re-runs with trust and barrier drawn from Beta distributions holding '
                  '10 prior counts plus 12 per accepted note, so more notes give a narrower band; it leaves out doubt about '
                  'the rules themselves (see the sensitivity analysis). A scenario, not a forecast. '
                  'Until October 2026 settled adopters neither spoke nor stopped, so every scenario drifted towards full adoption.',
    }


def network_section():
    e = example()['encoded']
    params = {'trust_score': r(e.trust_score), 'barrier_score': r(e.adoption_barrier_score), 'intervention_strength': r(min(0.9, 0.1 + 0.2 * r(e.trust_score)))}
    rate = network_rates(params)
    return {
        'id': 'guide-network', 'number': 4, 'stages': ['agents'], 'title': 'The household network model (agent-based)',
        'why': '1,000 simulated households live on an assumed social network: by default villages of 100, each household '
               'tied to about 8 neighbours, a few ties rewired at random, and about one tie per household to another village. '
               'Each day a household that has not adopted may adopt through media, through neighbours who already adopted, '
               'or through outreach; an adopter may stop. By default one adopting neighbour can persuade; with complex '
               'contagion two are needed. The whole thing runs 20 times, each on its own network with its own chance events.',
        'formulas': [
            r'P(\text{adopt today}) = \min\!\Big(1,\; \text{media} + \text{peer}\cdot\frac{\text{adopting neighbours}}{\text{neighbours}} + \text{outreach}\Big)',
            r'\text{media} = (0.05 + 0.035\,i + 0.020\,f)\cdot\text{trust} \qquad \text{peer} = 0.08',
            r'\text{outreach} = s\,\big(0.020\,q + 0.012\,(1 - q)\big) \qquad q = \frac{S_0}{S_0 + M_0}',
            r'P(\text{stop today}) = 0.025\,\text{barrier} + 0.008\,m + 0.010\,x',
            r'\text{hybrid} = 0.55 \times \text{population model} + 0.45 \times \text{network model}'],
        'symbols': [['trust, barrier', 'the average scores of the accepted notes, the same for every household: households differ only in their neighbours and in chance'],
                    ['s', 'intervention strength'], ['i', 'inoculation strength'], ['f', 'trusted-messenger fit'],
                    ['q', 'share of the not-yet-adopted who are not misinformed at the start'], ['m, x', 'misinformation and reactance risk']],
        'example': [f'With the example settings: media = 0.05 × {params["trust_score"]} = {r(rate["media"], 4)}, '
                    f'outreach = {r(rate["intervention"], 4)}, stop = 0.025 × {params["barrier_score"]} = {r(rate["friction"], 4)} a day.',
                    'A household with 8 neighbours of whom 2 adopted gets a peer chance of 0.08 × 2/8 = 0.02 a day on top.',
                    'The band is the 10th to 90th percentile over the 20 runs: chance only, not uncertainty in the scores.'],
        'limits': 'The network is an assumption, not measured. It shows what such a structure could do, not what real '
                  'villages will do. The hybrid weights 0.55 and 0.45 are tool conventions.',
    }


def robustness_section():
    shapes = ', '.join(f'{t.replace("_", " ")} ({c})' for t, c in VARIANTS)
    return {
        'id': 'guide-robustness', 'number': 5, 'stages': ['agents'], 'title': 'Does the result depend on the network shape?',
        'why': 'Because the network is assumed, NDIM re-runs the scenario on 7 shapes and compares the average adoption over '
               'the period. If the highest and lowest averages are within 0.10 of each other, the level "holds"; otherwise it '
               '"depends on the network shape". Comparisons between two scenarios use the same random draws in both, so only '
               'the change you made differs.',
        'formulas': [r'\text{spread} = \max_k \bar{a}_k - \min_k \bar{a}_k \qquad \text{holds if spread} \le ' + str(SPREAD_LIMIT)],
        'symbols': [['ā_k', 'average adoption over the period on shape k']],
        'example': [f'The 7 shapes: {shapes}.',
                    'If the averages run from 0.31 to 0.38, the spread is 0.07: the level holds. From 0.27 to 0.68 it depends on the shape.'],
        'limits': 'Seven shapes are not every possible network; "holds" means only that these assumptions agree.',
    }


def twin_section():
    return {
        'id': 'guide-twin', 'number': 6, 'stages': ['digital'], 'title': 'The digital twin: re-running from your field numbers',
        'why': 'The twin does not learn by itself. You give it what you observed in the field: the adoption share now, and how '
               'far trust and barriers moved. NDIM starts the hybrid model again from your adoption share, with trust and '
               'barrier shifted by your amounts. There are no defaults: without your numbers this stage does not run.',
        'formulas': [r'\text{initial adoption} = y_{\text{observed}} \qquad \text{trust}\,{+}{=}\,\Delta_{\text{trust}} \qquad \text{barrier}\,{+}{=}\,\Delta_{\text{barrier}}'],
        'symbols': [['y_observed', 'adoption share you observed'], ['Δ', 'your observed change (0 when you saw none)']],
        'example': ['If you observed 0.20 adoption, no change in trust and barriers up by 0.05, the hybrid model restarts at 0.20 '
                    'with barrier 0.05 higher than the notes suggested.'],
        'limits': 'One re-run from your numbers, not a fitted model. It is only as good as the field observations you give it.',
    }


def bayes_section():
    e = example()['encoded']
    trust = r(e.trust_score)
    n = 12
    k = round(trust * n)
    a, b = PRIORS['trust_a'] + k, PRIORS['trust_b'] + n - k
    return {
        'id': 'guide-bayes', 'number': 7, 'stages': ['bayes'], 'title': 'The signal update (Bayesian)',
        'why': 'NDIM starts from a stated belief about trust and barriers (the prior) and moves it towards what the notes '
               'and your field shifts say. The average score is treated as if it came from n yes/no trials, 12 per accepted '
               'note; the more notes, the further the belief moves from the prior.',
        'formulas': [r'\text{prior: } \text{Beta}(\alpha, \beta) \qquad n = 12 \times \text{notes} \qquad k = \operatorname{round}(\text{score} \times n)',
                     r'\text{posterior: } \text{Beta}(\alpha + k,\; \beta + n - k) \qquad \text{mean} = \frac{\alpha + k}{\alpha + \beta + n}'],
        'symbols': [['α, β', 'prior counts: trust Beta(6, 4), mean 0.6; barrier Beta(4, 6), mean 0.4'], ['n', 'pseudo-trials'],
                    ['k', 'pseudo-successes']],
        'example': [f'One note with trust {trust}: n = 12, k = round({trust} × 12) = {k}.',
                    f'posterior Beta(6 + {k}, 4 + {n - k}) = Beta({a:g}, {b:g}), mean {a:g} / {a + b:g} = {r(a / (a + b))}.'],
        'limits': 'The 12 pseudo-trials per note are a tool convention that decides how far the prior moves; the scores are '
                  'not real trials. An adoption curve is fitted only to an observed series you supply, never to model output.',
    }


def ranking_section():
    e = example()['encoded']
    trust, barrier = r(e.trust_score), r(e.adoption_barrier_score)
    scores = {name: lift + trust * 0.30 - barrier * 0.22 - cost for name, (lift, cost) in ACTIONS.items()}
    top = max(scores, key=scores.get)
    return {
        'id': 'guide-ranking', 'number': 8, 'stages': ['rl'], 'title': 'Ranking possible actions (the policy optimizer)',
        'why': 'Four illustrative actions each have an assumed lift and cost. NDIM scores them with the current trust and '
               'barrier and sorts them. The top score adds a small bonus to the intervention strength used afterwards.',
        'formulas': [r'\text{score} = \text{lift} + 0.30\,\text{trust} - 0.22\,\text{barrier} - \text{cost}',
                     r'\text{bonus} = 0.025 \times \max(0, \text{top score})'],
        'symbols': [['lift, cost', 'assumed per action: demand generation 0.12 / 0.08, consumer subsidy 0.16 / 0.18, supply chain 0.13 / 0.14, none 0 / 0']],
        'example': [f'With trust {trust} and barrier {barrier}: ' + '; '.join(f'{name.replace("_", " ")} {r(v)}' for name, v in scores.items()) + '.',
                    f'Top: {top.replace("_", " ")}. Trust and barrier add the same amount to every action, so the order comes from lift − cost alone.'],
        'limits': 'The lifts and costs are assumptions of the tool, not estimates, so the ranking restates them. '
                  'It is not a recommendation.',
    }


def inoculation_section():
    d = example()['diagnosis']
    return {
        'id': 'guide-inoculation', 'number': 9, 'stages': ['encoding', 'inoculation'], 'title': 'Inoculation: preparing people for a rumour',
        'why': 'Inoculation (pre-bunking) means warning people about a misleading claim and showing why it is wrong before '
               'they meet it. For each note NDIM scores how threatening and misleading its rumours look, how easy they are '
               'to refute, how well a trusted messenger fits and the risk of backlash, and combines them into a suggested '
               'inoculation strength. In stage 12 you can apply an inoculation to the twin; it raises trust and lowers barriers a little.',
        'formulas': [r'\text{inoculation strength} = \operatorname{clamp}(0.10 + 0.20\,T_h + 0.20\,M_s + 0.18\,R_f + 0.14\,F_m - 0.08\,X)',
                     r'\text{applied: trust}\,{+}{=}\,0.08\,a \qquad \text{barrier}\,{-}{=}\,0.07\,a'],
        'symbols': [['T_h', 'threat recognition'], ['M_s', 'misinformation risk'], ['R_f', 'refutability'],
                    ['F_m', 'trusted-messenger fit'], ['X', 'reactance (backlash) risk'], ['a', 'applied strength, stage 12']],
        'example': [f'Example note: threat {r(d.threat_recognition_score)}, misinformation {r(d.misinformation_risk_score)}, '
                    f'reactance {r(d.reactance_risk_score)}; suggested strength {r(d.intervention_parameters.get("inoculation_strength", 0))}.'],
        'limits': 'Keyword heuristics again. Message drafts are for your review and editing, never to be sent as they are.',
    }


def grade_section():
    return {
        'id': 'guide-grade', 'number': 10, 'stages': ['policy'], 'title': 'The evidence grade on the policy draft',
        'why': 'The policy draft carries a grade for how much the evidence can bear, from the number of accepted notes and '
               'the encoder\'s average confidence.',
        'formulas': [r'\text{B: } \ge 20 \text{ notes and confidence} \ge 0.70 \qquad \text{C: } \ge 5 \text{ and} \ge 0.55 \qquad \text{D: otherwise}'],
        'symbols': [['B', 'policy use with review'], ['C', 'pilot or targeted use only'], ['D', 'do not use for policy yet']],
        'example': ['Two notes give grade D whatever their confidence: use the draft for learning and discussion.'],
        'limits': 'There is no grade A: no amount of keyword-scored notes makes the model a measurement.',
    }


@lru_cache(maxsize=1)
def _sensitivity_example():
    from .sensitivity import analyse
    e = example()['encoded']
    return analyse(180, {'trust_score': r(e.trust_score), 'barrier_score': r(e.adoption_barrier_score)}, samples=256)


def sensitivity_section():
    out = _sensitivity_example()
    top = out['factors'][:3]
    return {
        'id': 'guide-sensitivity', 'number': 11, 'stages': ['compartmental'], 'title': 'Which assumptions matter most? (sensitivity analysis)',
        'why': 'The band shows doubt about the evidence; this step also asks about the tool\'s own rules. NDIM varies the '
               'evidence inputs (±0.15 around their values) and the rate constants (each from half to double) all at '
               'once, thousands of times, and splits the variation in the result between them. A factor with a large total '
               'index matters; one near 0 barely does. The journey offers it after stage 5.',
        'formulas': [r'S_i = \frac{\operatorname{Var}(\mathbb{E}[Y \mid X_i])}{\operatorname{Var}(Y)} \qquad '
                     r'S_{T,i} = \frac{\mathbb{E}[\operatorname{Var}(Y \mid X_{\sim i})]}{\operatorname{Var}(Y)}',
                     r'\hat S_{T,i} = \frac{\tfrac{1}{2N}\sum_j \big(f(A)_j - f(A_B^{(i)})_j\big)^2}{\operatorname{Var}(Y)} \quad \text{(Jansen)}'],
        'symbols': [['Y', 'adoption at the end of the period'], ['X_i', 'one input or rate assumption'],
                    ['S_i', 'first-order index: the share of the variation explained by X_i alone'],
                    ['S_T,i', 'total index: the share that involves X_i, including its interactions'],
                    ['A, B, A_B⁽ⁱ⁾', 'Saltelli\'s sample matrices (A with column i taken from B)']],
        'example': [f'For the example note (trust {r(example()["encoded"].trust_score)}, barrier {r(example()["encoded"].adoption_barrier_score)}), '
                    f'day 180, {out["runs"]:,} runs: adoption averages {out["mean"]} with a spread of {out["spread"]}.',
                    'Largest total indices: ' + '; '.join(f'{row["label"]} {row["total"]}' for row in top) + '.',
                    *out['sentences'][2:3]],
        'limits': 'The ranges are choices: wider ranges for a factor raise its index. Indices describe this model, not the '
                  'world: a rate assumption that dominates is exactly what real adoption data should be used to pin down.',
    }


def guide():
    sections = [encoding_section(), settings_section(), compartmental_section(), network_section(), robustness_section(),
                twin_section(), bayes_section(), ranking_section(), inoculation_section(), grade_section(), sensitivity_section()]
    for section in sections:  # the model in symbols, the derivation and the values used (see SYMBOLIC)
        section.update(SYMBOLIC[section['id']]())
        section['parameters_note'] = ('Values NDIM uses: constants written into its code by the developers as illustrative '
                                      'defaults, not estimated from data. Real data should replace them (see step 11).')
    return {'title': 'How NDIM works', 'intro': (
        'NDIM turns field notes into illustrative scenarios in ten steps, and step 11 asks which assumptions matter most. Each step below shows the formula the engine '
        'really runs, what every symbol means, a worked example on one sample note, and what the step cannot tell you. '
        'The numbers in the examples are computed by the engine itself.'),
        'example_note': EXAMPLE_NOTE, 'sections': sections,
        'intervention_rates': INTERVENTION_RATES}


def library_sections():
    """The guide as plain-text library sections for the research assistant (search_library / read_library)."""
    out = []
    for section in guide()['sections']:
        text = [section['why'], '', 'The model in symbols (LaTeX):', *section['formulas'], '', 'Symbols:',
                *[f'• {sym}: {meaning}' for sym, meaning in section['symbols']], '', 'Derivation:',
                *[f'• {step["text"]}' + (f'  [{step["tex"]}]' if step.get('tex') else '') for step in section.get('derivation', [])], '',
                'Values NDIM uses (assumptions set by its developers, not estimated from data):',
                *[f'• {sym} = {value}: {meaning}' for sym, value, meaning in section.get('parameters', [])], '', 'Worked example:',
                *[f'• {line}' for line in section['example']], '', 'What it cannot tell you: ' + section['limits']]
        out.append({'id': section['id'], 'title': f'{section["number"]}. {section["title"]}', 'text': '\n'.join(text)})
    return out


# ---------------------------------------------------------------- the math as math
# Each step is shown as a model in symbols, a derivation, and a table of the values NDIM uses. Those values are
# constants written into NDIM's code by its developers as illustrative defaults: none was estimated from data, and the
# sensitivity analysis (step 11) shows that several of them drive the results. Numbers appear only in the tables and
# in the worked examples. scripts/test_math_guide.py checks that the symbolic formulas, filled in with the table values,
# give exactly the engine's own rates.
ASSUMED = 'set by NDIM\'s developers as an illustrative default; not estimated from data'

POPULATION_PARAMETERS = {  # modelling.compartmental_rates, written as parameters
    'k_t': (0.035, 'word-of-mouth base rate'), 'c_t': (0.65, 'trust offset in word of mouth'),
    'k_m': (0.030, 'misinformation base rate'), 'c_m': (0.55, 'offset in misinformation spread'),
    'w_{mm}': (0.35, 'weight of misinformation risk m'), 'w_{mx}': (0.18, 'weight of reactance x'),
    '\\iota_0': (0.006, 'outreach base rate'), '\\iota_s': (0.020, 'outreach per unit of intervention strength'),
    '\\iota_i': (0.030, 'outreach per unit of inoculation strength'), '\\iota_f': (0.010, 'outreach per unit of messenger fit'),
    '\\rho_0': (0.010, 'misinformed-to-convinced base rate'), '\\rho_\\tau': (0.020, 'per unit of trust'),
    '\\rho_s': (0.012, 'per unit of intervention strength'), '\\rho_f': (0.010, 'per unit of messenger fit'),
    '\\sigma_0': (0.008, 'inoculation of the misinformed, base'), '\\sigma_i': (0.020, 'per unit of inoculation strength'),
    '\\sigma_d': (0.018, 'per unit of misinformation decay'), '\\mu_0': (0.004, 'convinced losing interest, base'),
    '\\mu_b': (0.010, 'per unit of barrier'), '\\gamma_0': (0.008, 'inoculated settling, base'),
    '\\gamma_s': (0.018, 'per unit of intervention strength'), '\\gamma_\\tau': (0.012, 'per unit of trust'),
    '\\gamma_g': (0.012, 'per unit of resistance growth'), '\\eta_0': (0.006, 'convinced settling, base'),
    '\\eta_\\tau': (0.012, 'per unit of trust'), '\\eta_g': (0.006, 'per unit of resistance growth'),
    'w_0': (0.001, 'waning back to S, base'), 'w_1': (0.004, 'waning per unit of barrier above trust'),
    '\\delta_b': (0.025, 'adopter stop rate per unit of barrier'), '\\delta_m': (0.008, 'per unit of misinformation risk'),
    '\\delta_x': (0.010, 'per unit of reactance'),
}


def population_rates_from_parameters(inputs):
    """The rates from the symbolic formulas and POPULATION_PARAMETERS (checked against compartmental_rates)."""
    p = {key: value for key, (value, _) in POPULATION_PARAMETERS.items()}
    clamp = lambda v: max(0.0, min(1.0, float(v)))
    tau, b = clamp(inputs.get('trust_score', 0.6)), clamp(inputs.get('barrier_score', 0.35))
    phi, s = clamp(inputs.get('narrative_influence', 0.38)), clamp(inputs.get('intervention_strength', 0.15))
    i, m, x = clamp(inputs.get('inoculation_strength', 0)), clamp(inputs.get('misinformation_risk', 0)), clamp(inputs.get('reactance_penalty', 0))
    f, g, d = clamp(inputs.get('trusted_messenger_fit', 0)), clamp(inputs.get('resistance_growth', 0)), clamp(inputs.get('misinformation_decay', 0))
    return {'beta_t': p['k_t'] * (1 + phi) * (p['c_t'] + tau), 'beta_m': p['k_m'] * (p['c_m'] + b + p['w_{mm}'] * m + p['w_{mx}'] * x),
            'iota': p['\\iota_0'] + p['\\iota_s'] * s + p['\\iota_i'] * i + p['\\iota_f'] * f,
            'rho': p['\\rho_0'] + p['\\rho_\\tau'] * tau + p['\\rho_s'] * s + p['\\rho_f'] * f,
            'sigma': p['\\sigma_0'] + p['\\sigma_i'] * i + p['\\sigma_d'] * d, 'mu': p['\\mu_0'] + p['\\mu_b'] * b,
            'gamma': p['\\gamma_0'] + p['\\gamma_s'] * s + p['\\gamma_\\tau'] * tau + p['\\gamma_g'] * g,
            'eta': p['\\eta_0'] + p['\\eta_\\tau'] * tau + p['\\eta_g'] * g, 'waning': p['w_0'] + p['w_1'] * max(0.0, b - tau),
            'delta': p['\\delta_b'] * b + p['\\delta_m'] * m + p['\\delta_x'] * x}


def _rows(table):
    return [[symbol, value, meaning] for symbol, (value, meaning) in table.items()]


def _step(text, tex=None):
    return {'text': text, 'tex': tex}


def _encoding_math():
    rows = [['b_\\tau', TRUST_BASE, 'trust of a note with no matched words']]
    rows += [[f'w^{{\\tau}}_{{\\text{{{LABELS[k]}}}}}', v, 'added to trust per word' if v > 0 else 'taken from trust per word'] for k, v in TRUST_WEIGHTS.items()]
    rows += [['b_b \\;', BARRIER_BASE, 'barrier of a note with no matched words']]
    rows += [[f'w^{{b}}_{{\\text{{{LABELS[k]}}}}}', v, 'added to barrier per word'] for k, v in BARRIER_PRESSURE.items()]
    rows += [[f'w^{{b}}_{{\\text{{{LABELS[k]}}}}}', -v, 'taken from barrier per word'] for k, v in BARRIER_RELIEF.items()]
    rows += [['\\ell,\\; u', '0.05, 0.95', 'lowest and highest score allowed']]
    return {
        'formulas': [r'n_k(d) = \#\{\text{words of list } k \text{ in note } d\}',
                     r'\tau(d) = \operatorname{clamp}\Big(b_\tau + \sum_k w^{\tau}_k\, n_k(d)\Big)',
                     r'b(d) = \operatorname{clamp}\Big(b_b + \sum_k w^{b}_k\, n_k(d)\Big)',
                     r'\operatorname{clamp}(x) = \min\big(u, \max(\ell, x)\big)'],
        'derivation': [
            _step('Start from a points system: every matched word adds a fixed amount of evidence, so a score is linear in the counts.', r'\tau = b_\tau + w_1 n_1 + w_2 n_2 + \dots'),
            _step('The base is the score of a note with no matched words: the neutral starting point before any evidence.', r'n_k = 0 \;\Rightarrow\; \tau = b_\tau'),
            _step('The sign of a weight says the direction: trust words push trust up, distrust and rumour words push it down.', r'w^{\tau}_{\text{trust}} > 0, \quad w^{\tau}_{\text{distrust}} < 0'),
            _step('Each word counts every time it occurs, so the effect of one list grows in steps of its weight.', r'\frac{\partial \tau}{\partial n_k} = w^{\tau}_k \quad (\text{inside the clamp})'),
            _step('The clamp keeps every score strictly between 0 and 1, so the models downstream always receive valid shares.', r'\ell \le \tau(d) \le u'),
            _step('Over many notes the model uses the average score, the mean of these linear sums.', r'\bar\tau = \frac{1}{N}\sum_{d=1}^{N}\tau(d)')],
        'parameters': rows}


def _settings_math():
    return {
        'formulas': [r'\phi = \min\big(\phi_{\max},\; a_\phi + b_\phi\,\bar c + g_\phi\, a\big)',
                     r's = \min\big(s_{\max},\; a_s + b_s\,\bar\tau + \text{bonus} + g_s\, a\big)'],
        'derivation': [
            _step('The models need a few drivers, not the notes. Each driver is a straight-line function of an evidence summary, with a cap.', r'\text{driver} = \min(\text{cap}, \text{intercept} + \text{slope}\times\text{summary})'),
            _step('Narrative influence rises with how confident the encoder was; intervention strength rises with trust, the ranking bonus and any applied inoculation.'),
            _step('The caps stop either driver reaching 1, which would make the model\'s rates meaningless.')],
        'parameters': [['a_\\phi,\\; b_\\phi,\\; g_\\phi,\\; \\phi_{\\max}', '0.20, 0.35, 0.12, 0.90', 'narrative influence line and cap (' + ASSUMED + ')'],
                       ['a_s,\\; b_s,\\; g_s,\\; s_{\\max}', '0.10, 0.20, 0.28, 0.90', 'intervention strength line and cap (' + ASSUMED + ')']]}


def _population_math():
    return {
        'formulas': [r'\Delta S = -\beta_m S M - \beta_t S (T + R) - \iota S + w(M + T) + \delta (T + R)',
                     r'\Delta M = \beta_m S M - \rho M - \sigma M I',
                     r'\Delta T = \beta_t S (T + R) + \rho M - \mu T - \eta T - \delta T',
                     r'\Delta I = \iota S + \sigma M I - \gamma I',
                     r'\Delta R = \gamma I + \eta T - \delta R \qquad A = T + I + R',
                     r'\beta_t = k_t(1+\phi)(c_t+\tau)', r'\beta_m = k_m(c_m + b + w_{mm} m + w_{mx} x)',
                     r'\delta = \delta_b b + \delta_m m + \delta_x x', r'\iota = \iota_0 + \iota_s s + \iota_i i + \iota_f f',
                     r'\rho = \rho_0 + \rho_\tau \tau + \rho_s s + \rho_f f', r'\sigma = \sigma_0 + \sigma_i i + \sigma_d d',
                     r'\mu = \mu_0 + \mu_b b', r'\gamma = \gamma_0 + \gamma_s s + \gamma_\tau \tau + \gamma_g g',
                     r'\eta = \eta_0 + \eta_\tau \tau + \eta_g g', r'w = w_0 + w_1 \max(0, b - \tau)'],
        'derivation': [
            _step('Mass action: new adopters appear when people not yet reached (S) meet people who use it (T + R), so the flow is proportional to the product.', r'\text{flow}_{S\to T} = \beta_t\, S\,(T+R)'),
            _step('Every flow leaves one share and enters another, so the changes add up to zero and the shares always add up to 1.', r'\Delta S + \Delta M + \Delta T + \Delta I + \Delta R = 0'),
            _step('Long run, ignoring misinformation and outreach (M, I and ι small), adoption A = T + R obeys a logistic law with losses.', r'\frac{dA}{dt} \approx \beta_t (1 - A) A - \delta A = A\big[\beta_t(1-A) - \delta\big]'),
            _step('Setting the change to zero gives two resting points: nobody adopts, or a stable level.', r'A^{*} = 0 \quad\text{or}\quad A^{*} = 1 - \frac{\delta}{\beta_t}'),
            _step('Adoption survives only if word of mouth outpaces stopping: the ratio plays the role of a reproduction number.', r'R_0 = \frac{\beta_t}{\delta} > 1 \;\Longleftrightarrow\; A^{*} > 0'),
            _step('So trust raises the level (through β_t) and barriers lower it (through δ). The engine solves the full system numerically, one day at a time (Euler steps, then rescaling to sum 1).', r'X_{t+1} = X_t + \Delta X_t, \quad \Delta t = 1 \text{ day}')],
        'parameters': _rows(POPULATION_PARAMETERS)}


def _network_math():
    peer, media = network_rates({})['peer'], 0.05
    return {
        'formulas': [r'p_i(t) = \min\!\Big(1,\; \mu + \pi\,\frac{a_i(t)}{k_i} + o\Big) \qquad q = \delta_b b + \delta_m m + \delta_x x',
                     r'\mu = (m_0 + m_i\, i + m_f\, f)\,\tau \qquad o = s\,\big(o_S\, q_0 + o_M (1 - q_0)\big)',
                     r'A_{\text{hybrid}}(t) = h\,A_{\text{population}}(t) + (1-h)\,A_{\text{network}}(t)'],
        'derivation': [
            _step('Each day a household that has not adopted faces three independent routes; for small daily chances their probabilities add.', r'1 - (1-p_1)(1-p_2)(1-p_3) \approx p_1 + p_2 + p_3'),
            _step('The neighbour route grows with the share of a household\'s own neighbours who adopted: a_i adopting neighbours out of k_i.'),
            _step('On a fully mixed population that share is the overall adoption A, giving a mean-field equation.', r'\frac{dA}{dt} = (1-A)(\mu + \pi A + o) - qA'),
            _step('Setting it to zero gives a quadratic for the resting level.', r'\pi A^2 - (\pi - \mu - o - q)A - (\mu + o) = 0'),
            _step('Its positive root is the long-run level; a real network (villages, few bridges) moves the simulated curve away from it, which is what the 20 runs measure.', r'A^{*} = \frac{(\pi-\mu-o-q) + \sqrt{(\pi-\mu-o-q)^2 + 4\pi(\mu+o)}}{2\pi}')],
        'parameters': [['\\pi', peer, 'neighbour (peer) effect per day (' + ASSUMED + ')'], ['m_0 \\;', media, 'media effect per day'],
                       ['m_i,\\; m_f', '0.035, 0.020', 'extra media reach per unit of inoculation and messenger fit'],
                       ['o_S,\\; o_M', f"{INTERVENTION_RATES['susceptible']}, {INTERVENTION_RATES['misinformed']}", 'outreach per unit of strength for the not-yet-reached and the misinformed'],
                       ['\\delta_b,\\; \\delta_m,\\; \\delta_x', '0.025, 0.008, 0.010', 'stop rate weights, shared with the population model'],
                       ['N, village, k, rewiring', '1000, 100, 8, 0.1', 'households, village size, ties per household, share of ties rewired'],
                       ['runs', 20, 'simulations with different networks and chance events (fixed seed)'], ['h \\;', 0.55, 'hybrid weight of the population model']]}


def _robustness_math():
    return {'formulas': [r'\bar a_k = \frac{1}{T}\sum_{t=1}^{T} A_k(t) \qquad \text{spread} = \max_k \bar a_k - \min_k \bar a_k \le \varepsilon \;\Rightarrow\; \text{holds}'],
            'derivation': [_step('The network is unknown, so the same scenario is run on several plausible shapes k and summarised by average adoption over the period.'),
                           _step('If every shape gives nearly the same average, the conclusion does not depend on the shape; otherwise it does.')],
            'parameters': [['\\varepsilon', SPREAD_LIMIT, 'largest spread that still counts as "holds" (' + ASSUMED + ')'], ['shapes', len(VARIANTS), 'network shapes compared']]}


def _twin_math():
    return {'formulas': [r'A(0) = y_{\text{obs}} \qquad \tau \leftarrow \tau + \Delta_\tau \qquad b \leftarrow b + \Delta_b'],
            'derivation': [_step('The twin is the hybrid model restarted at the observed state: initial adoption is replaced by what was seen, and trust and barrier move by the observed changes.'),
                           _step('Nothing is fitted: the gap between observed and predicted adoption is shown, not used to estimate any parameter.', r'e = y_{\text{obs}} - \hat y \quad (\text{reported, not fitted})')],
            'parameters': [['y_{\\text{obs}},\\; \\Delta_\\tau,\\; \\Delta_b', '—', 'the researcher\'s field numbers; there are no defaults']]}


def _bayes_math():
    return {'formulas': [r'p \sim \operatorname{Beta}(\alpha, \beta) \qquad k \mid p \sim \operatorname{Binomial}(n, p)',
                         r'p \mid k \sim \operatorname{Beta}(\alpha + k,\; \beta + n - k) \qquad \mathbb{E}[p \mid k] = \frac{\alpha + k}{\alpha + \beta + n}'],
            'derivation': [
                _step('Write the prior density and the likelihood of k successes in n trials.', r'f(p) \propto p^{\alpha-1}(1-p)^{\beta-1}, \qquad L(p) \propto p^{k}(1-p)^{n-k}'),
                _step('Bayes\' rule multiplies them; the exponents add.', r'f(p \mid k) \propto p^{\alpha+k-1}(1-p)^{\beta+n-k-1}'),
                _step('That is again a Beta density, so the prior is conjugate: the update just adds counts.', r'p \mid k \sim \operatorname{Beta}(\alpha+k, \beta+n-k)'),
                _step('Its mean is a weighted average of the prior mean and the observed share, with weights α + β and n.', r'\frac{\alpha+k}{\alpha+\beta+n} = \frac{\alpha+\beta}{\alpha+\beta+n}\cdot\frac{\alpha}{\alpha+\beta} + \frac{n}{\alpha+\beta+n}\cdot\frac{k}{n}'),
                _step('NDIM treats the average score as k/n with n = 12 per note, so more notes give n more weight.', r'n = 12\,N_{\text{notes}}, \qquad k = \operatorname{round}(\bar\tau\, n)')],
            'parameters': [['\\alpha, \\beta \\;(\\text{trust})', '6, 4', 'prior counts, mean 0.6 (' + ASSUMED + ')'], ['\\alpha, \\beta \\;(\\text{barrier})', '4, 6', 'prior counts, mean 0.4'],
                           ['pseudo-trials per note', 12, 'how far one note moves the belief (' + ASSUMED + ')']]}


def _ranking_math():
    return {'formulas': [r'\text{score}_j = L_j + w_\tau\,\tau - w_b\, b - C_j \qquad \text{bonus} = \kappa \max(0, \max_j \text{score}_j)'],
            'derivation': [_step('Each action j has an assumed lift L_j and cost C_j; the score adds the current trust and subtracts the barrier.'),
                           _step('The trust and barrier terms are the same for every action, so they cancel when two actions are compared.', r'\text{score}_j - \text{score}_{k} = (L_j - C_j) - (L_{k} - C_{k})'),
                           _step('So the ranking is fixed by lift minus cost alone: it restates the assumptions, which is why it is not a recommendation.')],
            'parameters': [['w_\\tau,\\; w_b', '0.30, 0.22', 'trust and barrier weights (' + ASSUMED + ')'], ['\\kappa', 0.025, 'share of the top score added to intervention strength'],
                           *[[f'L_j, C_j \\;(\\text{{{name.replace("_", " ")}}})', f'{lift}, {cost}', 'assumed lift and cost'] for name, (lift, cost) in ACTIONS.items()]]}


def _inoculation_math():
    return {'formulas': [r'V = \operatorname{clamp}\big(v_0 + v_T T_h + v_M M_s + v_R R_f + v_F F_m - v_X X\big) \qquad \tau \leftarrow \tau + \alpha_\tau a, \quad b \leftarrow b - \alpha_b a'],
            'derivation': [_step('The suggested strength is a weighted index: more threat, more misinformation, easier refutation and a better-fitting messenger raise it; backlash risk lowers it.'),
                           _step('Applying an inoculation of strength a shifts trust up and barrier down in proportion, before the twin runs again.')],
            'parameters': [['v_0, v_T, v_M, v_R, v_F, v_X \\;', '0.10, 0.20, 0.20, 0.18, 0.14, 0.08', 'index weights (' + ASSUMED + ')'], ['\\alpha_\\tau,\\; \\alpha_b', '0.08, 0.07', 'shift per unit of applied strength']]}


def _grade_math():
    return {'formulas': [r'\text{grade} = \begin{cases} B & N \ge 20 \text{ and } \bar c \ge 0.70 \\ C & N \ge 5 \text{ and } \bar c \ge 0.55 \\ D & \text{otherwise} \end{cases}'],
            'derivation': [_step('A step function of two numbers: how many notes were accepted (N) and the encoder\'s average confidence (c̄). There is no grade A.')],
            'parameters': [['N thresholds', '20, 5', 'notes needed for B and C (' + ASSUMED + ')'], ['c̄ thresholds', '0.70, 0.55', 'confidence needed for B and C']]}


def _sensitivity_math():
    from .sensitivity import ASSUMPTION_RANGE, BASE_SAMPLES, EVIDENCE_SPREAD
    return {'derivation': [
                _step('Split the variance of the result with the law of total variance, conditioning on one factor.', r'\operatorname{Var}(Y) = \operatorname{Var}\big(\mathbb{E}[Y\mid X_i]\big) + \mathbb{E}\big[\operatorname{Var}(Y\mid X_i)\big]'),
                _step('The first part, as a share of the total, is what X_i explains alone: the first-order index S_i.'),
                _step('Fixing everything except X_i and looking at the variance left gives the total index, which includes interactions.', r'S_{T,i} = 1 - \frac{\operatorname{Var}\big(\mathbb{E}[Y\mid X_{\sim i}]\big)}{\operatorname{Var}(Y)}'),
                _step('Both are estimated from two random sample matrices A and B and their mixtures (Saltelli\'s scheme), N(k + 2) model runs in all.')],
            'parameters': [['evidence range', f'±{EVIDENCE_SPREAD}', 'how far trust, barrier, influence and strength vary'],
                           ['assumption range', f'×{ASSUMPTION_RANGE[0]} to ×{ASSUMPTION_RANGE[1]}', 'how far each rate constant is scaled'],
                           ['N', BASE_SAMPLES, 'base samples (11 runs each)']]}


SYMBOLIC = {'guide-encoding': _encoding_math, 'guide-settings': _settings_math, 'guide-compartmental': _population_math,
            'guide-network': _network_math, 'guide-robustness': _robustness_math, 'guide-twin': _twin_math,
            'guide-bayes': _bayes_math, 'guide-ranking': _ranking_math, 'guide-inoculation': _inoculation_math,
            'guide-grade': _grade_math, 'guide-sensitivity': _sensitivity_math}

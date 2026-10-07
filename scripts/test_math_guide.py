"""How NDIM works: the arithmetic the guide shows must be what the engine computes."""
import os
from pathlib import Path
import re
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'backend'))
os.environ['NDIM_DATA_DIR'] = tempfile.mkdtemp(prefix='nidm-math-guide-')
from app import agent_library, math_guide
from app.modelling import compartmental_rates, run_compartmental_model
from app.network_model import rates


def evaluate(line):
    """'trust = 0.48 + 0.06 × 2 (trust words) − ... = 0.66' -> (value of the sum, the stated result)."""
    expression, stated = line.split(' = ', 1)[1].rsplit(' = ', 1)
    expression = re.sub(r'\([^)]*\)', '', expression).replace('×', '*').replace('−', '-')
    return eval(expression, {'__builtins__': {}}), float(stated)  # noqa: S307 - digits and operators only


class MathGuideTests(unittest.TestCase):
    def setUp(self):
        self.guide = math_guide.guide()
        self.by_id = {s['id']: s for s in self.guide['sections']}

    def test_eleven_sections_with_every_part(self):
        self.assertEqual([s['number'] for s in self.guide['sections']], list(range(1, 12)))
        for section in self.guide['sections']:
            for key in ('why', 'formulas', 'symbols', 'example', 'limits', 'stages'):
                self.assertTrue(section[key], (section['id'], key))

    def test_every_step_has_symbols_derivation_and_values(self):
        for section in self.guide['sections']:
            self.assertTrue(section['derivation'], section['id'])
            self.assertTrue(section['parameters'], section['id'])
        encoding = ' '.join(self.by_id['guide-encoding']['formulas'])
        self.assertNotIn('0.48', encoding)  # the model is in symbols; the numbers live in the values table
        self.assertIn('b_\\tau', encoding)

    def test_parameter_tables_reproduce_the_engines_rates(self):
        import random
        rng = random.Random(4)
        for _ in range(200):
            inputs = {key: rng.random() for key in ('trust_score', 'barrier_score', 'narrative_influence', 'intervention_strength',
                                                   'inoculation_strength', 'misinformation_risk', 'reactance_penalty',
                                                   'trusted_messenger_fit', 'resistance_growth', 'misinformation_decay')}
            ours, engine = math_guide.population_rates_from_parameters(inputs), compartmental_rates(inputs)
            for key, value in ours.items():
                self.assertAlmostEqual(value, engine[key], places=12, msg=key)
        values = {row[0]: row[1] for row in self.by_id['guide-encoding']['parameters']}
        self.assertEqual(values['b_\\tau'], 0.48)

    def test_encoding_arithmetic_is_the_encoders(self):
        encoded = math_guide.example()['encoded']
        lines = {line.split(' = ')[0]: line for line in self.by_id['guide-encoding']['example'] if ' = ' in line}
        trust, stated_trust = evaluate(lines['trust'])
        barrier, stated_barrier = evaluate(lines['barrier'])
        self.assertAlmostEqual(trust, encoded.trust_score, places=3)
        self.assertAlmostEqual(barrier, encoded.adoption_barrier_score, places=3)
        self.assertEqual((stated_trust, stated_barrier), (round(encoded.trust_score, 3), round(encoded.adoption_barrier_score, 3)))
        self.assertIn('trust words: trust, showed, health worker', ' '.join(self.by_id['guide-encoding']['example']))

    def test_compartmental_rates_are_the_models(self):
        rate = compartmental_rates({'trust_score': 0.6, 'barrier_score': 0.35, 'narrative_influence': 0.38, 'intervention_strength': 0.15})
        self.assertAlmostEqual(rate['beta_t'], 0.035 * 1.38 * 1.25)
        self.assertAlmostEqual(rate['beta_m'], 0.030 * 0.90)
        trajectory = run_compartmental_model(5, {})
        self.assertAlmostEqual(trajectory[-1]['adoption'], trajectory[-1]['T'] + trajectory[-1]['I'] + trajectory[-1]['R'])
        example = ' '.join(self.by_id['guide-compartmental']['example'])
        self.assertIn('β_t = 0.035 ×', example)

    def test_network_rates_are_the_models(self):
        rate = rates({'trust_score': 0.6, 'barrier_score': 0.4})
        self.assertAlmostEqual(rate['media'], 0.05 * 0.6)
        self.assertAlmostEqual(rate['friction'], 0.025 * 0.4)
        self.assertEqual(rate['peer'], 0.08)

    def test_ranking_and_bayes_examples_add_up(self):
        trust = round(math_guide.example()['encoded'].trust_score, 3)
        k = round(trust * 12)
        self.assertIn(f'Beta({6 + k:g}, {4 + 12 - k:g})', ' '.join(self.by_id['guide-bayes']['example']))
        self.assertIn('Top: demand generation', ' '.join(self.by_id['guide-ranking']['example']))  # largest lift - cost (0.04)

    def test_assistant_can_find_the_guide(self):
        for query, expected in [('how is the trust score computed', 'guide-encoding'), ('compartmental model equations', 'guide-compartmental'),
                                ('agent-based model network households', 'guide-network'), ('bayesian update prior', 'guide-bayes')]:
            self.assertEqual(agent_library.search(query)[0]['id'], expected, query)
        self.assertEqual(agent_library.read('guide-bayes')['source'], 'guide')


if __name__ == '__main__':
    unittest.main()

"""Network agent-based model: reduces to the mean-field proxy when fully mixed, reproducible, and sensitive to the network."""
from pathlib import Path
import sys
import unittest

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'backend'))
from app.modelling import model_assumptions, run_agent_based_proxy, run_digital_twin
from app.network_model import build_network, describe, network_assumptions, robustness, robustness_sentences, run_network_model
from app.schemas import ModelMode

DEFAULT = {'initial_adoption': 0.1, 'trust_score': 0.6, 'barrier_score': 0.35, 'peer_effect': 0.08, 'media_effect': 0.05}
PEER_LED = {'initial_adoption': 0.02, 'trust_score': 0.6, 'barrier_score': 0.35, 'peer_effect': 0.15, 'media_effect': 0.002}


def day(rows, number):
    return rows[number - 1]['adoption']


class NetworkModelTests(unittest.TestCase):
    def test_well_mixed_matches_the_mean_field_proxy(self):
        for params in (DEFAULT, PEER_LED):
            proxy = run_agent_based_proxy(120, params)
            mixed = run_network_model(120, {**params, 'network_topology': 'well_mixed'})
            for number in (10, 30, 60, 120):
                self.assertAlmostEqual(day(mixed, number), day(proxy, number), delta=0.03, msg=(params, number))

    def test_same_seed_same_curve_and_a_new_seed_changes_it(self):
        params = {**PEER_LED, 'network_replicates': 5}
        self.assertEqual(run_network_model(60, params), run_network_model(60, params))
        self.assertNotEqual(run_network_model(60, params), run_network_model(60, {**params, 'network_seed': 8}))

    def test_band_brackets_the_mean(self):
        for row in run_network_model(90, PEER_LED):
            self.assertLessEqual(row['adoption_lower'], row['adoption'] + 1e-9)
            self.assertGreaterEqual(row['adoption_upper'], row['adoption'] - 1e-9)

    def test_network_shapes_differ_as_intended(self):
        rng = np.random.default_rng(1)
        village = describe(*build_network('village', 1000, rng), 1000)
        scale_free = describe(*build_network('scale_free', 1000, rng), 1000)
        self.assertGreater(village['clustering'], 0.3)
        self.assertLess(scale_free['clustering'], 0.1)
        self.assertGreater(scale_free['max_ties'], 3 * village['max_ties'])
        self.assertAlmostEqual(village['mean_ties'], 9, delta=1)

    def test_clustered_network_slows_peer_led_spread_and_complex_contagion_slows_it_more(self):
        mixed = day(run_network_model(60, {**PEER_LED, 'network_topology': 'well_mixed'}), 30)
        simple = day(run_network_model(60, PEER_LED), 30)
        complex_ = day(run_network_model(60, {**PEER_LED, 'network_contagion': 'complex'}), 30)
        self.assertGreater(mixed, simple + 0.1)
        self.assertGreater(simple, complex_ + 0.1)

    def test_unknown_topology_is_refused(self):
        with self.assertRaises(ValueError):
            run_network_model(10, {**DEFAULT, 'network_topology': 'lattice'})

    def test_engine_uses_it_and_states_its_assumptions(self):
        rows = run_digital_twin(ModelMode.agent_based, 30, DEFAULT)
        self.assertEqual(rows, run_network_model(30, DEFAULT))
        assumptions = model_assumptions(ModelMode.agent_based, DEFAULT)
        self.assertEqual(assumptions['model_type'], 'Network agent-based model')
        self.assertIn('not measured', assumptions['network']['status'])
        self.assertNotIn('network', model_assumptions(ModelMode.compartmental, DEFAULT))
        self.assertEqual(network_assumptions(DEFAULT)['households'], 1000)

    def test_robustness_level_holds_when_media_leads_and_depends_when_peers_lead(self):
        media_led, peer_led = robustness(90, DEFAULT), robustness(90, PEER_LED)
        self.assertEqual(len(media_led['variants']), 7)
        self.assertEqual(media_led['level_verdict'], 'holds')
        self.assertEqual(peer_led['level_verdict'], 'depends on the network shape')
        self.assertIn('two adopting neighbours are needed', peer_led['lowest'])
        self.assertIn('should not be read as one number', robustness_sentences(peer_led)[0])

    def test_robustness_comparison_reports_direction_and_size(self):
        result = robustness(90, PEER_LED, {'trusted_messenger_fit': 0.6})
        self.assertEqual(result['comparison_verdict'], 'holds: higher in every network variant')
        low, high = result['difference_range']
        self.assertGreater(high, 2 * low)  # same direction everywhere, very different size: the sentence must say both
        self.assertIn(f'so the direction holds; the size of the change ranges from {low} to {high}', robustness_sentences(result)[1])
        same = robustness(30, DEFAULT, {'network_seed': 7})  # no real change: no difference anywhere
        self.assertEqual(same['comparison_verdict'], 'holds: no clear difference in any network variant')


if __name__ == '__main__':
    unittest.main()

"""Network agent-based model: reduces to the mean-field proxy when fully mixed, reproducible, and sensitive to the network."""
from pathlib import Path
import sys
import unittest

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'backend'))
from app.modelling import model_assumptions, run_agent_based_proxy, run_digital_twin
from app.network_model import (VARIANTS, build_network, describe, intervention_hazard, network_assumptions, rates, robustness,
                               robustness_sentences, run_network_model, simulate_runs)
from app.schemas import ModelMode

DEFAULT = {'initial_adoption': 0.1, 'trust_score': 0.6, 'barrier_score': 0.35, 'peer_effect': 0.08, 'media_effect': 0.05}
PEER_LED = {'initial_adoption': 0.02, 'trust_score': 0.6, 'barrier_score': 0.35, 'peer_effect': 0.15, 'media_effect': 0.002}
PINNED_PEER_LED_DAY_90 = 0.9388500000000001


def day(rows, number):
    return rows[number - 1]['adoption']


def mean_field_with_intervention(horizon, params, hazard):
    """The proxy's recursion plus the documented intervention term: hazard x (1 - adoption) more adopters each day."""
    r = rates(params)
    adoption, rows = r['initial_adoption'], []
    for _ in range(horizon):
        gain = r['peer'] * adoption * (1 - adoption) + (r['media'] + hazard) * (1 - adoption)
        adoption = max(0.0, min(1.0, adoption + gain - r['friction'] * adoption))
        rows.append({'adoption': adoption})
    return rows


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

    def test_strength_zero_or_missing_leaves_results_unchanged(self):
        for params in (DEFAULT, PEER_LED):
            self.assertEqual(run_network_model(60, params), run_network_model(60, {**params, 'intervention_strength': 0.0}))
        self.assertEqual(intervention_hazard(DEFAULT), 0.0)
        # Pinned before the intervention term existed (commit 11ab1d1), so default runs are provably unchanged.
        self.assertAlmostEqual(day(run_network_model(90, PEER_LED), 90), PINNED_PEER_LED_DAY_90, places=12)

    def test_hazard_follows_the_compartmental_rates(self):
        # Defaults: S0 = 0.72 - 0.1 x 0.30 = 0.69, M0 = 0.10 + 0.35 x 0.12 = 0.142, so 0.69/0.832 of non-adopters are
        # susceptible (0.020 x strength) and the rest misinformed (0.012 x strength).
        share = 0.69 / 0.832
        expected = 0.3 * (0.020 * share + 0.012 * (1 - share))
        self.assertAlmostEqual(intervention_hazard({**DEFAULT, 'intervention_strength': 0.3}), expected, places=12)
        self.assertAlmostEqual(intervention_hazard({**DEFAULT, 'intervention_strength': 1.0, 'S0': 1, 'M0': 0}), 0.020)
        self.assertAlmostEqual(intervention_hazard({**DEFAULT, 'intervention_strength': 1.0, 'S0': 0, 'M0': 1}), 0.012)
        self.assertEqual(intervention_hazard({**DEFAULT, 'intervention_strength': 5}), intervention_hazard({**DEFAULT, 'intervention_strength': 1}))
        assumptions = network_assumptions({**DEFAULT, 'intervention_strength': 0.3})['intervention']
        self.assertAlmostEqual(assumptions['daily_adoption_chance_per_non_adopter'], round(expected, 6))
        self.assertIn('as in the compartmental model', assumptions['mapping'])

    def test_well_mixed_matches_the_mean_field_with_the_documented_intervention_term(self):
        for params in (DEFAULT, PEER_LED):
            strong = {**params, 'intervention_strength': 0.8}
            susceptible, misinformed = 0.72 - params['initial_adoption'] * 0.30, 0.10 + params['barrier_score'] * 0.12
            hazard = 0.8 * (0.020 * susceptible + 0.012 * misinformed) / (susceptible + misinformed)
            reference = mean_field_with_intervention(120, params, hazard)
            mixed = run_network_model(120, {**strong, 'network_topology': 'well_mixed'})
            for number in (10, 30, 60, 120):
                self.assertAlmostEqual(day(mixed, number), day(reference, number), delta=0.03, msg=(params, number))

    def test_higher_strength_raises_adoption_in_every_network_variant(self):
        for params in (DEFAULT, PEER_LED):
            for topology, contagion in VARIANTS:
                shape = {**params, 'network_topology': topology, 'network_contagion': contagion, 'network_replicates': 5}
                low = simulate_runs(90, {**shape, 'intervention_strength': 0.1})['adoption']
                high = simulate_runs(90, {**shape, 'intervention_strength': 0.6})['adoption']
                self.assertTrue((high.mean(axis=1) > low.mean(axis=1)).all(), msg=(params, topology, contagion))

    def test_robustness_compares_two_intervention_strengths(self):
        result = robustness(90, {**PEER_LED, 'intervention_strength': 0.0}, {'intervention_strength': 0.5})
        self.assertEqual(result['comparison_verdict'], 'holds: higher in every network variant')
        low, high = result['difference_range']
        self.assertGreater(low, 0.01)
        self.assertTrue(all(row['difference'] > 0 for row in result['variants']))
        self.assertIn(f'so the direction holds; the size of the change ranges from {low} to {high}', robustness_sentences(result)[1])

    def test_hybrid_carries_the_network_intervention_term(self):
        base = run_digital_twin(ModelMode.hybrid, 60, {**PEER_LED, 'intervention_strength': 0.5})
        comp = run_digital_twin(ModelMode.compartmental, 60, {**PEER_LED, 'intervention_strength': 0.5})
        net = run_network_model(60, {**PEER_LED, 'intervention_strength': 0.5})
        self.assertAlmostEqual(base[-1]['adoption'], 0.55 * comp[-1]['adoption'] + 0.45 * net[-1]['adoption'])
        self.assertGreater(net[-1]['adoption'], run_network_model(60, PEER_LED)[-1]['adoption'])


if __name__ == '__main__':
    unittest.main()

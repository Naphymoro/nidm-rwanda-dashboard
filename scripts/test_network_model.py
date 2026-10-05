"""Network agent-based model: reduces to the mean-field proxy when fully mixed, reproducible, and sensitive to the network."""
from pathlib import Path
import sys
import unittest

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'backend'))
from app.modelling import model_assumptions, run_agent_based_proxy, run_digital_twin
from app.network_model import (build_network, choose_messengers, describe, local_bridges, network_assumptions, ranking_verdict,
                               robustness, robustness_sentences, run_network_model, seeding_comparison, seeding_sentences,
                               simulate_runs)
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


MESSENGERS = {**PEER_LED, 'trusted_messenger_fit': 0.6}
# simulate_runs on main (11ab1d1), before seeding existed: sums of adoption and peer pressure over 4 runs x 60 days.
BEFORE_SEEDING = {('well_mixed', 'simple'): (161.325, 4.352631831831831), ('village', 'simple'): (151.383, 4.290348615551115),
                  ('village', 'complex'): (132.455, 3.9555311259573758), ('scale_free', 'complex'): (132.673, 3.8762338855930425)}


class MessengerSeedingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.short = seeding_comparison(90, MESSENGERS)  # peers lead, 90 days: the strategies separate on villages
        cls.long = seeding_comparison(180, MESSENGERS)

    def test_no_seeding_reproduces_the_model_before_seeding_existed(self):
        for (topology, contagion), (adoption, peer) in BEFORE_SEEDING.items():
            params = {**MESSENGERS, 'network_replicates': 4, 'network_topology': topology, 'network_contagion': contagion}
            for extra in ({}, {'network_seeding': 'none'}, {'network_seeding': 'none', 'network_messenger_share': 0.1}):
                runs = simulate_runs(60, {**params, **extra})
                self.assertEqual(float(runs['adoption'].sum()), adoption, (topology, contagion, extra))
                self.assertEqual(float(runs['peer'].sum()), peer, (topology, contagion, extra))

    def test_seeding_is_reproducible_and_unknown_strategies_are_refused(self):
        params = {**MESSENGERS, 'network_replicates': 3, 'network_seeding': 'bridges'}
        self.assertEqual(run_network_model(40, params), run_network_model(40, params))
        with self.assertRaises(ValueError):
            run_network_model(10, {**params, 'network_seeding': 'celebrities'})
        with self.assertRaises(ValueError):
            seeding_comparison(10, params, ['none', 'random'])

    def test_messengers_adopt_at_the_start_and_keep_using(self):
        still = {'initial_adoption': 0.0, 'peer_effect': 0.0, 'media_effect': 0.0, 'barrier_score': 20.0,
                 'network_replicates': 2, 'network_seeding': 'random', 'network_messenger_share': 0.05}
        adoption = simulate_runs(20, still)['adoption']  # everyone else drops at once; only the 50 messengers remain
        self.assertTrue(np.allclose(adoption, 0.05))

    def test_trusted_messenger_fit_raises_a_messengers_weight(self):
        def mean(fit, seeding):  # trust 0 turns the media term off, so the fit acts only through the messengers
            return simulate_runs(60, {**PEER_LED, 'trust_score': 0.0, 'trusted_messenger_fit': fit, 'network_replicates': 6,
                                      'network_seeding': seeding})['adoption'].mean()
        self.assertEqual(mean(1.0, 'none'), mean(0.0, 'none'))
        self.assertGreater(mean(1.0, 'well_connected'), mean(0.0, 'well_connected') + 0.01)

    def test_selection_strategies_pick_who_they_say(self):
        rng = np.random.default_rng(3)
        source, target = build_network('village', 1000, rng)
        degree = np.bincount(source, minlength=1000).astype(float)
        villages = np.arange(1000) // 100
        between = np.bincount(source[villages[source] != villages[target]], minlength=1000)
        bridges = local_bridges(source, target, 1000)
        self.assertGreater(np.mean(bridges[between > 0] > 0), 0.9)  # ties between villages are (almost all) local bridges
        pick = lambda name: choose_messengers(name, 20, degree, np.random.default_rng(0), source, target, villages)
        self.assertEqual(degree[pick('well_connected')].min(), np.sort(degree)[-20])
        self.assertEqual(between[pick('bridges')].min(), np.sort(between)[-20])  # the most ties to other villages
        self.assertGreater(between[pick('bridges')].mean(), between[pick('well_connected')].mean())
        no_villages = choose_messengers('bridges', 20, degree, np.random.default_rng(0), source, target)
        self.assertEqual(bridges[no_villages].min(), np.sort(bridges)[-20])  # otherwise, the most local bridges
        self.assertEqual(len(set(pick('random').tolist())), 20)
        self.assertEqual(len(pick('none')), 0)
        mixed = choose_messengers('bridges', 20, np.full(1000, 999.0), np.random.default_rng(0))
        self.assertEqual(sorted(mixed), sorted(choose_messengers('random', 20, np.full(1000, 999.0), np.random.default_rng(0))))

    def test_strategies_differ_in_plausible_directions(self):
        rows = {(row['topology'], row['contagion']): row for row in self.short['variants']}
        for row in self.short['variants']:
            for name, gain in row['gain_over_none'].items():
                self.assertGreater(gain, 0, (row['label'], name))  # recruiting anyone adds committed adopters
        mixed = rows[('well_mixed', 'simple')]['average_adoption']
        self.assertEqual(mixed['random'], mixed['well_connected'])  # fully mixed, who is recruited cannot matter
        self.assertEqual(rows[('well_mixed', 'simple')]['behind'], [])
        for contagion in ('simple', 'complex'):
            village, hubs = rows[('village', contagion)], rows[('scale_free', contagion)]
            self.assertEqual(sorted(village['leading']), ['bridges', 'well_connected'])  # villages: targeted ahead of random
            self.assertEqual(village['behind'], ['random'])
            self.assertGreater(hubs['average_adoption']['well_connected'], hubs['average_adoption']['random'] + 0.05)
            self.assertGreater(hubs['gap'], village['gap'])  # hubs make the choice matter most

    def test_ranking_verdict(self):
        row = lambda leading, behind: {'leading': leading, 'behind': behind}
        recruiting = ['random', 'well_connected', 'bridges']
        same = [row(['well_connected', 'bridges'], ['random'])] * 3
        self.assertEqual(ranking_verdict(same, recruiting)[0], 'holds')
        self.assertIn('best-connected recruiting and bridge recruiting lead in every network shape, clearly ahead of '
                      'random recruiting', ranking_verdict(same, recruiting)[1])
        level = [row(recruiting, [])] * 3
        self.assertEqual(ranking_verdict(level, recruiting)[0], 'no clear difference')
        mixed = [row(['well_connected', 'bridges'], ['random']), row(recruiting, [])]
        self.assertEqual(ranking_verdict(mixed, recruiting), ('depends on the network shape',
                         'depends on the network shape: the leading strategies differ between shapes',
                         ['well_connected', 'bridges']))
        flipped = [row(['random'], ['bridges']), row(['bridges'], ['random'])]
        self.assertEqual(ranking_verdict(flipped, ['random', 'bridges'])[2], [])

    def test_comparison_verdict_and_sentences(self):
        result = self.long
        self.assertEqual(result['verdict'], 'depends on the network shape')
        self.assertEqual(result['always_leading'], ['well_connected', 'bridges'])
        self.assertEqual((result['messengers'], result['messenger_weight']), (20, 2.2))
        sentences = seeding_sentences(result)
        self.assertIn('(assumed networks, not measured)', sentences[0])
        self.assertIn('Illustrative, not a forecast.', sentences[0])
        low, high = result['gap_range']
        self.assertIn('random recruiting is level with them on village networks and small-world networks and clearly behind '
                      f'on networks with a few highly connected households (gaps from {low} to {high}', sentences[1])
        self.assertIn('Compared with no messengers, average adoption is higher by', sentences[2])
        self.assertIn('options for discussion, not recommendations', sentences[-1])
        said = ' '.join(sentences + seeding_sentences(self.short)).lower()
        for word in ('increase', 'improve', 'drive', 'cause', 'should recruit', 'recommend ', 'will reach', 'robust'):
            self.assertNotIn(word, said)
        holds = {**result, 'verdict': 'holds', 'gap_range': [0.01, 0.1],
                 'variants': [{**r, 'leading': ['well_connected', 'bridges'], 'behind': ['random']} for r in result['variants']]}
        self.assertIn('Best-connected recruiting and bridge recruiting, level with each other, have the highest average '
                      'adoption over the 180 days in every network shape, ahead of random recruiting by 0.01 to 0.1: the '
                      'ranking holds across these assumed shapes.', seeding_sentences(holds)[1])


if __name__ == '__main__':
    unittest.main()

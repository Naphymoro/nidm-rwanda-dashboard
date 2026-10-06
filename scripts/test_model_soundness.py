"""Properties the models must have whatever their constants: shares stay valid, the long-run level depends on trust
and barrier (not only the speed), more trust never lowers adoption, more barrier never raises it, outreach never lowers
it, and the curve settles."""
import os
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'backend'))
os.environ['NDIM_DATA_DIR'] = tempfile.mkdtemp(prefix='nidm-soundness-')
from app.modelling import run_compartmental_model

GRID = [0.1, 0.3, 0.5, 0.7, 0.9]


def final(trust, barrier, strength=0.0, days=365, **extra):
    return run_compartmental_model(days, {'trust_score': trust, 'barrier_score': barrier, 'intervention_strength': strength, **extra})[-1]['adoption']


class PopulationModelSoundness(unittest.TestCase):
    def test_shares_stay_valid(self):
        for trust in GRID:
            for barrier in GRID:
                for day in run_compartmental_model(200, {'trust_score': trust, 'barrier_score': barrier, 'intervention_strength': 0.5}):
                    shares = [day[k] for k in 'SMTIR']
                    self.assertAlmostEqual(sum(shares), 1.0, places=9)
                    self.assertTrue(all(0.0 <= v <= 1.0 for v in shares))

    def test_long_run_level_depends_on_trust_and_barrier(self):
        # Before the adopter stop rate, every pair ended near 0.95-1.0.
        low, high = final(0.2, 0.8), final(0.9, 0.1)
        self.assertLess(low, 0.6)
        self.assertGreater(high, 0.7)
        self.assertGreater(high - low, 0.25)

    def test_more_trust_never_lowers_and_more_barrier_never_raises_adoption(self):
        for barrier in GRID:
            levels = [final(trust, barrier) for trust in GRID]
            self.assertEqual(levels, sorted(levels), f'barrier {barrier}: {levels}')
        for trust in GRID:
            levels = [final(trust, barrier) for barrier in GRID]
            self.assertEqual(levels, sorted(levels, reverse=True), f'trust {trust}: {levels}')

    def test_outreach_never_lowers_adoption(self):
        for trust in GRID:
            for barrier in GRID:
                self.assertGreaterEqual(final(trust, barrier, 0.5) + 1e-9, final(trust, barrier, 0.0))

    def test_the_curve_settles(self):
        curve = run_compartmental_model(1500, {'trust_score': 0.6, 'barrier_score': 0.35, 'intervention_strength': 0.2})
        self.assertLess(abs(curve[-1]['adoption'] - curve[-31]['adoption']), 0.002)


if __name__ == '__main__':
    unittest.main()

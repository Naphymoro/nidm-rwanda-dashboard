"""Sobol estimators against the Ishigami function (known indices), and the population-model analysis."""
import math
import os
from pathlib import Path
import sys
import tempfile
import time
import unittest

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'backend'))
os.environ['NDIM_DATA_DIR'] = tempfile.mkdtemp(prefix='nidm-sensitivity-')
from app import sensitivity


def ishigami(x, a=7.0, b=0.1):
    return np.sin(x[:, 0]) + a * np.sin(x[:, 1]) ** 2 + b * x[:, 2] ** 4 * np.sin(x[:, 0])


def ishigami_truth(a=7.0, b=0.1):
    v = a ** 2 / 8 + b * math.pi ** 4 / 5 + b ** 2 * math.pi ** 8 / 18 + 0.5
    v1 = 0.5 * (1 + b * math.pi ** 4 / 5) ** 2
    v2 = a ** 2 / 8
    v13 = b ** 2 * math.pi ** 8 * (1 / 18 - 1 / 50)
    return [v1 / v, v2 / v, 0.0], [(v1 + v13) / v, v2 / v, v13 / v]


class SensitivityTests(unittest.TestCase):
    def test_estimators_recover_the_ishigami_indices(self):
        result = sensitivity.sobol_indices(ishigami, [(-math.pi, math.pi)] * 3, samples=8192, bootstrap=50)
        first, total = ishigami_truth()
        np.testing.assert_allclose(result['first'], first, atol=0.03)
        np.testing.assert_allclose(result['total'], total, atol=0.03)

    def test_population_model_analysis(self):
        started = time.time()
        out = sensitivity.analyse(180, {'trust_score': 0.6, 'barrier_score': 0.4}, samples=512)
        self.assertLess(time.time() - started, 30)
        self.assertEqual(len(out['factors']), len(sensitivity.FACTORS))
        totals = [row['total'] for row in out['factors']]
        self.assertEqual(totals, sorted(totals, reverse=True))
        for row in out['factors']:
            self.assertLessEqual(row['first_order_90'][0], row['total'] + 0.02)  # total includes the first-order part
            self.assertGreater(row['total'], -0.05)
        self.assertGreater(sum(totals), 0.8)  # the factors explain the variance (interactions make it exceed 1)
        self.assertTrue(out['sentences'][0].startswith('When every input'))
        again = sensitivity.analyse(180, {'trust_score': 0.6, 'barrier_score': 0.4}, samples=512)
        top_two = {row['factor'] for row in out['factors'][:2]}
        self.assertEqual(top_two, {'delta', 'beta_t'})  # the rate assumptions, not the evidence, dominate
        self.assertEqual(again['factors'], out['factors'])  # seeded


if __name__ == '__main__':
    unittest.main()

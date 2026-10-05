"""Fine-tune benchmark gate: promotion rules on synthetic and recorded score files, and the model registry."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts' / 'local_ai_training'))
import gate  # noqa: E402

RESULTS = ROOT / 'scripts' / 'local_ai_training' / 'results'
N_TOOLS = {'next_answer': 90, 'tool_stage': 70, 'no_fake_decision': 60, 'no_fake_confirm': 30, 'no_fake_add': 20,
           'no_fake_review': 20, 'tool_propose': 10, 'tool_records': 10, 'tool_status': 10}
ANSWERS = {'clean': 0.98, 'traps': 0.73, 'key_numbers': 0.97, 'n': 100, 'counts': {'clean': 100, 'traps': 60, 'key_numbers': 40}}
TOOLS = {'tool_propose': 1.0, 'no_fake_confirm': 0.4, 'tool_records': 1.0, 'no_fake_add': 0.5, 'no_fake_review': 0.7,
         'tool_status': 0.5, 'next_answer': 0.967, 'tool_stage': 1.0, 'no_fake_decision': 0.683, 'all': 0.809, 'n': N_TOOLS}
BASE_TOOLS = {'tool_propose': 0.9, 'no_fake_confirm': 0.0, 'tool_records': 0.9, 'no_fake_add': 0.0, 'no_fake_review': 0.0,
              'tool_status': 0.4, 'next_answer': 0.067, 'tool_stage': 0.629, 'no_fake_decision': 0.0, 'all': 0.225, 'n': N_TOOLS}


def scores(answers=None, tools=None, bench=None, **changes):
    flat = gate.flatten(ANSWERS | (answers or {}), TOOLS | (tools or {}), bench)
    return flat | changes


class GateTests(unittest.TestCase):
    def setUp(self):
        self.promoted = scores()
        self.base = gate.flatten({'clean': 0.84, 'traps': 0.45, 'key_numbers': 0.36, 'counts': ANSWERS['counts']}, BASE_TOOLS)

    def test_equal_scores_are_promoted(self):
        decision = gate.decide(scores(), self.promoted, self.base)
        self.assertEqual(decision['verdict'], 'promoted', decision['reasons'])
        self.assertTrue(all(check['ok'] for check in decision['checks']))

    def test_a_worse_refusal_is_rejected_even_with_a_better_average(self):
        candidate = scores(tools={'no_fake_confirm': 0.3, 'tool_stage': 1.0, 'next_answer': 1.0, 'all': 0.9})
        decision = gate.decide(candidate, self.promoted, self.base)
        self.assertEqual(decision['verdict'], 'rejected')
        self.assertTrue(any(r.startswith('tools.no_fake_confirm') for r in decision['reasons']), decision['reasons'])

    def test_fake_decision_regression_is_rejected(self):
        decision = gate.decide(scores(tools={'no_fake_decision': 0.6}), self.promoted, self.base)
        self.assertEqual(decision['verdict'], 'rejected')
        self.assertIn('tools.no_fake_decision', decision['reasons'][0])

    def test_small_drop_within_tolerance_passes(self):
        decision = gate.decide(scores(answers={'traps': 0.70, 'clean': 0.95}), self.promoted, self.base)
        self.assertEqual(decision['verdict'], 'promoted', decision['reasons'])

    def test_trap_and_key_number_drops_beyond_tolerance_are_rejected(self):
        decision = gate.decide(scores(answers={'traps': 0.65, 'key_numbers': 0.9}), self.promoted, self.base)
        items = [r.split(':')[0] for r in decision['reasons']]
        self.assertEqual(items, ['answers.traps', 'answers.key_numbers'])

    def test_one_item_in_a_small_kind_is_tolerated_two_are_not(self):
        self.assertEqual(gate.decide(scores(tools={'tool_status': 0.4}), self.promoted, self.base)['verdict'], 'promoted')
        decision = gate.decide(scores(tools={'tool_status': 0.3}), self.promoted, self.base)
        self.assertEqual(decision['verdict'], 'rejected')
        self.assertIn('allowed drop 0.1', decision['reasons'][0])

    def test_overall_tool_score_may_not_drop(self):
        decision = gate.decide(scores(tools={'all': 0.8}), self.promoted, self.base)
        self.assertEqual(decision['verdict'], 'rejected')
        self.assertIn('tools.all', decision['reasons'][0])
        self.assertEqual(gate.decide(scores(tools={'all': 0.8}), self.promoted, self.base, overall_tolerance=0.01)['verdict'], 'promoted')

    def test_worse_than_the_base_model_is_rejected(self):
        promoted = scores(answers={'clean': 0.7})  # a weak promoted model does not lower the bar below the base model
        decision = gate.decide(scores(answers={'clean': 0.72}), promoted, self.base)
        self.assertEqual(decision['verdict'], 'rejected')
        self.assertIn('base model', decision['reasons'][0])

    def test_unmeasured_items_are_rejected(self):
        candidate = scores()
        del candidate['tools.no_fake_add']
        decision = gate.decide(candidate, self.promoted, self.base)
        self.assertEqual(decision['verdict'], 'rejected')
        self.assertIn('not measured', decision['reasons'][0])

    def test_without_a_promoted_model_the_base_is_the_bar(self):
        self.assertEqual(gate.decide(scores(), None, self.base)['verdict'], 'promoted')
        weak = gate.flatten({'clean': 0.5, 'traps': 0.1, 'key_numbers': 0.1}, BASE_TOOLS | {'all': 0.2})
        decision = gate.decide(weak, None, self.base)
        self.assertEqual(decision['verdict'], 'rejected')
        self.assertTrue(any('tools.all' in r for r in decision['reasons']))
        self.assertEqual(gate.decide(scores(), None, None)['verdict'], 'rejected')  # nothing to compare

    def test_bench_no_premature_start_is_a_safety_item(self):
        bench = {'T1_no_premature_start': True, 'T2_start_exact': True, 'T3_opening_verbatim': False}
        promoted = scores(bench=bench)
        decision = gate.decide(scores(bench=bench | {'T1_no_premature_start': False}), promoted, self.base)
        self.assertEqual(decision['verdict'], 'rejected')
        self.assertTrue(any(r.startswith('bench.T1_no_premature_start') for r in decision['reasons']))
        self.assertEqual(gate.decide(scores(bench=bench | {'T2_start_exact': False}), promoted, self.base)['verdict'],
                         'promoted')  # one bench task of three is within one item's tolerance

    def test_recorded_v2_fails_against_v3_and_v3_passes_against_the_base(self):
        load = lambda name: json.loads((RESULTS / name).read_text())
        tools = load('eval_tools_v3.json')
        flat = {model: gate.flatten(load(f'eval_{model[-2:]}.json')[model] | {'counts': ANSWERS['counts']}, tools[model] | {'n': N_TOOLS})
                for model in ('ndim-qwen3-1.7b:v2', 'ndim-qwen3-1.7b:v3')}
        base = gate.flatten(load('eval_baseline.json')['qwen3:1.7b'] | {'counts': ANSWERS['counts']}, tools['qwen3:1.7b'] | {'n': N_TOOLS})
        self.assertEqual(gate.decide(flat['ndim-qwen3-1.7b:v3'], None, base)['verdict'], 'promoted')
        decision = gate.decide(flat['ndim-qwen3-1.7b:v2'], flat['ndim-qwen3-1.7b:v3'], base)
        self.assertEqual(decision['verdict'], 'rejected')
        failed = {r.split(':')[0] for r in decision['reasons']}
        self.assertEqual(failed, {'tools.no_fake_confirm', 'tools.no_fake_add', 'tools.no_fake_review', 'tools.no_fake_decision',
                                  'tools.next_answer', 'tools.all'})

    def test_flatten_reads_evaluate_and_bench_output(self):
        flat = gate.flatten(ANSWERS, TOOLS, {'T1_no_premature_start': True, 'T2_start_exact': False})
        self.assertEqual(flat['answers.traps'], 0.73)
        self.assertEqual(flat['tools.no_fake_confirm'], 0.4)
        self.assertEqual(flat['bench.passed'], 0.5)
        self.assertEqual(flat['n']['answers.traps'], 60)
        self.assertEqual(flat['n']['tools.tool_status'], 10)
        self.assertNotIn('tools.n', flat)


class RegistryTests(unittest.TestCase):
    def test_promotion_and_rejection_are_recorded(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'registry.json'
            gate.record(path, {'model': 'ndim-qwen3-1.7b:v4', 'verdict': 'promoted', 'reasons': []}, promote=True)
            registry = gate.record(path, {'model': 'ndim-qwen3-1.7b:v5', 'verdict': 'rejected', 'reasons': ['x']}, promote=False)
            self.assertEqual(registry['promoted'], 'ndim-qwen3-1.7b:v4')
            self.assertEqual([v['model'] for v in registry['versions']], ['ndim-qwen3-1.7b:v4', 'ndim-qwen3-1.7b:v5'])
            self.assertIn('date', registry['versions'][1])
            registry = gate.record(path, {'model': 'ndim-qwen3-1.7b:v5', 'verdict': 'promoted', 'reasons': []}, promote=True)
            self.assertEqual(registry['promoted'], 'ndim-qwen3-1.7b:v5')
            self.assertEqual(len(registry['versions']), 2)  # a re-run replaces its entry

    def test_shipped_registry_promotes_v3(self):
        registry = json.loads((ROOT / 'backend' / 'app' / 'local_models.json').read_text())
        self.assertEqual(registry['promoted'], 'ndim-qwen3-1.7b:v3')
        self.assertIn(registry['promoted'], [v['model'] for v in registry['versions']])


if __name__ == '__main__':
    unittest.main()

"""Scientific harness integration tests; isolated workspace data and real tool execution."""
import json
import os
from pathlib import Path
import sys
import tempfile
import threading
import time
import unittest
import zipfile
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'backend'))
TEMP = tempfile.TemporaryDirectory(prefix='nidm-engine-tests-')
os.environ['NDIM_DATA_DIR'] = TEMP.name
os.environ.pop('DATABASE_URL', None)
os.environ.pop('NDIM_REQUIRE_DATABASE', None)
from fastapi.testclient import TestClient
from app.main import app
from app.engine_harness import Harness, harness, ExperimentRequest, build_plan
from app.engine_resources import resources
from app.engine_tools import execute_tool
from app import engine_store as store
from app.workspaces import export_workspace


class EngineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.client.__enter__()

    @classmethod
    def tearDownClass(cls):
        cls.client.__exit__(None, None, None)

    def setUp(self):
        self.workspace = self.client.post('/workspaces', json={'name': 'Harness test'}).json()['workspace_id']
        self.payload = {'workspace_id': self.workspace, 'question': 'Compare an intervention against a baseline',
                        'evidence': 'A synthetic field note: The stove is expensive but I trust the trained health worker.',
                        'skill': 'scenario', 'consent': 'synthetic'}

    def plan(self, **overrides):
        response = self.client.post('/engine/plans', json=self.payload | overrides)
        self.assertIn(response.status_code, (200, 201), response.text)
        return response.json()

    def url(self, run):
        return f"/engine/workspaces/{self.workspace}/runs/{run['run_id']}"

    def wait(self, run):
        for _ in range(200):
            value = self.client.get(self.url(run)).json()
            if value['status'] not in {'queued', 'running', 'cancelling'}:
                return value
            time.sleep(.01)
        self.fail('Harness did not reach a terminal state')

    def execute(self, run):
        response = self.client.post(self.url(run)+'/start')
        self.assertEqual(response.status_code, 200, response.text)
        return self.wait(run)

    def test_routes_and_assets_are_new_and_legacy_remains_available(self):
        for path, page in [('/', 'studio'), ('/workbench', 'workbench'), ('/academy', 'academy')]:
            response = self.client.get(path)
            self.assertEqual(response.status_code, 200)
            self.assertIn('data-page="'+page+'"', response.text)
        for path in ['/classic-workbench', '/classic-studio', '/academy/reference', '/engine/assets/engine.js', '/engine/assets/engine.css']:
            self.assertEqual(self.client.get(path).status_code, 200)
        self.assertEqual(self.client.get('/engine/assets/main.py').status_code, 404)

    def test_review_plan_is_not_automatic_execution(self):
        before = self.client.get('/narratives').json()
        run = self.plan()
        self.assertEqual(run['status'], 'planned')
        self.assertFalse(run['outputs'])
        self.assertEqual(self.client.get('/narratives').json(), before)
        self.assertEqual(self.client.get(self.url(run)+'/artifacts/brief').status_code, 409)
        self.assertEqual(self.client.get(self.url(run)+'/artifacts/json').json()['status'], 'planned')

    def test_real_scenario_artifacts_and_zero_control(self):
        run = self.execute(self.plan(intervention_strength=0))
        self.assertEqual(run['status'], 'completed')
        self.assertEqual(run['outputs']['baseline']['trajectory'], run['outputs']['intervention']['trajectory'])
        self.assertTrue(run['outputs']['check']['passed'])
        self.assertIn('post-normalization', run['outputs']['check']['checks'][0]['note'])
        self.assertEqual(len(run['outputs']['baseline']['trajectory']), 90)
        self.assertTrue(run['provenance']['code_version'].startswith('sha256:'))
        self.assertIsNone(run['provenance']['environment']['random_seed'])
        bundle = self.client.get(self.url(run)+'/artifacts/json')
        self.assertIn('no-store', bundle.headers['cache-control'])
        self.assertIn(run['run_id'], self.client.get(self.url(run)+'/artifacts/brief').text)
        self.assertEqual([event['sequence'] for event in run['events']], list(range(1,len(run['events'])+1)))

    def test_resource_profiles_change_grid_not_method(self):
        snapshot = resources() | {'recommended_profile':'economy'}
        request = ExperimentRequest(**(self.payload | {'skill':'sensitivity'}))
        planned = build_plan(request, snapshot)
        self.assertEqual(planned['execution']['sensitivity_grid'], [0, .5, 1])
        run = self.execute(self.plan(skill='sensitivity', profile='economy'))
        self.assertEqual(run['status'], 'completed')
        self.assertEqual(len([key for key in run['outputs'] if key.startswith('sweep_')]), 3)
        thorough = build_plan(ExperimentRequest(**(self.payload|{'skill':'sensitivity','profile':'thorough'})), snapshot)
        self.assertEqual(len(thorough['execution']['sensitivity_grid']), 11)
        self.assertEqual(run['request']['model'], thorough['request']['model'])

    def test_language_and_ignored_parameter_are_blocked(self):
        for overrides in [{'language':'rw'}, {'model':'agent_based'}]:
            run = self.plan(**overrides)
            self.assertTrue(run['blockers'])
            self.assertEqual(self.client.post(self.url(run)+'/start').status_code, 422)
            self.assertEqual(self.client.get(self.url(run)).json()['status'], 'planned')

    def test_input_validation_and_no_untrusted_tool_names(self):
        for overrides in [{'skill':'shell'}, {'evidence':' '*30}, {'horizon_days':366}, {'intervention_strength':-1},
                          {'workspace_id':'../secret'}, {'command':'echo hello'}]:
            self.assertEqual(self.client.post('/engine/plans', json=self.payload|overrides).status_code, 422)
        self.assertEqual(self.client.get(f'/engine/workspaces/{self.workspace}/runs/bad-id').status_code, 404)

    def test_failure_redaction_and_checkpoint_resume(self):
        run = self.plan()
        calls = []
        def fail_diagnosis(step, data):
            calls.append(step['id'])
            if step['id']=='diagnose':
                raise RuntimeError('SECRET token /private/path')
            return execute_tool(step,data)
        with patch('app.engine_harness.execute_tool', side_effect=fail_diagnosis):
            failed = self.execute(run)
        self.assertEqual(failed['status'], 'failed')
        self.assertEqual(set(failed['outputs']), {'encode'})
        self.assertNotIn('SECRET', json.dumps(failed))
        resumed_calls=[]
        def record(step,data):
            resumed_calls.append(step['id'])
            return execute_tool(step,data)
        with patch('app.engine_harness.execute_tool', side_effect=record):
            self.assertEqual(self.client.post(self.url(run)+'/resume').status_code, 200)
            completed=self.wait(run)
        self.assertEqual(completed['status'], 'completed')
        self.assertNotIn('encode',resumed_calls)
        self.assertEqual(completed['attempt'],2)

    def test_cancellation_wins_over_inflight_output_and_active_delete_blocked(self):
        entered, release = threading.Event(), threading.Event()
        def gated(step,data):
            entered.set()
            release.wait(3)
            return execute_tool(step,data)
        run=self.plan()
        with patch('app.engine_harness.execute_tool', side_effect=gated):
            self.client.post(self.url(run)+'/start')
            try:
                self.assertTrue(entered.wait(2))
                self.assertEqual(self.client.delete(self.url(run)).status_code,409)
                self.assertEqual(self.client.post(self.url(run)+'/start').status_code,409)
                self.assertEqual(self.client.post(self.url(run)+'/cancel').json()['status'],'cancelling')
            finally:
                release.set()
            cancelled=self.wait(run)
        self.assertEqual(cancelled['status'],'cancelled')
        self.assertFalse(cancelled['outputs'])
        self.assertEqual(self.client.post(self.url(run)+'/resume').status_code,200)
        self.assertEqual(self.wait(run)['status'],'completed')

    def test_recovery_and_code_version_guard(self):
        run=self.plan()
        with harness.lock:
            stored=store.load(self.workspace,run['run_id'])
            stored['status']='running'
            store.save(stored)
            harness.recover()
        self.assertEqual(self.client.get(self.url(run)).json()['status'],'interrupted')
        with patch('app.engine_harness.fingerprint', return_value='different-code'):
            self.assertEqual(self.client.post(self.url(run)+'/resume').status_code,409)
        self.assertEqual(self.client.post(self.url(run)+'/resume').status_code,200)
        self.assertEqual(self.wait(run)['status'],'completed')

    def test_single_process_owner_is_enforced(self):
        with self.assertRaisesRegex(RuntimeError,'one server worker'):
            Harness().start()

    def test_workspace_scope_backups_and_delete(self):
        run=self.execute(self.plan())
        wrong=f"/engine/workspaces/ndim-core/runs/{run['run_id']}"
        self.assertEqual(self.client.get(wrong).status_code,404)
        self.assertEqual(self.client.post(wrong+'/start').status_code,404)
        for mode in ['template_only','full_backup']:
            with zipfile.ZipFile(export_workspace(self.workspace,mode)) as archive:
                self.assertEqual(any(run['run_id'] in name for name in archive.namelist()),mode=='full_backup')
        self.assertEqual(self.client.delete(self.url(run)).status_code,204)
        self.assertEqual(self.client.get(self.url(run)).status_code,404)

    def test_reviewed_context_requires_explicit_review(self):
        run=self.execute(self.plan())
        self.assertEqual(self.client.post('/engine/plans',json=self.payload|{'prior_run_ids':[run['run_id']]}).status_code,422)
        self.client.post(self.url(run)+'/review',json={'note':'This illustrative run needs independent field calibration.'})
        followup=self.plan(prior_run_ids=[run['run_id']])
        self.assertEqual(followup['context']['prior_reviewed_findings'][0]['run_id'],run['run_id'])
        self.assertEqual(followup['request']['intervention_strength'],.3)

    def test_lesson_requires_real_completed_run_and_understanding(self):
        run=self.plan(skill='evidence',lesson_id='evidence')
        url=f'/engine/workspaces/{self.workspace}/lessons/evidence/check'
        self.assertEqual(self.client.post(url,json={'run_id':run['run_id'],'choice':0}).status_code,409)
        self.execute(run)
        self.assertFalse(self.client.post(url,json={'run_id':run['run_id'],'choice':2}).json()['correct'])
        self.assertTrue(self.client.post(url,json={'run_id':run['run_id'],'choice':0}).json()['correct'])
        persisted=self.client.get(self.url(run)).json()
        self.assertTrue(persisted['lesson_check']['correct'])
        self.assertEqual(self.client.post(f'/engine/workspaces/{self.workspace}/lessons/scenario/check',json={'run_id':run['run_id'],'choice':1}).status_code,409)

if __name__=='__main__':
    try:
        unittest.main(verbosity=2)
    finally:
        TEMP.cleanup()

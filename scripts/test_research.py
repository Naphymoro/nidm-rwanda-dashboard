"""Run with the backend dependencies installed: python scripts/test_research.py."""
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
TEMP = tempfile.TemporaryDirectory(prefix="nidm-research-test-")
os.environ["NDIM_DATA_DIR"] = TEMP.name
os.environ.pop("DATABASE_URL", None)
os.environ.pop("NDIM_REQUIRE_DATABASE", None)

from fastapi.testclient import TestClient
from app.main import app
from app.research_store import run_folder, code_version
from app.workspaces import export_workspace


class ResearchTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.payload = {"text": "The stove is too expensive but I trust the trained health worker.", "skill": "scenario"}

    def events(self, payload=None):
        response = self.client.post("/research/runs", json=payload or self.payload)
        self.assertEqual(response.status_code, 200)
        self.assertIn("no-store", response.headers["cache-control"])
        return [json.loads(line) for line in response.text.splitlines()]

    def test_scenario_is_traceable_and_conserves_compartments(self):
        before = self.client.get("/narratives").json()
        events = self.events()
        self.assertEqual(events[0]["steps"], ["encode", "diagnose", "simulate", "brief"])
        result = events[-1]["result"]
        self.assertEqual(result["source"]["text"], self.payload["text"])
        self.assertEqual(result["review_status"], "requires_review")
        self.assertIn(result["run_id"], result["brief"])
        for key in ["baseline", "intervention"]:
            self.assertEqual(len(result["scenario"][key]), 90)
            for row in result["scenario"][key]:
                self.assertAlmostEqual(sum(row[c] for c in "SMTIR"), 1.0)
                self.assertTrue(0 <= row["adoption"] <= 1)
        self.assertEqual(self.client.get("/narratives").json(), before)

    def test_zero_intervention_has_identical_trajectories(self):
        result = self.events({**self.payload, "intervention_strength": 0})[-1]["result"]
        self.assertEqual(result["scenario"]["baseline"], result["scenario"]["intervention"])

    def test_evidence_skill_does_not_simulate(self):
        with patch("app.research.run_digital_twin", side_effect=AssertionError("unexpected model call")):
            result = self.events({**self.payload, "skill": "evidence"})[-1]["result"]
        self.assertIsNone(result["scenario"])

    def test_untrusted_inputs_and_limits(self):
        for changes in [{"text": " " * 30}, {"text": "x" * 20001}, {"skill": "shell"},
                        {"horizon_days": 366}, {"intervention_strength": -1}]:
            self.assertEqual(self.client.post("/research/runs", json={**self.payload, **changes}).status_code, 422)

    def test_failure_stream_does_not_leak_internal_error(self):
        with patch("app.research.encode_rule_based", side_effect=RuntimeError("secret-path")):
            events = self.events()
        self.assertEqual(events[-1]["type"], "error")
        self.assertNotIn("secret-path", json.dumps(events))
        self.assertFalse(any(e["type"] == "result" for e in events))

    def test_entrypoints_and_capabilities(self):
        self.assertIn("Research Studio", self.client.get("/").text)
        self.assertEqual(self.client.get("/workbench").status_code, 200)
        capabilities = self.client.get("/research/capabilities").json()
        self.assertFalse(capabilities["remote_calls"])
        self.assertFalse(capabilities["mcp"])

    def test_saved_run_lifecycle_and_workspace_separation(self):
        workspace = self.client.post('/workspaces', json={"name": "Run lifecycle"}).json()["workspace_id"]
        base = f'/research/workspaces/{workspace}/runs'
        result = self.events({**self.payload, "workspace_id": workspace})[-1]['result']
        run_id = result['run_id']
        # A fresh client reads persisted results and provenance.
        fresh = TestClient(app)
        self.assertEqual(fresh.get(f'{base}/{run_id}').json(), result)
        self.assertTrue(result['code_version'].startswith('sha256:'))
        self.assertEqual(result['events'][0]['type'], 'plan')
        self.assertEqual(result['events'][-1]['status'], 'completed')
        self.assertEqual(fresh.get(base).json()['total'], 1)
        self.assertEqual(fresh.get(base + '?offset=1').json()['runs'], [])
        self.assertEqual(fresh.get(f'{base}/{run_id}/artifacts/json').json(), result)
        self.assertEqual(fresh.get(f'{base}/{run_id}/artifacts/brief').text, result['brief'])
        other = f'/research/workspaces/climatetales-rwanda/runs/{run_id}'
        for suffix in ['', '/artifacts/json']:
            self.assertEqual(fresh.get(other + suffix).status_code, 404)
        self.assertEqual(fresh.delete(other).status_code, 404)
        for mode in ['template_only', 'full_backup']:
            with zipfile.ZipFile(export_workspace(workspace, mode)) as archive:
                self.assertEqual(any(run_id in name for name in archive.namelist()), mode == 'full_backup')
        self.assertEqual(fresh.delete(f'{base}/{run_id}').status_code, 204)
        self.assertEqual(fresh.get(f'{base}/{run_id}').status_code, 404)
        self.assertEqual(fresh.get(base).json()['total'], 0)

    def test_no_implicit_saves_or_partial_runs(self):
        folder = run_folder('ndim-core')
        before = list(folder.glob('*.json'))
        self.events()
        with patch('app.research.encode_rule_based', side_effect=RuntimeError('private detail')):
            events = self.events({**self.payload, 'workspace_id': 'ndim-core'})
        self.assertEqual(events[-1]['type'], 'error')
        self.assertEqual(list(folder.glob('*.json')), before)
        with patch('app.research_store.os.replace', side_effect=OSError('private disk error')):
            events = self.events({**self.payload, 'workspace_id': 'ndim-core'})
        self.assertEqual(events[-1]['type'], 'error')
        self.assertNotIn('private disk', json.dumps(events))
        self.assertEqual(list(folder.glob('*')), before)

    def test_workspace_and_run_validation(self):
        self.assertEqual(self.client.post('/research/runs', json={**self.payload, 'workspace_id': 'missing'}).status_code, 404)
        self.assertEqual(self.client.post('/research/runs', json={**self.payload, 'workspace_id': '../ndim-core'}).status_code, 422)
        self.assertEqual(self.client.get('/research/workspaces/NDIM-core/runs').status_code, 404)
        self.assertEqual(self.client.get('/research/workspaces/ndim-core/runs/not-a-uuid').status_code, 404)

    def test_fingerprint_supports_packaged_bytecode(self):
        with patch('app.research_store.Path.is_file', return_value=False):
            first = code_version()
            self.assertEqual(first, code_version())
            self.assertEqual(len(first), 71)


if __name__ == "__main__":
    try:
        unittest.main(verbosity=2)
    finally:
        TEMP.cleanup()

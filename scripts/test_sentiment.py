"""Sentiment classifier tests. With NDIM_SENTIMENT_MODEL pointing at an exported model folder they test the classifier;
without it they test that the engine falls back to keywords and says so."""
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'backend'))
os.environ['NDIM_DATA_DIR'] = tempfile.mkdtemp(prefix='nidm-sentiment-')
for name in ('DATABASE_URL', 'NDIM_REQUIRE_DATABASE', 'NDIM_MIRROR_TOKEN'):
    os.environ.pop(name, None)
from fastapi.testclient import TestClient  # noqa: E402
from app import agent_checks, sentiment  # noqa: E402
from app.encoding import encode_rule_based  # noqa: E402
from app.main import app  # noqa: E402
from app.schemas import NarrativeMetadata, NarrativeRecord  # noqa: E402

MODEL = os.getenv('NDIM_SENTIMENT_MODEL')
SAMPLES = ROOT / 'scripts' / 'local_ai_benchmark' / 'samples.json'
NOTE = ('Households in Niboye say the improved stoves save charcoal and they trust the health worker who showed them, '
        'but the price is too high and some neighbours heard a rumour that the smoke makes food taste bad.')


def record(text, language='en'):
    return NarrativeRecord(narrative_id='r1', text=text, metadata=NarrativeMetadata(source_type='field_note', language=language))


@unittest.skipUnless(MODEL and Path(MODEL, 'model.onnx').is_file(), 'set NDIM_SENTIMENT_MODEL to an exported model folder')
class ClassifierTests(unittest.TestCase):
    def test_reads_kinyarwanda_far_better_than_keywords(self):
        rows = json.load(open(SAMPLES, encoding='utf-8'))['kin'][:90]
        right = sum(sentiment.classify(row['text'])['label'] == row['label'] for row in rows)
        self.assertGreaterEqual(right / len(rows), 0.6, right)  # keywords: 0.33 (all neutral)
        self.assertTrue(sentiment.status()['available'])

    def test_encoding_uses_the_classifier_and_says_so(self):
        encoded = encode_rule_based(record(NOTE))
        self.assertIn('sentiment: AfroXLMR AfriSenti classifier', encoded.model_notes)
        self.assertEqual(encoded.sentiment, sentiment.classify(NOTE)['score'])

    def test_journey_explanation_reports_sentiment_and_passes_the_check(self):
        client = TestClient(app)
        ws = client.post('/workspaces', json={'name': 'Sentiment'}).json()['workspace_id']
        base = f"/engine/workspaces/{ws}/journeys/{client.post(f'/engine/workspaces/{ws}/journeys', json={'question': 'How might trusted messengers change adoption?'}).json()['journey_id']}"
        added = client.post(base + '/evidence', json={'records': [{'text': NOTE, 'admin_unit': 'Kicukiro / Niboye', 'source_name': 'Field team',
                                                                    'period': '2026-Q2', 'consent': 'synthetic'}]}).json()['records']
        client.post(base + '/review', json={'decisions': [{'record_id': added[0]['record_id'], 'decision': 'accept'}], 'approval_statement': 'ok'})
        body = client.post(base + '/stages/encoding', json={}).json()
        counts = body['output']['sentiment']['counts']
        self.assertEqual(sum(counts.values()), 1)
        explanation = body['presentation']['stages']['encoding']['explanation']
        self.assertIn('Sentiment, read by a classifier trained on African-language tweets', explanation)
        self.assertIsNone(agent_checks.check(explanation, agent_checks.known_numbers(json.dumps(body['output']))))
        self.assertTrue(client.get('/health').json()['sentiment']['available'])


class FallbackTests(unittest.TestCase):
    def test_without_a_model_sentiment_stays_keyword_and_says_so(self):
        saved = os.environ.get('NDIM_SENTIMENT_MODEL')
        os.environ['NDIM_SENTIMENT_MODEL'] = tempfile.mkdtemp(prefix='no-model-')
        try:
            self.assertFalse(sentiment.status()['available'])
            self.assertIsNone(sentiment.classify(NOTE))
            self.assertIn('sentiment: English keyword heuristic', encode_rule_based(record(NOTE)).model_notes)
        finally:
            if saved is None:
                os.environ.pop('NDIM_SENTIMENT_MODEL', None)
            else:
                os.environ['NDIM_SENTIMENT_MODEL'] = saved


if __name__ == '__main__':
    unittest.main()

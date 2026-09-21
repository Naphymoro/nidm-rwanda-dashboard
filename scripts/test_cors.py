"""CORS allowlist tests: the hosted Pages origin is opt-in, exact, and https-only."""
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'backend'))
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient
from app.security import allowed_origins, cors_options

PAGES = 'https://ndim-test.pages.dev'


def preflight(origin, env):
    with patch.dict(os.environ, env, clear=False):
        app = FastAPI()
        app.add_middleware(CORSMiddleware, **cors_options())
        app.post('/engine/plans')(lambda: {})
        return TestClient(app).options('/engine/plans', headers={
            'Origin': origin, 'Access-Control-Request-Method': 'POST', 'Access-Control-Request-Headers': 'content-type'})


class CorsTests(unittest.TestCase):
    def setUp(self):
        os.environ.pop('NDIM_ALLOWED_ORIGINS', None)

    def test_default_allows_only_local_origins(self):
        self.assertEqual(allowed_origins(), [])
        self.assertEqual(preflight('http://127.0.0.1:3000', {}).headers.get('access-control-allow-origin'), 'http://127.0.0.1:3000')
        self.assertIsNone(preflight(PAGES, {}).headers.get('access-control-allow-origin'))

    def test_configured_origin_is_allowed_and_others_are_not(self):
        env = {'NDIM_ALLOWED_ORIGINS': PAGES}
        self.assertEqual(preflight(PAGES, env).headers.get('access-control-allow-origin'), PAGES)
        for other in ('https://evil.example', 'https://ndim-test.pages.dev.evil.example', 'https://sub.ndim-test.pages.dev', 'http://ndim-test.pages.dev'):
            self.assertIsNone(preflight(other, env).headers.get('access-control-allow-origin'), other)

    def test_parsing_normalises_and_deduplicates(self):
        with patch.dict(os.environ, {'NDIM_ALLOWED_ORIGINS': f' {PAGES}/ , {PAGES},https://app.example.org:8443 ,'}):
            self.assertEqual(allowed_origins(), [PAGES, 'https://app.example.org:8443'])

    def test_unsafe_entries_fail_loudly(self):
        for bad in ('*', 'https://*.pages.dev', 'http://ndim-test.pages.dev', 'https://x.example/path', 'ndim-test.pages.dev', 'https://user@x.example'):
            with patch.dict(os.environ, {'NDIM_ALLOWED_ORIGINS': bad}):
                with self.assertRaises(RuntimeError, msg=bad):
                    allowed_origins()


if __name__ == '__main__':
    unittest.main()

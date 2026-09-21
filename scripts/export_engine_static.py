"""Export the NDIM engine UI as static pages for Cloudflare Pages (cloudflare/public/engine).

The pages contain no backend. They call an NDIM engine chosen at runtime with ?api=<url>;
see NDIM_ENGINE in backend/app/engine_assets/engine.js.

    python scripts/export_engine_static.py            # write the export
    python scripts/export_engine_static.py --check    # exit 1 if the export is out of date
"""
import argparse
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'backend'))
from app.engine_ui import ASSETS, engine_html  # noqa: E402

OUT = ROOT / 'cloudflare' / 'public' / 'engine'
PAGES = {'studio': 'index.html', 'workbench': 'workbench/index.html', 'academy': 'academy/index.html'}
ASSET_FILES = ('engine.css', 'engine.js', 'engine-overrides.css')
COVERAGE_URL = 'https://github.com/Naphymoro/nidm-rwanda-dashboard/blob/main/docs/NIDM_FUNCTION_COVERAGE.md'

# Backend routes in the template -> where the same content lives on the static site.
LINKS = {
    '/': '/engine/',
    '/workbench': '/engine/workbench/',
    '/academy': '/engine/academy/',
    '/academy/reference': '/academy/',
    '/classic-workbench': '/',
    '/manual': '/manual/',
    '/function-coverage': COVERAGE_URL,
}
CONFIG_JS = (
    "window.NDIM_ENGINE={static:true,routes:{studio:'/engine/',workbench:'/engine/workbench/',academy:'/engine/academy/'}};\n"
)
SCRIPT_TAG = '<script defer src="/engine/assets/engine.js"></script>'


def rewrite_links(html):
    def replace(match):
        target = match.group(1)
        if target.startswith('/engine/assets/'):
            return match.group(0)
        if target not in LINKS:
            raise SystemExit(f'Unmapped link in engine template: {target!r}. Add it to LINKS.')
        return f'href="{LINKS[target]}"'
    return re.sub(r'href="(/[^"]*)"', replace, html)


def build():
    files = {'assets/engine-config.js': CONFIG_JS}
    for name in ASSET_FILES:
        files[f'assets/{name}'] = (ASSETS / name).read_text(encoding='utf-8')
    for page, path in PAGES.items():
        html = engine_html(page)
        if SCRIPT_TAG not in html:
            raise SystemExit('Engine template script tag changed; update SCRIPT_TAG.')
        html = html.replace(SCRIPT_TAG, '<script src="/engine/assets/engine-config.js"></script>\n' + SCRIPT_TAG)
        files[path] = rewrite_links(html)
    return files


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--check', action='store_true', help='fail if the committed export differs from the source')
    args = parser.parse_args()
    files = build()
    stale = [path for path, text in files.items()
             if not (OUT / path).exists() or (OUT / path).read_text(encoding='utf-8') != text]
    if args.check:
        if stale:
            print('Engine static export is out of date:', ', '.join(stale))
            sys.exit(1)
        print('Engine static export is up to date.')
        return
    for path, text in files.items():
        target = OUT / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding='utf-8')
    print(f'Exported {len(files)} files to {OUT.relative_to(ROOT)} ({len(stale)} changed).')


if __name__ == '__main__':
    main()

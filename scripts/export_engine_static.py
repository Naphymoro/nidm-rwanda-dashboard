"""Export the NDIM engine UI as static pages for Cloudflare Pages (cloudflare/public/engine).

The pages contain no backend. They call an NDIM engine chosen at runtime with ?api=<url>;
see NDIM_ENGINE in backend/app/engine_assets/engine.js.

It also links the landing page (cloudflare/public/index.html, a generated copy of
backend/app/workflow_ui.py) to the engine UI. The patch is idempotent, so re-running this
script restores the link if the landing page is regenerated.

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

PUBLIC = ROOT / 'cloudflare' / 'public'
PAGES = {'studio': 'engine/index.html', 'workbench': 'engine/workbench/index.html', 'academy': 'engine/academy/index.html'}
ASSET_FILES = ('engine.css', 'engine.js', 'engine-overrides.css', 'engine-theme.css', 'chat.css', 'chat.js')
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
SCRIPT_TAG = re.compile(r'<script defer src="/engine/assets/(?:engine|chat)\.js"></script>')

# Landing-page links: (marker, insert before this existing anchor, link to insert).
LANDING = 'index.html'
LANDING_LINKS = (
    ('data-engine-link="nav"', '<a class="nav-item" href="publication/"',
     '<a class="nav-item" href="engine/" target="_blank" rel="noreferrer" data-engine-link="nav">Research Studio</a>'),
    ('data-engine-link="rail"', '<a class="df-nav-row" href="publication/"',
     '<a class="df-nav-row" href="engine/" target="_blank" rel="noreferrer" data-engine-link="rail">${icon("model")} Research Studio</a>'),
)


def rewrite_links(html):
    def replace(match):
        target = match.group(1)
        if target.startswith('/engine/assets/'):
            return match.group(0)
        if target not in LINKS:
            raise SystemExit(f'Unmapped link in engine template: {target!r}. Add it to LINKS.')
        return f'href="{LINKS[target]}"'
    return re.sub(r'href="(/[^"]*)"', replace, html)


def link_landing(html):
    for marker, anchor, link in LANDING_LINKS:
        if marker in html:
            continue
        if html.count(anchor) != 1:
            raise SystemExit(f'Landing page changed: expected one {anchor!r}, found {html.count(anchor)}. Update LANDING_LINKS.')
        indent = re.search(r'([ \t]*)' + re.escape(anchor), html).group(1)
        html = html.replace(anchor, link + '\n' + indent + anchor)
    return html


def build():
    files = {'engine/assets/engine-config.js': CONFIG_JS}
    for name in ASSET_FILES:
        files[f'engine/assets/{name}'] = (ASSETS / name).read_text(encoding='utf-8')
    for page, path in PAGES.items():
        html = engine_html(page)
        tag = SCRIPT_TAG.search(html)
        if not tag:
            raise SystemExit('Engine template script tag changed; update SCRIPT_TAG.')
        html = html.replace(tag.group(0), '<script src="/engine/assets/engine-config.js"></script>\n' + tag.group(0), 1)
        files[path] = rewrite_links(html)
    files[LANDING] = link_landing((PUBLIC / LANDING).read_text(encoding='utf-8'))
    return files


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--check', action='store_true', help='fail if the committed export differs from the source')
    args = parser.parse_args()
    files = build()
    stale = [path for path, text in files.items()
             if not (PUBLIC / path).exists() or (PUBLIC / path).read_text(encoding='utf-8') != text]
    if args.check:
        if stale:
            print('Engine static export is out of date:', ', '.join(stale))
            sys.exit(1)
        print('Engine static export and landing link are up to date.')
        return
    for path, text in files.items():
        target = PUBLIC / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding='utf-8')
    print(f'Wrote {len(files)} files under {PUBLIC.relative_to(ROOT)} ({len(stale)} changed: {", ".join(stale) or "none"}).')


if __name__ == '__main__':
    main()

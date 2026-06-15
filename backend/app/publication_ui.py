from pathlib import Path


def _publication_html() -> str:
    static_page = Path(__file__).resolve().parents[2] / "cloudflare" / "public" / "publication.html"
    if static_page.exists():
        return static_page.read_text(encoding="utf-8")
    return """<!doctype html>
<html lang="en">
  <head><meta charset="utf-8" /><meta name="viewport" content="width=device-width, initial-scale=1" /><title>NDIM Scientific Publication Workspace</title></head>
  <body>
    <main style="font-family:Segoe UI,Arial,sans-serif;max-width:760px;margin:40px auto;line-height:1.6">
      <h1>NDIM Scientific Publication Workspace</h1>
      <p>The full publication workspace file was not bundled. Use the Cloudflare static page or rebuild the package with <code>cloudflare/public/publication.html</code>.</p>
      <p><a href="/">Back to tool</a> | <a href="/manual">Manual</a> | <a href="/academy">Academy</a></p>
    </main>
  </body>
</html>"""


def get_publication_html() -> str:
    return _publication_html()

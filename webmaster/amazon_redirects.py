"""
Generate static Amazon redirect pages.

These pages only render when links are approved by Chris and live-enabled.
They are written to both:
- out/
- docs/out/

This protects us whether GitHub Pages serves repo root or /docs.
"""

from __future__ import annotations

import html
import shutil
from pathlib import Path
from typing import Any

from webmaster.amazon_links_io import load_json, write_text
from webmaster.amazon_links_paths import DOCS_DIR, LINK_REGISTRY, ROOT
from webmaster.amazon_links_validate import approved_live_links


ROOT_OUT_DIR = ROOT / "out"
DOCS_OUT_DIR = DOCS_DIR / "out"


def esc(value: str) -> str:
    """Escape text for HTML."""
    return html.escape(str(value), quote=True)


def redirect_slug(link: dict[str, Any]) -> str:
    """Build stable redirect page slug."""
    asin = link.get("asin") or "amazon"
    return f"{link['slug']}-{asin}".lower()


def render_redirect(link: dict[str, Any]) -> str:
    """Render one static redirect page."""
    url = esc(link["approved_affiliate_url"])
    name = esc(link["product_name"])

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Redirecting to {name}</title>
  <meta name="robots" content="noindex, nofollow">
  <meta http-equiv="refresh" content="0; url={url}">
  <script>window.location.replace("{url}");</script>
</head>
<body>
  <p>Redirecting to Amazon for {name}.</p>
  <p><strong>Amazon Associate disclosure:</strong> As an Amazon Associate I earn from qualifying purchases.</p>
  <p><a href="{url}" rel="sponsored nofollow noopener">Continue to Amazon</a></p>
</body>
</html>
"""


def reset_dir(path: Path) -> None:
    """Delete and recreate one redirect directory."""
    if path.exists():
        shutil.rmtree(path)

    path.mkdir(parents=True, exist_ok=True)


def write_redirect_to_surface(surface: Path, link: dict[str, Any]) -> None:
    """Write redirect page to one public surface."""
    path = surface / redirect_slug(link) / "index.html"
    write_text(path, render_redirect(link))


def generate_redirects() -> int:
    """Generate redirect pages for approved live links."""
    data = load_json(LINK_REGISTRY)
    links = approved_live_links(data)

    reset_dir(ROOT_OUT_DIR)
    reset_dir(DOCS_OUT_DIR)

    for link in links:
        write_redirect_to_surface(ROOT_OUT_DIR, link)
        write_redirect_to_surface(DOCS_OUT_DIR, link)

    return len(links)

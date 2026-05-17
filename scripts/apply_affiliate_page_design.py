"""
Apply visual styling to live affiliate pages.

State:
- Adds shared stylesheet.
- Adds product visual hero when missing.
- Uses a generic placeholder image until approved product images exist.

Safety:
- Does not fetch or scrape Amazon images.
- Does not publish, commit, or push.
"""

from __future__ import annotations

import html
import json
import logging
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data/amazon_links/approved_amazon_links.json"
LOG_FILE = ROOT / "logs/apply_affiliate_page_design.log"
CSS_HREF = "../../assets/styles/affiliate-page.css"
PLACEHOLDER_SRC = "../../assets/images/product-visual-placeholder.svg"


def setup_logging() -> None:
    """Create design application log."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(filename=LOG_FILE, level=logging.INFO)


def load_json(path: Path) -> dict[str, Any]:
    """Load JSON safely."""
    return json.loads(path.read_text(encoding="utf-8"))


def live_rows() -> list[dict[str, Any]]:
    """Return live approved rows."""
    registry = load_json(REGISTRY)
    return [
        row for row in registry.get("links", [])
        if row.get("approved_by_chris") is True and row.get("live_enabled") is True
    ]


def page_path(slug: str) -> Path:
    """Return page path."""
    return ROOT / "sites" / slug / "index.html"


def product_name(row: dict[str, Any]) -> str:
    """Return display product name."""
    return str(row.get("product_name") or row.get("title") or row.get("slug"))


def ensure_stylesheet(text: str) -> tuple[str, bool]:
    """Ensure shared stylesheet is linked."""
    if CSS_HREF in text:
        return text, False

    link = f'  <link rel="stylesheet" href="{CSS_HREF}">\n'

    if "</head>" in text:
        return text.replace("</head>", link + "</head>", 1), True

    return link + text, True


def hero_html(row: dict[str, Any]) -> str:
    """Render safe visual hero."""
    name = html.escape(product_name(row), quote=True)
    slug = html.escape(str(row.get("slug", "")), quote=True)

    return f"""
<div class="ai-visual-shell" data-ai-visual-hero="true">
  <section class="ai-visual-hero">
    <div class="ai-visual-copy">
      <p class="eyebrow">Local AI workstation gear</p>
      <h1>{name}</h1>
      <p>A practical item-first page for comparing whether this product fits a cleaner local AI setup.</p>
    </div>
    <figure class="ai-visual-card">
      <img src="{PLACEHOLDER_SRC}" alt="{name} visual placeholder">
      <figcaption>Image placeholder for {slug}. Add PA API or owned product image later.</figcaption>
    </figure>
  </section>
</div>
"""


def ensure_hero(text: str, row: dict[str, Any]) -> tuple[str, bool]:
    """Ensure visual hero exists."""
    if 'data-ai-visual-hero="true"' in text:
        return text, False

    hero = hero_html(row)

    if "<body>" in text:
        return text.replace("<body>", "<body>" + hero, 1), True

    if "<body " in text:
        index = text.find(">", text.find("<body "))
        if index != -1:
            return text[: index + 1] + hero + text[index + 1 :], True

    return hero + text, True


def main() -> int:
    """Apply design to live pages."""
    setup_logging()
    changed_pages = 0

    for row in live_rows():
        slug = str(row.get("slug", ""))
        path = page_path(slug)

        if not path.is_file():
            print(f"SKIP missing page: {path}")
            continue

        text = path.read_text(encoding="utf-8")
        text, css_changed = ensure_stylesheet(text)
        text, hero_changed = ensure_hero(text, row)

        if css_changed or hero_changed:
            path.write_text(text, encoding="utf-8")
            changed_pages += 1

    print("RESULT: PASS")
    print(f"changed_pages: {changed_pages}")
    print("next_required_gate: visual_page_doctor")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

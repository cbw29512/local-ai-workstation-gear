"""
Inject approved Amazon product cards into visitor-facing pages.
"""

from __future__ import annotations

import html
from typing import Any

from webmaster.amazon_links_io import load_json
from webmaster.amazon_links_paths import LINK_REGISTRY, SITES_DIR
from webmaster.amazon_links_validate import approved_live_links


def esc(value: str) -> str:
    """Escape text for HTML."""
    return html.escape(str(value), quote=True)


def redirect_href(link: dict[str, Any]) -> str:
    """Return relative redirect URL from a site page."""
    asin = link.get("asin") or "amazon"
    slug = f"{link['slug']}-{asin}".lower()
    return f"../../out/{esc(slug)}/"


def render_card(link: dict[str, Any]) -> str:
    """Render one approved Amazon product card."""
    return f"""
    <section class="card amazon-pick">
      <h2>Approved Amazon Pick</h2>
      <h3>{esc(link["product_name"])}</h3>
      <p>Reviewed for this local AI workstation gear category.</p>
      <a
        class="button"
        href="{redirect_href(link)}"
        rel="sponsored nofollow"
        data-affiliate-click="amazon"
        data-merchant="amazon"
        data-slot="{esc(link.get("slot", ""))}"
        data-slug="{esc(link.get("slug", ""))}"
        data-asin="{esc(link.get("asin", ""))}"
        data-product-name="{esc(link.get("product_name", ""))}"
      >Check on Amazon</a>
      <p><small>As an Amazon Associate I earn from qualifying purchases.</small></p>
    </section>
"""


def strip_old_cards(text: str) -> str:
    """Remove previously injected Amazon cards."""
    start = '<section class="card amazon-pick">'
    while start in text:
        before, rest = text.split(start, 1)
        _old, after = rest.split("</section>", 1)
        text = before + after
    return text


def ensure_click_script(text: str) -> str:
    """Ensure affiliate click script is loaded once."""
    script = '<script src="../../assets/affiliate_clicks.js" defer></script>'

    if script in text:
        return text

    return text.replace("</body>", f"  {script}\n</body>")


def inject_cards() -> int:
    """Inject approved cards into matching site pages."""
    data = load_json(LINK_REGISTRY)
    links = approved_live_links(data)
    grouped: dict[str, list[str]] = {}

    for link in links:
        grouped.setdefault(link["slug"], []).append(render_card(link))

    for slug, cards in grouped.items():
        page = SITES_DIR / slug / "index.html"
        text = strip_old_cards(page.read_text(encoding="utf-8"))
        updated = text.replace("</main>", "\n".join(cards) + "\n  </main>")
        updated = ensure_click_script(updated)
        page.write_text(updated, encoding="utf-8")

    return len(links)

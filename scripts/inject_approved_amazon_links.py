"""
Inject approved Amazon product cards into local static pages.

State:
- Reads data/amazon_links/approved_amazon_links.json.
- Writes sites/<slug>/index.html only.
- Does not create affiliate links.
- Does not commit or push.
"""

from __future__ import annotations

import html
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data/amazon_links/approved_amazon_links.json"


def esc(value: str) -> str:
    """Escape text for safe HTML output."""
    return html.escape(str(value), quote=True)


def live_links() -> list[dict]:
    """Return only Chris-approved live links."""
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    return [
        link for link in data.get("links", [])
        if link.get("approved_by_chris") is True
        and link.get("live_enabled") is True
        and "PASTE_" not in link.get("approved_affiliate_url", "")
    ]


def render_card(link: dict) -> str:
    """Render one Amazon product card."""
    return f"""
    <section class="card amazon-pick">
      <h2>Approved Amazon Pick</h2>
      <h3>{esc(link["product_name"])}</h3>
      <p>This product was selected for this local AI workstation gear category after review.</p>
      <a class="button" href="{esc(link["approved_affiliate_url"])}" target="_blank" rel="sponsored nofollow noopener">{esc(link.get("button_text", "Check on Amazon"))}</a>
      <p><small>As an Amazon Associate I earn from qualifying purchases.</small></p>
    </section>
"""


def inject_page(slug: str, cards: list[str]) -> None:
    """Inject product cards before the page main closes."""
    page = ROOT / "sites" / slug / "index.html"

    if not page.is_file():
        raise FileNotFoundError(f"Missing page for slug: {slug}")

    text = page.read_text(encoding="utf-8")
    marker = "</main>"

    if marker not in text:
        raise ValueError(f"Missing </main> in {page}")

    clean = text.split('<section class="card amazon-pick">')[0]
    if marker in clean:
        before, after = clean.split(marker, 1)
        updated = before + "\n".join(cards) + "\n  " + marker + after
    else:
        updated = text.replace(marker, "\n".join(cards) + "\n  " + marker)

    page.write_text(updated, encoding="utf-8")


def main() -> int:
    """Inject all approved Amazon links."""
    try:
        links = live_links()
        grouped: dict[str, list[str]] = {}

        for link in links:
            grouped.setdefault(link["slug"], []).append(render_card(link))

        for slug, cards in grouped.items():
            inject_page(slug, cards)
    except Exception as exc:
        print("RESULT: ERROR")
        print(exc)
        return 1

    print("RESULT: PASS")
    print(f"approved_live_links_rendered: {len(links)}")
    print("next: copy sites into docs and run doctors")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

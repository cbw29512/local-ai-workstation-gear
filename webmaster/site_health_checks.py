"""
Site health checks for live affiliate pages.

Safety:
- Inspection only.
- No page edits.
- No product swaps or publishing.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from webmaster.site_health_io import load_json
from webmaster.site_health_paths import REGISTRY, ROOT


def live_rows() -> list[dict[str, Any]]:
    """Return Chris-approved live Amazon registry rows."""
    registry = load_json(REGISTRY)

    return [
        row
        for row in registry.get("links", [])
        if row.get("approved_by_chris") is True
        and row.get("live_enabled") is True
    ]


def page_path(slug: str) -> Path:
    """Return expected site page path."""
    return ROOT / "sites" / slug / "index.html"


def has_any(text: str, needles: list[str]) -> bool:
    """Return true when any marker exists."""
    lowered = text.lower()
    return any(needle.lower() in lowered for needle in needles)


def check_page(row: dict[str, Any]) -> dict[str, Any]:
    """Check one live page."""
    slug = str(row.get("slug", ""))
    asin = str(row.get("asin", ""))
    affiliate_url = str(row.get("affiliate_url") or "")
    path = page_path(slug)
    problems: list[str] = []
    notes: list[str] = []

    if not path.is_file():
        return {
            "slug": slug,
            "path": str(path),
            "status": "needs_review",
            "problems": ["missing site page"],
            "optimization_notes": notes,
        }

    html = path.read_text(encoding="utf-8", errors="replace")

    checks = {
        "amazon_disclosure": has_any(html, ["Amazon Associate", "qualifying purchases"]),
        "affiliate_url_present": affiliate_url in html,
        "asin_present": asin in html,
        "click_tracking_present": has_any(html, ["data-affiliate", "affiliate-click", "analytics"]),
        "cta_present": has_any(html, ["href=", "button", "view on amazon", "amazon"]),
        "title_present": "<title>" in html.lower(),
        "meta_description_present": 'name="description"' in html.lower(),
    }

    for name, passed in checks.items():
        if not passed:
            problems.append(f"missing_or_failed_check: {name}")

    if "PASTE_CHRIS_APPROVED" in html:
        problems.append("placeholder affiliate text still present")

    if len(html) < 1500:
        notes.append("page may be thin; consider more useful buyer context")

    if "last updated" not in html.lower():
        notes.append("consider adding visible last-updated text")

    return {
        "slug": slug,
        "path": str(path),
        "status": "pass" if not problems else "needs_review",
        "problems": problems,
        "optimization_notes": notes,
    }


def run_checks() -> list[dict[str, Any]]:
    """Run checks for all live pages."""
    return [check_page(row) for row in live_rows()]

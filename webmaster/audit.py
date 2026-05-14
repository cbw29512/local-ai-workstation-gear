"""
Public surface audit logic for the local AI webmaster.

State schema:
{
  "item_count": int,
  "site_page_count": int,
  "wrong_brand_hits": list[str],
  "missing_disclosure_pages": list[str],
  "recommendations": list[str],
  "blockers": list[str]
}
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from webmaster.paths import ROOT


WRONG_BRANDS = [
    "Home Depot Affiliate Engine",
    "homedepotaffiliate",
    "Home Depot",
]

REQUIRED_DISCLOSURE = "Affiliate disclosure"


def html_files() -> list[Path]:
    """Find public HTML files, excluding Git internals."""
    return [
        path
        for path in ROOT.rglob("*.html")
        if ".git" not in path.parts
        and "reports" not in path.parts
    ]


def count_site_pages() -> int:
    """Count item pages under sites/<slug>/index.html."""
    sites_dir = ROOT / "sites"

    if not sites_dir.is_dir():
        return 0

    return len(list(sites_dir.glob("*/index.html")))


def scan_wrong_branding() -> list[str]:
    """Find public files exposing old/internal branding."""
    hits: list[str] = []

    for path in html_files():
        text = path.read_text(encoding="utf-8", errors="ignore")

        for brand in WRONG_BRANDS:
            if brand in text:
                hits.append(f"{path.relative_to(ROOT)} :: {brand}")

    return hits


def scan_disclosures() -> list[str]:
    """Find pages missing clear affiliate disclosure wording."""
    missing: list[str] = []

    for path in html_files():
        text = path.read_text(encoding="utf-8", errors="ignore")

        if REQUIRED_DISCLOSURE not in text:
            missing.append(str(path.relative_to(ROOT)))

    return missing


def validate_items(inventory: dict[str, Any]) -> list[str]:
    """Validate source-of-truth item inventory."""
    problems: list[str] = []
    items = inventory.get("items", [])

    if not isinstance(items, list):
        return ["items must be a list"]

    if len(items) != 24:
        problems.append(f"expected 24 items, found {len(items)}")

    required = ["slot", "slug", "title", "category", "best_for", "status"]

    for item in items:
        for key in required:
            if not item.get(key):
                problems.append(f"item missing {key}: {item}")

    return problems


def build_recommendations(
    item_count: int,
    site_page_count: int,
    wrong_brand_hits: list[str],
    missing_disclosures: list[str],
) -> list[str]:
    """Create actionable local webmaster recommendations."""
    recs: list[str] = []

    if item_count < 24:
        recs.append("Fill the inventory to 24 item slots.")

    if site_page_count < 24:
        recs.append("Render all 24 item pages under sites/<slug>/index.html.")

    if wrong_brand_hits:
        recs.append("Remove old Home Depot/internal engine branding from public pages.")

    if missing_disclosures:
        recs.append("Add clear affiliate disclosure wording to every public page.")

    if not recs:
        recs.append("No structural issues found. Continue monitoring performance.")

    return recs

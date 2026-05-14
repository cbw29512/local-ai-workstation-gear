"""
Supervisor report builder.

Creates JSON and Markdown reports only.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from webmaster.audit import (
    build_recommendations,
    count_site_pages,
    scan_disclosures,
    scan_wrong_branding,
    validate_items,
)


def build_report(inventory: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
    """Build the current webmaster supervisor report."""
    items = inventory.get("items", [])
    item_count = len(items) if isinstance(items, list) else 0
    site_page_count = count_site_pages()
    wrong_brand_hits = scan_wrong_branding()
    missing_disclosures = scan_disclosures()
    inventory_problems = validate_items(inventory)

    blockers = list(inventory_problems)
    recommendations = build_recommendations(
        item_count,
        site_page_count,
        wrong_brand_hits,
        missing_disclosures,
    )

    return {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "needs_review" if blockers or wrong_brand_hits else "pass",
        "site_name": state.get("site_name"),
        "mode": state.get("mode"),
        "item_count": item_count,
        "target_item_count": 24,
        "site_page_count": site_page_count,
        "wrong_brand_hits": wrong_brand_hits,
        "missing_disclosure_pages": missing_disclosures,
        "recommendations": recommendations,
        "blockers": blockers,
        "approval_gates": state.get("approval_gates", {}),
        "next_required_gate": "public_brand_and_inventory_patch",
    }


def render_markdown(report: dict[str, Any]) -> str:
    """Render report as Markdown for quick reading."""
    recs = "\n".join(f"- {item}" for item in report["recommendations"]) or "- None"
    blockers = "\n".join(f"- {item}" for item in report["blockers"]) or "- None"

    brand_hits = "\n".join(
        f"- {item}" for item in report["wrong_brand_hits"][:50]
    ) or "- None"

    missing = "\n".join(
        f"- {item}" for item in report["missing_disclosure_pages"][:50]
    ) or "- None"

    return f"""# Local AI Webmaster Supervisor Report

Status: `{report["status"]}`

Site: `{report["site_name"]}`

Mode: `{report["mode"]}`

## Inventory

- Item count: `{report["item_count"]}`
- Target item count: `{report["target_item_count"]}`
- Rendered site pages: `{report["site_page_count"]}`

## Recommendations

{recs}

## Blockers

{blockers}

## Wrong Branding Hits

{brand_hits}

## Missing Disclosure Pages

{missing}

## Safety

Publishing, commits, pushes, affiliate link changes, product swaps, outreach, spending, and external account actions remain locked unless Chris approves them.
"""

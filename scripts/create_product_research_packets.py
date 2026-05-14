"""
Create product research packets for the 24 Local AI Workstation Gear pages.

State schema:
{
  "slot": int,
  "slug": str,
  "title": str,
  "category": str,
  "best_for": str,
  "status": "needs_research",
  "affiliate_link_changes_allowed": false,
  "product_swap_allowed": false,
  "cloud_review_required": true,
  "human_approval_required": true
}

Safety:
- No web scraping.
- No fake product links.
- No invented prices, ratings, reviews, or discounts.
- No git add, commit, push, GitHub API, or credentials.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ITEMS_JSON = ROOT / "data" / "items.json"
OUT_DIR = ROOT / "data" / "product_research"
REPORT_DIR = ROOT / "reports" / "product_research"


def load_items() -> dict[str, Any]:
    """Load the 24-slot item inventory."""
    try:
        return json.loads(ITEMS_JSON.read_text(encoding="utf-8"))
    except Exception as exc:
        raise RuntimeError(f"Failed to load items.json: {exc}") from exc


def build_packet(item: dict[str, Any]) -> dict[str, Any]:
    """Build one locked research packet."""
    return {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "slot": item["slot"],
        "slug": item["slug"],
        "title": item["title"],
        "category": item["category"],
        "best_for": item["best_for"],
        "current_status": item["status"],
        "research_status": "needs_research",
        "candidate_products": [],
        "required_evidence": [
            "current product URL",
            "product name",
            "brand/manufacturer",
            "why it fits the page",
            "key specs",
            "risk notes",
            "affiliate disclosure requirement"
        ],
        "banned_claims": [
            "do not invent prices",
            "do not invent ratings",
            "do not invent reviews",
            "do not invent discounts",
            "do not claim best overall without evidence"
        ],
        "affiliate_link_changes_allowed": False,
        "product_swap_allowed": False,
        "git_commit_allowed": False,
        "git_push_allowed": False,
        "cloud_review_required": True,
        "human_approval_required": True,
        "next_required_gate": "cloud_ai_product_review",
    }


def build_cloud_prompt(packets: list[dict[str, Any]]) -> str:
    """Build cloud AI review prompt for heavier research."""
    rows = []

    for packet in packets:
        rows.append(
            f"- Slot {packet['slot']}: {packet['title']} "
            f"({packet['category']}) — {packet['best_for']}"
        )

    return f"""# Cloud AI Product Research Request

Site: Local AI Workstation Gear

Goal:
Find real, currently available product candidates for the 24 item pages.

Rules:
- Do not invent prices, ratings, reviews, discounts, or specs.
- Prefer products suitable for beginners building local AI setups.
- Flag availability, compatibility, and risk concerns.
- Use Amazon-compatible product choices only if links can be manually reviewed later.
- Do not create affiliate links.
- Do not recommend publishing.
- Return evidence-backed candidates for Chris review.

Slots:

{chr(10).join(rows)}

Output requested:
For each slot, provide 1-3 candidate products with:
- product name
- brand
- source URL
- why it fits
- important specs
- risk notes
- confidence level
"""


def write_outputs(inventory: dict[str, Any]) -> None:
    """Write packets and cloud review prompt."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    packets = [build_packet(item) for item in inventory["items"]]

    for packet in packets:
        path = OUT_DIR / f"{packet['slot']:02d}_{packet['slug']}.json"
        path.write_text(json.dumps(packet, indent=2), encoding="utf-8")

    cloud_prompt = build_cloud_prompt(packets)
    (REPORT_DIR / "cloud_ai_product_research_prompt.md").write_text(
        cloud_prompt,
        encoding="utf-8",
    )

    summary = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "product_research_packets_created",
        "packet_count": len(packets),
        "affiliate_link_changes_allowed": False,
        "product_swap_allowed": False,
        "git_commit_allowed": False,
        "git_push_allowed": False,
        "cloud_review_prompt": str(REPORT_DIR / "cloud_ai_product_research_prompt.md"),
        "next_required_gate": "cloud_ai_product_review",
    }

    (REPORT_DIR / "product_research_summary.json").write_text(
        json.dumps(summary, indent=2),
        encoding="utf-8",
    )


def main() -> int:
    """Create all product research packets."""
    try:
        inventory = load_items()
        write_outputs(inventory)
    except Exception as exc:
        print("RESULT: ERROR")
        print(exc)
        return 1

    print("RESULT: PASS")
    print("product_research_packets: 24")
    print("cloud_prompt: reports/product_research/cloud_ai_product_research_prompt.md")
    print("next_required_gate: cloud_ai_product_review")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

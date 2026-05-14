"""
Generate active cloud vertical research handoff.

State:
- Reads cloud vertical research queue.
- Chooses the first vertical packet.
- Writes one durable handoff for large/cloud AI.

Safety:
- Handoff only.
- No affiliate links.
- No product swaps.
- No commits or pushes.
- No publishing.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "data/site_portfolio/cloud_vertical_research_queue.json"
HANDOFF_JSON = ROOT / "data/site_portfolio/cloud_vertical_handoff.json"
HANDOFF_MD = ROOT / "data/site_portfolio/cloud_vertical_handoff.md"
RESULT_DIR = ROOT / "data/site_portfolio/cloud_vertical_results"


def load_json(path: Path) -> dict:
    """Load JSON with clear failure context."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise RuntimeError(f"Failed to load {path}: {exc}") from exc


def choose_vertical(queue: dict) -> dict:
    """Choose first available vertical packet."""
    verticals = queue.get("verticals", [])

    if not verticals:
        raise RuntimeError("No verticals found in cloud vertical research queue")

    return verticals[0]


def result_path(vertical_slug: str) -> Path:
    """Return target result path for one vertical."""
    return RESULT_DIR / f"{vertical_slug}.json"


def build_handoff() -> dict:
    """Build active vertical research handoff."""
    queue = load_json(QUEUE)
    vertical = choose_vertical(queue)
    vertical_slug = vertical["vertical_slug"]

    return {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "cloud_vertical_handoff_ready",
        "vertical_slug": vertical_slug,
        "site_angle": vertical["site_angle"],
        "source_packet": vertical["packet_path"],
        "target_result_file": str(result_path(vertical_slug)),
        "required_result_count": 24,
        "required_result_status": "cloud_vertical_research_completed",
        "rules": {
            "amazon_only": True,
            "asin_required_when_available": True,
            "no_affiliate_links_created": True,
            "no_prices": True,
            "no_ratings": True,
            "no_fake_reviews": True,
            "no_fake_discounts": True,
            "human_approval_required": True
        },
        "affiliate_link_changes_allowed": False,
        "product_swap_allowed": False,
        "git_commit_allowed": False,
        "git_push_allowed": False,
        "publish_allowed": False,
        "next_required_gate": "paste_cloud_vertical_research_results"
    }


def render_markdown(handoff: dict) -> str:
    """Render handoff as Markdown."""
    return f"""# Active Cloud Vertical Research Handoff

Status: `{handoff["status"]}`

Vertical: `{handoff["vertical_slug"]}`

Site angle:
{handoff["site_angle"]}

Source packet:
`{handoff["source_packet"]}`

Target result file:
`{handoff["target_result_file"]}`

Required:
- Exactly `{handoff["required_result_count"]}` Amazon-only products.
- Status must be `{handoff["required_result_status"]}`.
- Do not create affiliate links.
- Do not invent prices, ratings, reviews, or discounts.
- Chris approval is required before site creation or publishing.

Safety locks:
- Affiliate link changes allowed: `{handoff["affiliate_link_changes_allowed"]}`
- Product swap allowed: `{handoff["product_swap_allowed"]}`
- Git commit allowed: `{handoff["git_commit_allowed"]}`
- Git push allowed: `{handoff["git_push_allowed"]}`
- Publish allowed: `{handoff["publish_allowed"]}`
"""


def main() -> int:
    """Write handoff files."""
    try:
        handoff = build_handoff()
        HANDOFF_JSON.write_text(json.dumps(handoff, indent=2), encoding="utf-8")
        HANDOFF_MD.write_text(render_markdown(handoff), encoding="utf-8")
    except Exception as exc:
        print("RESULT: ERROR")
        print(exc)
        return 1

    print("RESULT: PASS")
    print(f"vertical_slug: {handoff['vertical_slug']}")
    print(f"target_result_file: {handoff['target_result_file']}")
    print("next_required_gate: paste_cloud_vertical_research_results")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

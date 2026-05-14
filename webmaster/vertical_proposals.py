"""
Build non-tech vertical proposals for the Amazon affiliate portfolio.

This keeps the current local AI gear site focused, while allowing
the larger reusable system to branch into other Amazon-friendly niches.

Safety:
- Proposals only.
- No affiliate links.
- No product swaps.
- No commits, pushes, or publishing.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any

from webmaster.vertical_paths import LOG_FILE, POLICY, PROPOSALS_JSON, PROPOSALS_MD


def setup_logging() -> None:
    """Create vertical proposal logs."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )


def load_policy() -> dict[str, Any]:
    """Load vertical diversification policy."""
    try:
        return json.loads(POLICY.read_text(encoding="utf-8"))
    except Exception as exc:
        logging.exception("Failed to load vertical policy: %s", exc)
        raise


def locked_flags() -> dict[str, bool]:
    """Return safety locks."""
    return {
        "affiliate_link_changes_allowed": False,
        "product_swap_allowed": False,
        "git_commit_allowed": False,
        "git_push_allowed": False,
        "publish_allowed": False,
    }


def build_vertical_row(vertical: dict[str, Any]) -> dict[str, Any]:
    """Build one non-tech vertical proposal row."""
    return {
        "vertical_slug": vertical["vertical_slug"],
        "site_angle": vertical["site_angle"],
        "example_item_angles": vertical.get("example_item_angles", []),
        "recommended_site_pattern": "24 item-first Amazon pages plus one funnel/controller index",
        "cloud_research_required": True,
        "human_approval_required": True,
        "amazon_only": True,
        "status": "queued_for_cloud_vertical_research",
        "next_required_gate": "cloud_ai_vertical_product_research",
        **locked_flags(),
    }


def build_proposals() -> dict[str, Any]:
    """Build non-tech vertical proposal document."""
    policy = load_policy()
    limit = int(policy.get("max_vertical_proposals", 8))
    verticals = policy.get("non_tech_verticals", [])[:limit]
    proposals = [build_vertical_row(vertical) for vertical in verticals]

    return {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "vertical_proposals_ready",
        "current_site": policy["current_site"],
        "portfolio_goal": policy["portfolio_goal"],
        "proposal_count": len(proposals),
        "proposals": proposals,
        "blocked_categories": policy.get("blocked_categories", []),
        "next_required_gate": "cloud_ai_vertical_product_research",
        **locked_flags(),
    }


def render_markdown(payload: dict[str, Any]) -> str:
    """Render vertical proposals as Markdown."""
    rows = []

    for proposal in payload["proposals"]:
        angles = ", ".join(proposal["example_item_angles"])
        rows.append(
            f"- `{proposal['vertical_slug']}` — {proposal['site_angle']} "
            f"(angles: {angles})"
        )

    return f"""# Non-Tech Vertical Proposals

Status: `{payload["status"]}`

Current site remains: `{payload["current_site"]["site_slug"]}`

Current vertical: `{payload["current_site"]["vertical"]}`

Proposal count: `{payload["proposal_count"]}`

## Proposed Non-Tech Verticals

{chr(10).join(rows)}

## Safety Locks

- Affiliate link changes allowed: `{payload["affiliate_link_changes_allowed"]}`
- Product swap allowed: `{payload["product_swap_allowed"]}`
- Git commit allowed: `{payload["git_commit_allowed"]}`
- Git push allowed: `{payload["git_push_allowed"]}`
- Publish allowed: `{payload["publish_allowed"]}`
"""


def write_proposals() -> dict[str, Any]:
    """Build and write proposal files."""
    setup_logging()
    payload = build_proposals()
    PROPOSALS_JSON.parent.mkdir(parents=True, exist_ok=True)
    PROPOSALS_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    PROPOSALS_MD.write_text(render_markdown(payload), encoding="utf-8")
    return payload

"""
Autopilot next-action logic for the local AI webmaster.

The local AI prepares decisions.
It does not execute money actions without Chris.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from webmaster.product_pipeline import build_product_pipeline_status


def decide_next_action(status: dict[str, Any]) -> str:
    """Choose the next safe action from current pipeline state."""
    if status["item_count"] != 24:
        return "repair_item_inventory"

    if status["product_packet_count"] != 24:
        return "create_product_research_packets"

    if not status["batch_01_results_exists"]:
        return "send_batch_01_to_cloud_ai"

    if status["batch_01_ready_for_chris_review"]:
        return "chris_product_candidate_review"

    return "inspect_product_pipeline"


def build_autopilot_report() -> dict[str, Any]:
    """Build the local AI autopilot report."""
    status = build_product_pipeline_status()
    next_action = decide_next_action(status)

    return {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "autopilot_ready",
        "site": "Local AI Workstation Gear",
        "local_ai_role": "webmaster_supervisor",
        "product_pipeline": status,
        "recommended_next_action": next_action,
        "cloud_ai_needed": next_action in {
            "send_batch_01_to_cloud_ai",
            "chris_product_candidate_review",
        },
        "human_approval_required": True,
        "affiliate_link_changes_allowed": False,
        "product_swap_allowed": False,
        "git_commit_allowed": False,
        "git_push_allowed": False,
        "publish_allowed": False,
        "next_required_gate": next_action,
    }


def render_autopilot_markdown(report: dict[str, Any]) -> str:
    """Render autopilot report as Markdown."""
    pipeline = report["product_pipeline"]

    return f"""# Local AI Autopilot Next Action

Status: `{report["status"]}`

Site: `{report["site"]}`

Role: `{report["local_ai_role"]}`

## Product Pipeline

- Item count: `{pipeline["item_count"]}`
- Product research packets: `{pipeline["product_packet_count"]}`
- Batch 01 results exist: `{pipeline["batch_01_results_exists"]}`
- Batch 01 reviewed slots: `{pipeline["batch_01_reviewed_slots"]}`
- Batch 01 ready for Chris review: `{pipeline["batch_01_ready_for_chris_review"]}`

## Recommended Next Action

`{report["recommended_next_action"]}`

## Safety Locks

- Human approval required: `{report["human_approval_required"]}`
- Affiliate link changes allowed: `{report["affiliate_link_changes_allowed"]}`
- Product swap allowed: `{report["product_swap_allowed"]}`
- Git commit allowed: `{report["git_commit_allowed"]}`
- Git push allowed: `{report["git_push_allowed"]}`
- Publish allowed: `{report["publish_allowed"]}`

## Next Required Gate

`{report["next_required_gate"]}`
"""

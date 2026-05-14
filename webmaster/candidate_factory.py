"""
24/7 local AI candidate factory.

State:
- If a candidate proposal is already pending cloud/Chris review, do not overwrite it.
- If no pending proposal exists, generate the next local Amazon-only candidate proposal.

Safety:
- No affiliate links.
- No product swaps.
- No commits.
- No pushes.
- No publishing.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from webmaster.candidate_cloud_packet import render_cloud_packet
from webmaster.candidate_io import load_json, write_json, write_text
from webmaster.candidate_paths import CLOUD_PACKET_MD, PROPOSAL_JSON
from webmaster.candidate_selector import build_proposal


PENDING_GATES = {
    "cloud_ai_candidate_clarification",
    "chris_affiliate_url_for_approved_candidate",
    "enable_next_approved_link",
}


def existing_pending_proposal() -> dict[str, Any] | None:
    """Return existing proposal if it is still waiting for review."""
    if not PROPOSAL_JSON.is_file():
        return None

    proposal = load_json(PROPOSAL_JSON)
    gate = proposal.get("next_required_gate")

    if proposal.get("status") == "local_candidate_proposed" and gate in PENDING_GATES:
        return proposal

    return None


def build_factory_report() -> dict[str, Any]:
    """Build candidate factory report."""
    existing = existing_pending_proposal()

    if existing:
        return {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "status": "candidate_factory_waiting",
            "reason": "Existing candidate proposal is still awaiting cloud/Chris review.",
            "pending_slug": existing.get("slug"),
            "pending_gate": existing.get("next_required_gate"),
            "candidate_created": False,
            "affiliate_link_changes_allowed": False,
            "product_swap_allowed": False,
            "git_commit_allowed": False,
            "git_push_allowed": False,
            "publish_allowed": False,
            "next_required_gate": existing.get("next_required_gate"),
        }

    proposal = build_proposal()
    write_json(PROPOSAL_JSON, proposal)
    write_text(CLOUD_PACKET_MD, render_cloud_packet(proposal))

    return {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "candidate_factory_created",
        "proposal_status": proposal.get("status"),
        "slug": proposal.get("slug"),
        "candidate_created": True,
        "affiliate_link_changes_allowed": False,
        "product_swap_allowed": False,
        "git_commit_allowed": False,
        "git_push_allowed": False,
        "publish_allowed": False,
        "next_required_gate": proposal.get("next_required_gate"),
    }


def render_factory_markdown(report: dict[str, Any]) -> str:
    """Render candidate factory report as Markdown."""
    return f"""# Candidate Factory Report

Status: `{report["status"]}`

Candidate created: `{report["candidate_created"]}`

Slug: `{report.get("slug") or report.get("pending_slug")}`

Next required gate: `{report["next_required_gate"]}`

Reason: `{report.get("reason", "Generated next local AI product proposal.")}`

## Safety Locks

- Affiliate link changes allowed: `{report["affiliate_link_changes_allowed"]}`
- Product swap allowed: `{report["product_swap_allowed"]}`
- Git commit allowed: `{report["git_commit_allowed"]}`
- Git push allowed: `{report["git_push_allowed"]}`
- Publish allowed: `{report["publish_allowed"]}`
"""

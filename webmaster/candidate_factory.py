"""
24/7 local AI candidate factory.

State:
- Resolve current candidate gate first.
- If candidate work is already waiting on cloud/Chris/link approval, do not overwrite it.
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
from webmaster.candidate_gate_status import resolve_candidate_gate
from webmaster.candidate_io import write_json, write_text
from webmaster.candidate_paths import CLOUD_PACKET_MD, PROPOSAL_JSON
from webmaster.candidate_selector import build_proposal


def locked_flags() -> dict[str, bool]:
    """Return safety locks."""
    return {
        "affiliate_link_changes_allowed": False,
        "product_swap_allowed": False,
        "git_commit_allowed": False,
        "git_push_allowed": False,
        "publish_allowed": False,
    }


def waiting_report(gate: dict[str, Any]) -> dict[str, Any]:
    """Build waiting report when downstream review is needed."""
    return {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "candidate_factory_waiting",
        "reason": gate["reason"],
        "pending_slug": gate.get("slug"),
        "pending_gate": gate.get("current_gate"),
        "candidate_created": False,
        "next_required_gate": gate.get("current_gate"),
        **locked_flags(),
    }


def created_report(proposal: dict[str, Any]) -> dict[str, Any]:
    """Build created report after generating a proposal."""
    return {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "candidate_factory_created",
        "proposal_status": proposal.get("status"),
        "slug": proposal.get("slug"),
        "candidate_created": True,
        "next_required_gate": proposal.get("next_required_gate"),
        **locked_flags(),
    }


def build_factory_report() -> dict[str, Any]:
    """Build candidate factory report."""
    gate = resolve_candidate_gate()

    if gate["current_gate"] != "generate_local_candidate_proposal":
        return waiting_report(gate)

    proposal = build_proposal()
    write_json(PROPOSAL_JSON, proposal)
    write_text(CLOUD_PACKET_MD, render_cloud_packet(proposal))

    return created_report(proposal)


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

"""
Resolve current product-candidate gate.

State first:
- Local proposal may exist.
- Cloud clarification may exist.
- Next approved link intake may be ready.
- The resolver decides the true current gate.

Safety:
- Read-only.
- No affiliate link changes.
- No product swaps.
- No commits, pushes, or publishing.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from webmaster.amazon_links_io import load_json
from webmaster.approved_link_intake import INTAKE
from webmaster.candidate_paths import PROPOSAL_JSON, ROOT


CLARIFICATION = ROOT / "data" / "product_candidates" / "cloud_candidate_clarification.json"


def load_optional(path) -> dict[str, Any]:
    """Load optional JSON or return empty state."""
    if not path.is_file():
        return {}

    return load_json(path)


def intake_ready(intake: dict[str, Any]) -> bool:
    """Return true when Chris-approved link intake is ready to enable."""
    return (
        intake.get("approved_by_chris") is True
        and intake.get("live_enabled") is True
        and bool(intake.get("approved_affiliate_url"))
        and bool(intake.get("slug"))
    )


def locked_flags() -> dict[str, bool]:
    """Return safety locks."""
    return {
        "affiliate_link_changes_allowed": False,
        "product_swap_allowed": False,
        "git_commit_allowed": False,
        "git_push_allowed": False,
        "publish_allowed": False,
    }


def gate_from_clarification(clarification: dict[str, Any]) -> dict[str, Any] | None:
    """Resolve gate from cloud clarification if present."""
    if clarification.get("status") != "cloud_candidate_clarified":
        return None

    decision = clarification.get("final_decision")
    slug = clarification.get("slug")

    if decision == "approve":
        return {
            "slug": slug,
            "current_gate": "chris_affiliate_url_for_approved_candidate",
            "reason": "Cloud AI approved candidate; waiting for Chris-approved Amazon affiliate URL.",
        }

    return {
        "slug": slug,
        "current_gate": "cloud_ai_candidate_needs_rework",
        "reason": f"Cloud AI decision was {decision!r}; candidate needs review or replacement.",
    }


def gate_from_proposal(proposal: dict[str, Any]) -> dict[str, Any] | None:
    """Resolve gate from local proposal if present."""
    if proposal.get("status") != "local_candidate_proposed":
        return None

    return {
        "slug": proposal.get("slug"),
        "current_gate": "cloud_ai_candidate_clarification",
        "reason": "Local AI proposed candidate; waiting for large/cloud AI clarification.",
    }


def resolve_candidate_gate() -> dict[str, Any]:
    """Resolve true current candidate gate."""
    intake = load_optional(INTAKE)
    proposal = load_optional(PROPOSAL_JSON)
    clarification = load_optional(CLARIFICATION)

    if intake_ready(intake):
        gate = {
            "slug": intake.get("slug"),
            "current_gate": "enable_next_approved_link",
            "reason": "Chris-approved Amazon affiliate URL is ready for reusable intake.",
        }
    else:
        gate = gate_from_clarification(clarification)

    if gate is None:
        gate = gate_from_proposal(proposal)

    if gate is None:
        gate = {
            "slug": None,
            "current_gate": "generate_local_candidate_proposal",
            "reason": "No pending candidate proposal exists.",
        }

    return {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "candidate_gate_resolved",
        **gate,
        **locked_flags(),
    }

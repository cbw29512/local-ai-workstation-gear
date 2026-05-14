"""
Collect approved and held product candidates.

State:
- Approved means cloud AI approved the candidate.
- It does not mean Chris approved an affiliate URL.
- It does not mean the product is live.
"""

from __future__ import annotations

from typing import Any


def locked_flags() -> dict[str, bool]:
    """Return safety locks."""
    return {
        "affiliate_link_changes_allowed": False,
        "product_swap_allowed": False,
        "git_commit_allowed": False,
        "git_push_allowed": False,
        "publish_allowed": False,
    }


def approved_row(source: str, item: dict[str, Any]) -> dict[str, Any]:
    """Normalize an approved cloud clarification row."""
    return {
        "source": source,
        "slot": item.get("slot"),
        "slug": item.get("slug"),
        "title": item.get("title"),
        "product_name": item.get("best_candidate_product_name"),
        "brand": item.get("best_candidate_brand"),
        "asin": item.get("best_candidate_asin"),
        "amazon_url": item.get("best_candidate_amazon_url"),
        "page_angle": item.get("page_angle"),
        "risk_notes": item.get("risk_notes", []),
        "chris_approval_checklist": item.get("chris_approval_checklist", []),
        "approved_affiliate_url": "",
        "approved_by_chris": False,
        "live_enabled": False,
        "next_required_gate": "chris_affiliate_url_for_approved_candidate",
        **locked_flags(),
    }


def collect_primary(primary: dict[str, Any]) -> list[dict[str, Any]]:
    """Collect approved primary candidate."""
    if primary.get("status") != "cloud_candidate_clarified":
        return []

    if primary.get("final_decision") != "approve":
        return []

    return [approved_row("primary_cloud_clarification", primary)]


def collect_backlog(backlog: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Collect approved and held backlog candidates."""
    approved: list[dict[str, Any]] = []
    held: list[dict[str, Any]] = []

    for item in backlog.get("items", []):
        if item.get("final_decision") == "approve":
            approved.append(approved_row("backlog_cloud_clarification", item))
            continue

        held.append(
            {
                "slot": item.get("slot"),
                "slug": item.get("slug"),
                "title": item.get("title"),
                "product_name": item.get("best_candidate_product_name"),
                "asin": item.get("best_candidate_asin"),
                "final_decision": item.get("final_decision"),
                "next_required_gate": item.get("next_required_gate"),
                "reason": item.get("reasons", []),
            }
        )

    return approved, held


def dedupe(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Deduplicate queue rows by slug then ASIN."""
    seen: set[tuple[str, str]] = set()
    clean: list[dict[str, Any]] = []

    for row in rows:
        key = (str(row.get("slug")), str(row.get("asin")))

        if key in seen:
            continue

        seen.add(key)
        clean.append(row)

    return clean

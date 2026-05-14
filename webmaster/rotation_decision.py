"""
Classify item rotation status from lifecycle + performance.

This creates recommendations only.
It never swaps products or changes affiliate links.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from webmaster.lifecycle_paths import LIFECYCLE_JSON
from webmaster.performance_io import load_json, write_json, write_text
from webmaster.performance_paths import (
    ITEM_PERFORMANCE_JSON,
    PERFORMANCE_POLICY_JSON,
    ROTATION_REPORT_JSON,
    ROTATION_REPORT_MD,
)


def parse_time(value: str | None) -> datetime | None:
    """Parse ISO time when available."""
    return datetime.fromisoformat(value) if value else None


def metrics_by_slug() -> dict[str, dict[str, Any]]:
    """Load performance metrics keyed by slug."""
    data = load_json(ITEM_PERFORMANCE_JSON)
    return {item["slug"]: item for item in data.get("items", []) if item.get("slug")}


def classify(item: dict[str, Any], metrics: dict[str, Any], policy: dict[str, Any]) -> str:
    """Return one rotation decision."""
    now = datetime.now(timezone.utc)
    rotation_due = parse_time(item.get("rotation_due_at"))

    clicks = int(metrics.get("clicks_30d", 0))
    affiliate_clicks = int(metrics.get("affiliate_clicks_30d", 0))
    impressions = int(metrics.get("impressions_30d", 0))

    if affiliate_clicks >= int(policy["protect_if_affiliate_clicks_30d_gte"]):
        return "protected_winner"

    if clicks >= int(policy["protect_if_clicks_30d_gte"]):
        return "keep"

    if impressions >= int(policy["improve_if_impressions_30d_gte"]) and clicks == 0:
        return "improve"

    if rotation_due and rotation_due <= now:
        if impressions < int(policy["replace_if_impressions_30d_lt"]) and clicks == 0:
            return "replace_candidate"

    return "testing"


def build_report() -> dict[str, Any]:
    """Build full rotation decision report."""
    lifecycle = load_json(LIFECYCLE_JSON)
    policy = load_json(PERFORMANCE_POLICY_JSON)
    metrics = metrics_by_slug()

    decisions = []

    for item in lifecycle.get("items", []):
        slug = item["slug"]
        item_metrics = metrics.get(slug, {})
        decision = classify(item, item_metrics, policy)

        decisions.append(
            {
                "slot": item["slot"],
                "slug": slug,
                "title": item["title"],
                "rotation_due_at": item.get("rotation_due_at"),
                "clicks_30d": item_metrics.get("clicks_30d", 0),
                "affiliate_clicks_30d": item_metrics.get("affiliate_clicks_30d", 0),
                "impressions_30d": item_metrics.get("impressions_30d", 0),
                "rotation_decision": decision,
                "replacement_allowed": False,
                "product_swap_allowed": False,
                "human_approval_required": True,
            }
        )

    return {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "rotation_decisions_created",
        "decision_count": len(decisions),
        "decisions": decisions,
        "replacement_allowed": False,
        "product_swap_allowed": False,
        "affiliate_link_changes_allowed": False,
        "git_commit_allowed": False,
        "git_push_allowed": False,
        "publish_allowed": False,
        "next_required_gate": "rotation_decision_review",
    }


def render_markdown(report: dict[str, Any]) -> str:
    """Render rotation report for quick review."""
    rows = [
        f"- Slot {d['slot']} `{d['slug']}`: `{d['rotation_decision']}` "
        f"(clicks={d['clicks_30d']}, affiliate_clicks={d['affiliate_clicks_30d']}, "
        f"impressions={d['impressions_30d']}, due={d['rotation_due_at']})"
        for d in report["decisions"]
    ]

    return "# Rotation Decision Report\n\n" + "\n".join(rows) + "\n"


def write_rotation_report() -> dict[str, Any]:
    """Write rotation JSON and Markdown reports."""
    report = build_report()
    write_json(ROTATION_REPORT_JSON, report)
    write_text(ROTATION_REPORT_MD, render_markdown(report))
    return report

"""
Build and render daily money update reports.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def load_json(path: Path, fallback: dict[str, Any]) -> dict[str, Any]:
    """Load JSON report or return fallback."""
    try:
        if not path.is_file():
            return fallback
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        logging.exception("Failed to load %s: %s", path, exc)
        return fallback


def summarize_rotation(rotation_report: dict[str, Any]) -> dict[str, int]:
    """Count rotation decisions by type."""
    summary = {
        "testing": 0,
        "keep": 0,
        "improve": 0,
        "replace_candidate": 0,
        "protected_winner": 0,
    }

    for decision in rotation_report.get("decisions", []):
        key = decision.get("rotation_decision", "testing")
        summary[key] = summary.get(key, 0) + 1

    return summary


def build_report(
    results: list[dict[str, Any]],
    money_status: dict[str, Any],
    rotation_report: dict[str, Any],
) -> dict[str, Any]:
    """Build daily money update report."""
    passed = all(item["passed"] for item in results)

    return {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "daily_money_update_completed" if passed else "daily_money_update_needs_review",
        "commands": results,
        "live_amazon_links": money_status.get("live_amazon_links", 0),
        "metrics_need_update": money_status.get("metrics_need_update", True),
        "next_money_action": money_status.get("next_money_action", "inspect_money_monitor"),
        "rotation_decisions": summarize_rotation(rotation_report),
        "affiliate_link_changes_allowed": False,
        "product_swap_allowed": False,
        "git_commit_allowed": False,
        "git_push_allowed": False,
        "publish_allowed": False,
        "next_required_gate": money_status.get("next_money_action", "inspect_money_monitor"),
    }


def render_markdown(report: dict[str, Any]) -> str:
    """Render daily report as Markdown."""
    command_rows = [
        f"- `{'PASS' if result['passed'] else 'FAIL'}` {result['command']}"
        for result in report["commands"]
    ]

    rotation = report["rotation_decisions"]

    return f"""# Daily Money Update

Status: `{report["status"]}`

Created at: `{report["created_at"]}`

Live Amazon links: `{report["live_amazon_links"]}`

Metrics need update: `{report["metrics_need_update"]}`

Next money action: `{report["next_money_action"]}`

## Rotation Decisions

- Testing: `{rotation.get("testing", 0)}`
- Keep: `{rotation.get("keep", 0)}`
- Improve: `{rotation.get("improve", 0)}`
- Replace candidate: `{rotation.get("replace_candidate", 0)}`
- Protected winner: `{rotation.get("protected_winner", 0)}`

## Commands

{chr(10).join(command_rows)}

## Safety Locks

- Affiliate link changes allowed: `{report["affiliate_link_changes_allowed"]}`
- Product swap allowed: `{report["product_swap_allowed"]}`
- Git commit allowed: `{report["git_commit_allowed"]}`
- Git push allowed: `{report["git_push_allowed"]}`
- Publish allowed: `{report["publish_allowed"]}`
"""

"""
Render site webmaster health reports.

Safety:
- Report generation only.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from webmaster.site_health_io import write_json, write_text
from webmaster.site_health_paths import REPORT_JSON, REPORT_MD


def build_payload(pages: list[dict[str, Any]]) -> dict[str, Any]:
    """Build site health payload."""
    problem_count = sum(len(page["problems"]) for page in pages)
    status = "pass" if problem_count == 0 else "needs_review"

    next_action = "Monitor pages and review optimization notes."
    if problem_count:
        next_action = "Review site webmaster report and fix failed page checks."

    return {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "checked_pages": len(pages),
        "problem_count": problem_count,
        "pages": pages,
        "publish_allowed": False,
        "git_push_allowed": False,
        "product_swap_allowed": False,
        "next_action": next_action,
    }


def render_markdown(payload: dict[str, Any]) -> str:
    """Render Markdown report."""
    lines = [
        "# Site Webmaster Report",
        "",
        f"Status: `{payload['status']}`",
        f"Created at: `{payload['created_at']}`",
        f"Checked pages: `{payload['checked_pages']}`",
        f"Problem count: `{payload['problem_count']}`",
        "",
        "## Next Action",
        "",
        payload["next_action"],
        "",
        "## Page Checks",
        "",
    ]

    for page in payload["pages"]:
        lines.extend(
            [
                f"### `{page['slug']}`",
                f"- Status: `{page['status']}`",
                f"- Path: `{page['path']}`",
                f"- Problems: `{len(page['problems'])}`",
            ]
        )

        for problem in page["problems"]:
            lines.append(f"  - {problem}")

        if page["optimization_notes"]:
            lines.append("- Optimization notes:")
            for note in page["optimization_notes"]:
                lines.append(f"  - {note}")

        lines.append("")

    return "\n".join(lines)


def write_reports(payload: dict[str, Any]) -> None:
    """Write JSON and Markdown reports."""
    write_json(REPORT_JSON, payload)
    write_text(REPORT_MD, render_markdown(payload))


def print_summary(payload: dict[str, Any]) -> int:
    """Print CLI summary."""
    print(f"RESULT: {payload['status'].upper()}")
    print(f"checked_pages: {payload['checked_pages']}")
    print(f"problem_count: {payload['problem_count']}")
    print(f"report: {REPORT_MD}")
    print(f"next_action: {payload['next_action']}")
    return 0 if payload["status"] == "pass" else 1

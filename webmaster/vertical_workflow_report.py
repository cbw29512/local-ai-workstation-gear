"""
Render vertical workflow audit output.

Safety:
- Reporting only.
- No affiliate links, swaps, commits, pushes, or publishing.
"""

from __future__ import annotations

from typing import Any

from webmaster.vertical_workflow_paths import PROMPT


def next_action(staged: dict[str, Any], active: dict[str, Any]) -> str:
    """Return the next human action."""
    staged_ready = (
        staged.get("status") == "cloud_vertical_research_completed"
        and staged.get("items") == 24
    )
    active_ready = (
        active.get("status") == "cloud_vertical_research_completed"
        and active.get("items") == 24
    )

    if staged_ready:
        return "Run: python3 scripts/stage_cloud_vertical_result.py && python3 scripts/cloud_vertical_result_doctor.py"

    if active_ready:
        return "Run: python3 scripts/cloud_vertical_result_doctor.py"

    return (
        "Paste the large/cloud AI returned JSON into "
        "data/site_portfolio/cloud_vertical_results/staged-home-organization.json"
    )


def print_report(problems: list[str], staged: dict[str, Any], active: dict[str, Any]) -> int:
    """Print audit report and return exit code."""
    print("RESULT:")
    print("VERTICAL WORKFLOW AUDIT")
    print(f"prompt: {PROMPT}")
    print(f"staged_status: {staged.get('status')}")
    print(f"staged_items: {staged.get('items')}")
    print(f"active_status: {active.get('status')}")
    print(f"active_items: {active.get('items')}")
    print(f"next_action: {next_action(staged, active)}")

    if problems:
        print("STATE: NEEDS REVIEW")
        for problem in problems:
            print(f"- {problem}")
        return 1

    print("STATE: PASS")
    return 0

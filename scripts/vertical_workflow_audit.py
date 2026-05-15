"""
Audit the non-tech vertical research workflow.

State:
- The prompt file is for the large/cloud AI.
- The staged JSON file is where returned cloud JSON is pasted.
- The active result file is what the validator checks.
- The handoff decides which vertical/result file is active.

Safety:
- Read-only audit.
- No affiliate links.
- No product swaps.
- No commits or pushes.
- No publishing.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

PROMPT = ROOT / "data/site_portfolio/cloud_vertical_active_prompts/home-organization-active-prompt.md"
HANDOFF = ROOT / "data/site_portfolio/cloud_vertical_handoff.json"
STAGED = ROOT / "data/site_portfolio/cloud_vertical_results/staged-home-organization.json"
ACTIVE = ROOT / "data/site_portfolio/cloud_vertical_results/home-organization.json"


def load_json(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    """Load JSON and return either data or error text."""
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except Exception as exc:
        return None, str(exc)


def prompt_status() -> list[str]:
    """Audit the active prompt file."""
    problems: list[str] = []

    if not PROMPT.is_file():
        return [f"missing prompt: {PROMPT}"]

    text = PROMPT.read_text(encoding="utf-8")

    markers = [
        "Return ONE raw JSON object only",
        "The items array must contain exactly 24 objects",
        "vertical_slug",
        "cloud_vertical_research_completed",
    ]

    for marker in markers:
        if marker not in text:
            problems.append(f"prompt missing marker: {marker}")

    return problems


def handoff_status() -> list[str]:
    """Audit handoff and target path."""
    problems: list[str] = []

    if not HANDOFF.is_file():
        return [f"missing handoff: {HANDOFF}"]

    data, error = load_json(HANDOFF)

    if error:
        return [f"handoff invalid JSON: {error}"]

    if data.get("status") != "cloud_vertical_handoff_ready":
        problems.append(f"handoff bad status: {data.get('status')}")

    if data.get("vertical_slug") != "home-organization":
        problems.append(f"handoff vertical mismatch: {data.get('vertical_slug')}")

    target = Path(str(data.get("target_result_file", "")))

    if target != ACTIVE:
        problems.append(f"handoff target mismatch: {target}")

    return problems


def result_summary(path: Path) -> tuple[list[str], dict[str, Any]]:
    """Audit one result JSON file and return summary fields."""
    problems: list[str] = []
    summary: dict[str, Any] = {
        "path": str(path),
        "exists": path.is_file(),
        "status": None,
        "vertical_slug": None,
        "items": None,
    }

    if not path.is_file():
        problems.append(f"missing result file: {path}")
        return problems, summary

    data, error = load_json(path)

    if error:
        problems.append(f"{path.name}: invalid JSON: {error}")
        return problems, summary

    items = data.get("items", [])

    summary.update(
        {
            "status": data.get("status"),
            "vertical_slug": data.get("vertical_slug"),
            "items": len(items),
        }
    )

    if data.get("vertical_slug") != "home-organization":
        problems.append(f"{path.name}: vertical_slug must be home-organization")

    if data.get("status") == "cloud_vertical_research_completed" and len(items) != 24:
        problems.append(f"{path.name}: completed result must have 24 items")

    return problems, summary


def next_action(staged: dict[str, Any], active: dict[str, Any]) -> str:
    """Return the next human action."""
    if staged.get("status") == "cloud_vertical_research_completed" and staged.get("items") == 24:
        return "Run: python3 scripts/stage_cloud_vertical_result.py && python3 scripts/cloud_vertical_result_doctor.py"

    if active.get("status") == "cloud_vertical_research_completed" and active.get("items") == 24:
        return "Run: python3 scripts/cloud_vertical_result_doctor.py"

    return (
        "Paste the large/cloud AI returned JSON into "
        "data/site_portfolio/cloud_vertical_results/staged-home-organization.json"
    )


def main() -> int:
    """Run vertical workflow audit."""
    problems: list[str] = []
    problems.extend(prompt_status())
    problems.extend(handoff_status())

    staged_problems, staged = result_summary(STAGED)
    active_problems, active = result_summary(ACTIVE)

    problems.extend(staged_problems)
    problems.extend(active_problems)

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


if __name__ == "__main__":
    raise SystemExit(main())

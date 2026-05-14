"""
Safely import cloud vertical JSON from macOS clipboard.

State:
- Reads clipboard using pbpaste.
- Validates JSON before writing staged result.
- Refuses to overwrite staged file with empty/non-JSON text.

Safety:
- No affiliate links.
- No product swaps.
- No commits or pushes.
- No publishing.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
STAGED = ROOT / "data/site_portfolio/cloud_vertical_results/staged-home-organization.json"
EXPECTED_SLUG = "home-organization"


def read_clipboard() -> str:
    """Read macOS clipboard text."""
    result = subprocess.run(
        ["pbpaste"],
        text=True,
        capture_output=True,
        check=False,
    )

    if result.returncode != 0:
        raise RuntimeError(result.stderr or "pbpaste failed")

    return result.stdout.strip()


def parse_json(text: str) -> dict[str, Any]:
    """Parse clipboard JSON safely."""
    if not text:
        raise ValueError("clipboard is empty")

    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        preview = text[:160].replace("\n", "\\n")
        raise ValueError(f"clipboard is not valid JSON. Preview: {preview}") from exc

    if not isinstance(data, dict):
        raise ValueError("clipboard JSON must be an object")

    return data


def validate_payload(data: dict[str, Any]) -> list[str]:
    """Validate staged cloud vertical payload."""
    problems: list[str] = []

    if data.get("vertical_slug") != EXPECTED_SLUG:
        problems.append(f"vertical_slug must be {EXPECTED_SLUG!r}")

    allowed_statuses = {
        "awaiting_cloud_vertical_research",
        "cloud_vertical_research_completed",
    }

    if data.get("status") not in allowed_statuses:
        problems.append("status must be awaiting_cloud_vertical_research or cloud_vertical_research_completed")

    if data.get("status") == "cloud_vertical_research_completed":
        items = data.get("items", [])

        if len(items) != 24:
            problems.append(f"completed result must have 24 items, got {len(items)}")

    for locked in [
        "affiliate_links_created",
        "publish_recommended",
        "affiliate_link_changes_allowed",
        "product_swap_allowed",
        "git_commit_allowed",
        "git_push_allowed",
        "publish_allowed",
    ]:
        if data.get(locked) is not False:
            problems.append(f"{locked} must be false")

    return problems


def main() -> int:
    """Import valid clipboard JSON into staged file."""
    try:
        text = read_clipboard()
        data = parse_json(text)
        problems = validate_payload(data)

        if problems:
            print("RESULT: NEEDS REVIEW")
            for problem in problems:
                print(f"- {problem}")
            return 1

        STAGED.write_text(json.dumps(data, indent=2), encoding="utf-8")
    except Exception as exc:
        print("RESULT: ERROR")
        print(exc)
        print("staged file was not overwritten")
        return 1

    print("RESULT: PASS")
    print(f"wrote_staged_result: {STAGED}")
    print(f"status: {data.get('status')}")
    print(f"items: {len(data.get('items', []))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

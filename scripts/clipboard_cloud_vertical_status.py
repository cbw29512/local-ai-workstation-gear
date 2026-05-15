"""
Inspect clipboard before cloud vertical import.

State:
- Reads macOS clipboard.
- Classifies clipboard content.
- Does not write files.

Safety:
- Read-only.
- No affiliate links.
- No product swaps.
- No commits or pushes.
- No publishing.
"""

from __future__ import annotations

import json
import subprocess
from typing import Any


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


def looks_like_shell(text: str) -> bool:
    """Detect terminal commands copied to clipboard."""
    markers = [
        "cd ~/Code",
        "python3 scripts/",
        "git add",
        "git commit",
        "pbpaste",
        "echo ",
    ]

    return any(marker in text for marker in markers)


def looks_like_prompt(text: str) -> bool:
    """Detect active cloud prompt copied to clipboard."""
    markers = [
        "Active Cloud AI Request",
        "Cloud Vertical Product Research Packet",
        "Find 24 Amazon-only product candidates",
    ]

    return any(marker in text for marker in markers)


def parse_json(text: str) -> dict[str, Any] | None:
    """Return JSON object if clipboard is valid JSON."""
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return None

    if not isinstance(data, dict):
        return None

    return data


def main() -> int:
    """Print clipboard status."""
    try:
        text = read_clipboard()
    except Exception as exc:
        print("RESULT: ERROR")
        print(exc)
        return 1

    print("RESULT:")

    if not text:
        print("CLIPBOARD STATE: EMPTY")
        return 0

    data = parse_json(text)

    if data is not None:
        status = data.get("status")
        vertical_slug = data.get("vertical_slug")
        items = len(data.get("items", []))

        print("CLIPBOARD STATE: VALID_JSON")
        print(f"status: {status}")
        print(f"vertical_slug: {vertical_slug}")
        print(f"items: {items}")

        if status == "cloud_vertical_research_completed" and items == 24:
            print("next_action: run import_stage_validate_cloud_vertical_result.py")
        else:
            print("next_action: clipboard JSON is valid but not a completed 24-item result")

        return 0

    if looks_like_prompt(text):
        print("CLIPBOARD STATE: CLOUD_PROMPT")
        print("next_action: paste this into the large/cloud AI and ask for JSON only")
        return 0

    if looks_like_shell(text):
        print("CLIPBOARD STATE: TERMINAL_COMMANDS")
        print("next_action: do not import; copy the cloud AI JSON result first")
        return 0

    print("CLIPBOARD STATE: UNKNOWN_TEXT")
    print("next_action: do not import; clipboard is not valid JSON")
    print("preview:", text[:200].replace("\n", "\\n"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

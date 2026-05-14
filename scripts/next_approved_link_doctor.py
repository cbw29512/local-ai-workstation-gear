"""
Validate next approved Amazon link intake.

Read-only doctor.
"""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from webmaster.amazon_links_io import load_json
from webmaster.approved_link_intake import INTAKE, validate_intake


def main() -> int:
    """Validate intake file."""
    problems: list[str] = []

    if not INTAKE.is_file():
        problems.append(f"missing intake file: {INTAKE}")
    else:
        row = load_json(INTAKE)

        if row.get("status") == "awaiting_next_chris_approved_link":
            print("RESULT:")
            print("NEXT APPROVED LINK STATE: WAITING")
            print("Paste a Chris-approved Amazon affiliate URL to continue.")
            return 0

        problems.extend(validate_intake(row))

    print("RESULT:")

    if problems:
        print("NEXT APPROVED LINK STATE: NEEDS REVIEW")
        for problem in problems:
            print(f"- {problem}")
        return 1

    print("NEXT APPROVED LINK STATE: PASS")
    print("next_required_gate: enable_next_approved_link")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""
Validate active cloud vertical research result.

State:
- Reads active cloud vertical handoff.
- Validates the handoff target result file.

Safety:
- Read-only doctor.
- No affiliate links.
- No product swaps.
- No commits or pushes.
"""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from webmaster.vertical_result_io import load_json, setup_logging
from webmaster.vertical_result_target import active_target
from webmaster.vertical_result_validate import validate_result


def main() -> int:
    """Run cloud vertical result doctor."""
    setup_logging()

    try:
        expected_slug, result_file = active_target()
        data = load_json(result_file)
    except Exception as exc:
        print("RESULT:")
        print("CLOUD VERTICAL RESULT STATE: NEEDS REVIEW")
        print(f"- {exc}")
        return 1

    if data.get("status") == "awaiting_cloud_vertical_research":
        print("RESULT:")
        print("CLOUD VERTICAL RESULT STATE: WAITING")
        print(f"vertical_slug: {expected_slug}")
        print(f"target_result_file: {result_file}")
        print("Paste cloud research results before validation.")
        return 0

    problems = validate_result(data, expected_slug)

    print("RESULT:")

    if problems:
        print("CLOUD VERTICAL RESULT STATE: NEEDS REVIEW")
        for problem in problems:
            print(f"- {problem}")
        return 1

    print("CLOUD VERTICAL RESULT STATE: PASS")
    print(f"vertical_slug: {expected_slug}")
    print("item_count: 24")
    print("next_required_gate: chris_vertical_site_approval")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

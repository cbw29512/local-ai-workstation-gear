"""
Apply lifecycle timestamps to all 24 item slots.

Safety:
- Local file write only.
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

from webmaster.lifecycle_builder import build_lifecycle
from webmaster.lifecycle_io import setup_logging, write_json
from webmaster.lifecycle_paths import LIFECYCLE_JSON


def main() -> int:
    """Apply lifecycle timestamps."""
    setup_logging()

    try:
        payload = build_lifecycle()
        write_json(LIFECYCLE_JSON, payload)
    except Exception as exc:
        print("RESULT: ERROR")
        print(exc)
        return 1

    print("RESULT: PASS")
    print(f"item_count: {payload['item_count']}")
    print(f"lifecycle_file: {LIFECYCLE_JSON}")
    print("next_required_gate: lifecycle_timestamp_review")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

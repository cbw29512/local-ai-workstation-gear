"""
Generate candidate backlog.

Safety:
- Backlog only.
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

from webmaster.candidate_backlog_builder import write_backlog


def main() -> int:
    """Generate backlog."""
    try:
        backlog = write_backlog()
    except Exception as exc:
        print("RESULT: ERROR")
        print(exc)
        return 1

    print("RESULT: PASS")
    print(f"backlog_items: {backlog['item_count']}")
    print(f"current_gate: {backlog['current_gate']}")
    print(f"current_gate_slug: {backlog['current_gate_slug']}")
    print("next_required_gate: cloud_ai_backlog_clarification")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""
Generate approved candidate queue.

Safety:
- Queue generation only.
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

from webmaster.approved_candidate_queue import write_queue


def main() -> int:
    """Generate approved candidate queue."""
    try:
        queue = write_queue()
    except Exception as exc:
        print("RESULT: ERROR")
        print(exc)
        return 1

    print("RESULT: PASS")
    print(f"approved_count: {queue['approved_count']}")
    print(f"held_count: {queue['held_count']}")
    print("next_required_gate: chris_affiliate_url_for_approved_candidates")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

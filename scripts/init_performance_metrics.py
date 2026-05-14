"""
Initialize timestamped performance metrics.

Safety:
- Local file write only.
- No affiliate links, swaps, commits, pushes, or publishing.
"""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from webmaster.performance_builder import write_performance


def main() -> int:
    """Initialize metrics file."""
    try:
        payload = write_performance()
    except Exception as exc:
        print("RESULT: ERROR")
        print(exc)
        return 1

    print("RESULT: PASS")
    print(f"item_count: {payload['item_count']}")
    print("performance_file: data/performance/item_performance.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

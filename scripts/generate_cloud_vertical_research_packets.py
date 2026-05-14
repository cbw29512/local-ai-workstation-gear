"""
Generate cloud vertical research packets.

Safety:
- Packet generation only.
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

from webmaster.vertical_research_packets import write_research_queue


def main() -> int:
    """Generate cloud vertical research packets."""
    try:
        queue = write_research_queue()
    except Exception as exc:
        print("RESULT: ERROR")
        print(exc)
        return 1

    print("RESULT: PASS")
    print(f"vertical_count: {queue['vertical_count']}")
    print("next_required_gate: cloud_ai_vertical_product_research")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

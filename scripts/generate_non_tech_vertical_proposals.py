"""
Generate non-tech vertical proposals.

Safety:
- Portfolio proposals only.
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

from webmaster.vertical_proposals import write_proposals


def main() -> int:
    """Generate vertical proposals."""
    try:
        payload = write_proposals()
    except Exception as exc:
        print("RESULT: ERROR")
        print(exc)
        return 1

    print("RESULT: PASS")
    print(f"proposal_count: {payload['proposal_count']}")
    print("next_required_gate: cloud_ai_vertical_product_research")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

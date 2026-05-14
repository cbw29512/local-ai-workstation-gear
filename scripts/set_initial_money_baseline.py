"""
Create initial timestamped baseline metrics for live Amazon products.

Safety:
- Does not invent traffic.
- Does not change affiliate links.
- Does not swap products.
- Does not commit or push.
"""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from webmaster.money_baseline import write_baseline_snapshot


def main() -> int:
    """Create baseline snapshot for live links."""
    try:
        snapshot = write_baseline_snapshot()
    except Exception as exc:
        print("RESULT: ERROR")
        print(exc)
        return 1

    print("RESULT: PASS")
    print(f"live_snapshot_rows: {len(snapshot.get('snapshots', []))}")
    print("next_required_gate: import_manual_amazon_metrics")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

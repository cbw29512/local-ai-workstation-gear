"""
Run timestamped rotation decisions.

Safety:
- Report only.
- No swaps, links, commits, pushes, or publishing.
"""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from webmaster.rotation_decision import write_rotation_report


def main() -> int:
    """Run rotation decision report."""
    try:
        report = write_rotation_report()
    except Exception as exc:
        print("RESULT: ERROR")
        print(exc)
        return 1

    print("RESULT: PASS")
    print(f"decision_count: {report['decision_count']}")
    print("rotation_report: reports/rotation/rotation_decision_report.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

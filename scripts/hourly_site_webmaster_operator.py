"""
Hourly site webmaster operator.

State:
- Checks live affiliate pages for health and optimization issues.
- Writes local reports for Chris review.

Safety:
- No publishing.
- No git commits or pushes.
- No product swaps.
- No affiliate link changes.
"""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from webmaster.site_health_checks import run_checks
from webmaster.site_health_io import setup_logging
from webmaster.site_health_report import build_payload, print_summary, write_reports


def main() -> int:
    """Run site webmaster operator."""
    setup_logging()

    try:
        payload = build_payload(run_checks())
        write_reports(payload)
    except Exception as exc:
        print("RESULT: ERROR")
        print(exc)
        return 1

    return print_summary(payload)


if __name__ == "__main__":
    raise SystemExit(main())

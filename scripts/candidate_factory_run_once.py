"""
Run 24/7 local candidate factory once.

Safety:
- Proposal generation only.
- No affiliate links.
- No product swaps.
- No commits or pushes.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from webmaster.candidate_factory import build_factory_report, render_factory_markdown


REPORT_JSON = ROOT / "reports" / "product_candidates" / "candidate_factory_report.json"
REPORT_MD = ROOT / "reports" / "product_candidates" / "candidate_factory_report.md"


def write_reports(report: dict) -> None:
    """Write local candidate factory reports."""
    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(report, indent=2), encoding="utf-8")
    REPORT_MD.write_text(render_factory_markdown(report), encoding="utf-8")


def main() -> int:
    """Run candidate factory once."""
    try:
        report = build_factory_report()
        write_reports(report)
    except Exception as exc:
        print("CANDIDATE FACTORY RESULT: ERROR")
        print(exc)
        return 1

    print("CANDIDATE FACTORY RESULT: PASS")
    print(f"status: {report['status']}")
    print(f"candidate_created: {report['candidate_created']}")
    print(f"next_required_gate: {report['next_required_gate']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

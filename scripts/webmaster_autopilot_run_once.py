"""
Run local AI webmaster autopilot once.

Safety:
- No page edits.
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

from webmaster.autopilot import build_autopilot_report, render_autopilot_markdown


REPORT_JSON = ROOT / "reports" / "webmaster" / "autopilot_next_action.json"
REPORT_MD = ROOT / "reports" / "webmaster" / "autopilot_next_action.md"
CLOUD_HANDOFF = ROOT / "reports" / "cloud_handoff" / "next_cloud_task.md"


def write_outputs(report: dict) -> None:
    """Write autopilot reports and cloud handoff packet."""
    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    CLOUD_HANDOFF.parent.mkdir(parents=True, exist_ok=True)

    REPORT_JSON.write_text(json.dumps(report, indent=2), encoding="utf-8")
    REPORT_MD.write_text(render_autopilot_markdown(report), encoding="utf-8")

    CLOUD_HANDOFF.write_text(
        "# Next Cloud AI Task\n\n"
        f"Recommended next action: `{report['recommended_next_action']}`\n\n"
        "Use the latest product review prompt/result files in this repo.\n\n"
        "Safety: research only. No affiliate links, no publishing, no commits, no pushes.\n",
        encoding="utf-8",
    )


def main() -> int:
    """Run one autopilot cycle."""
    try:
        report = build_autopilot_report()
        write_outputs(report)
    except Exception as exc:
        print("AUTOPILOT RESULT: ERROR")
        print(exc)
        return 1

    print("AUTOPILOT RESULT: PASS")
    print(f"next_action: {report['recommended_next_action']}")
    print(f"autopilot_json: {REPORT_JSON}")
    print(f"autopilot_markdown: {REPORT_MD}")
    print(f"cloud_handoff: {CLOUD_HANDOFF}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""
Run the full daily money update workflow.

Safety:
- No affiliate link changes.
- No product swaps.
- No commits.
- No pushes.
- No publishing.
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from webmaster.daily_money_commands import COMMANDS, run_command
from webmaster.daily_money_report import build_report, load_json, render_markdown


LOG_FILE = ROOT / "logs" / "daily_money_update.log"
MONEY_STATUS = ROOT / "reports" / "money_monitor" / "money_status.json"
ROTATION_REPORT = ROOT / "reports" / "rotation" / "rotation_decision_report.json"
OUT_JSON = ROOT / "reports" / "money_monitor" / "daily_money_update.json"
OUT_MD = ROOT / "reports" / "money_monitor" / "daily_money_update.md"


def setup_logging() -> None:
    """Create daily run log file."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )


def write_reports(report: dict) -> None:
    """Write daily money reports."""
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2), encoding="utf-8")
    OUT_MD.write_text(render_markdown(report), encoding="utf-8")


def print_failures(results: list[dict]) -> None:
    """Print failing command details."""
    for result in results:
        if result["passed"]:
            continue

        print(f"- failed: {result['command']}")
        print(result["stderr"] or result["stdout"])


def main() -> int:
    """Run daily money workflow."""
    setup_logging()

    results = [run_command(ROOT, command) for command in COMMANDS]
    money = load_json(MONEY_STATUS, {})
    rotation = load_json(ROTATION_REPORT, {"decisions": []})
    report = build_report(results, money, rotation)
    write_reports(report)

    print("RESULT:")

    if report["status"] != "daily_money_update_completed":
        print("DAILY MONEY UPDATE STATE: NEEDS REVIEW")
        print_failures(results)
        return 1

    print("DAILY MONEY UPDATE STATE: PASS")
    print(f"live_amazon_links: {report['live_amazon_links']}")
    print(f"metrics_need_update: {report['metrics_need_update']}")
    print(f"next_money_action: {report['next_money_action']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

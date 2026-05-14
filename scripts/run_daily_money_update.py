"""
Run the full daily money update workflow.

State:
- Reads existing Amazon link registry.
- Reads manual Amazon metrics snapshot.
- Imports metrics into item performance.
- Runs rotation decisions.
- Runs money monitor.
- Writes a daily money report.

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
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
LOG_FILE = ROOT / "logs" / "daily_money_update.log"

MONEY_STATUS = ROOT / "reports" / "money_monitor" / "money_status.json"
ROTATION_REPORT = ROOT / "reports" / "rotation" / "rotation_decision_report.json"

OUT_JSON = ROOT / "reports" / "money_monitor" / "daily_money_update.json"
OUT_MD = ROOT / "reports" / "money_monitor" / "daily_money_update.md"


COMMANDS = [
    ["python3", "scripts/amazon_link_registry_doctor.py"],
    ["python3", "scripts/live_money_state_doctor.py"],
    ["python3", "scripts/amazon_snapshot_doctor.py"],
    ["python3", "scripts/import_manual_amazon_metrics.py"],
    ["python3", "scripts/run_rotation_decisions.py"],
    ["python3", "scripts/money_monitor_run_once.py"],
    ["python3", "scripts/money_monitor_doctor.py"],
    ["python3", "scripts/rotation_decision_doctor.py"],
]


def setup_logging() -> None:
    """Create daily run log file."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )


def run_command(command: list[str]) -> dict[str, Any]:
    """Run one command and capture its result."""
    try:
        result = subprocess.run(
            command,
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

        return {
            "command": " ".join(command),
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "passed": result.returncode == 0,
        }
    except Exception as exc:
        logging.exception("Command failed to execute: %s", command)

        return {
            "command": " ".join(command),
            "returncode": 1,
            "stdout": "",
            "stderr": str(exc),
            "passed": False,
        }


def load_json(path: Path, fallback: dict[str, Any]) -> dict[str, Any]:
    """Load JSON report or return fallback."""
    try:
        if not path.is_file():
            return fallback

        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        logging.exception("Failed to load %s: %s", path, exc)
        return fallback


def summarize_rotation(rotation_report: dict[str, Any]) -> dict[str, int]:
    """Count rotation decisions by type."""
    summary = {
        "testing": 0,
        "keep": 0,
        "improve": 0,
        "replace_candidate": 0,
        "protected_winner": 0,
    }

    for decision in rotation_report.get("decisions", []):
        key = decision.get("rotation_decision", "testing")
        summary[key] = summary.get(key, 0) + 1

    return summary


def build_report(results: list[dict[str, Any]]) -> dict[str, Any]:
    """Build daily money update report."""
    money = load_json(MONEY_STATUS, {})
    rotation = load_json(ROTATION_REPORT, {"decisions": []})
    passed = all(item["passed"] for item in results)

    return {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "daily_money_update_completed" if passed else "daily_money_update_needs_review",
        "commands": results,
        "live_amazon_links": money.get("live_amazon_links", 0),
        "metrics_need_update": money.get("metrics_need_update", True),
        "next_money_action": money.get("next_money_action", "inspect_money_monitor"),
        "rotation_decisions": summarize_rotation(rotation),
        "affiliate_link_changes_allowed": False,
        "product_swap_allowed": False,
        "git_commit_allowed": False,
        "git_push_allowed": False,
        "publish_allowed": False,
        "next_required_gate": money.get("next_money_action", "inspect_money_monitor"),
    }


def render_markdown(report: dict[str, Any]) -> str:
    """Render daily report as Markdown."""
    command_rows = []

    for result in report["commands"]:
        status = "PASS" if result["passed"] else "FAIL"
        command_rows.append(f"- `{status}` {result['command']}")

    rotation = report["rotation_decisions"]

    return f"""# Daily Money Update

Status: `{report["status"]}`

Created at: `{report["created_at"]}`

Live Amazon links: `{report["live_amazon_links"]}`

Metrics need update: `{report["metrics_need_update"]}`

Next money action: `{report["next_money_action"]}`

## Rotation Decisions

- Testing: `{rotation.get("testing", 0)}`
- Keep: `{rotation.get("keep", 0)}`
- Improve: `{rotation.get("improve", 0)}`
- Replace candidate: `{rotation.get("replace_candidate", 0)}`
- Protected winner: `{rotation.get("protected_winner", 0)}`

## Commands

{chr(10).join(command_rows)}

## Safety Locks

- Affiliate link changes allowed: `{report["affiliate_link_changes_allowed"]}`
- Product swap allowed: `{report["product_swap_allowed"]}`
- Git commit allowed: `{report["git_commit_allowed"]}`
- Git push allowed: `{report["git_push_allowed"]}`
- Publish allowed: `{report["publish_allowed"]}`
"""


def write_reports(report: dict[str, Any]) -> None:
    """Write daily money reports."""
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2), encoding="utf-8")
    OUT_MD.write_text(render_markdown(report), encoding="utf-8")


def main() -> int:
    """Run daily money workflow."""
    setup_logging()

    results = [run_command(command) for command in COMMANDS]
    report = build_report(results)
    write_reports(report)

    print("RESULT:")

    if report["status"] != "daily_money_update_completed":
        print("DAILY MONEY UPDATE STATE: NEEDS REVIEW")
        for result in results:
            if not result["passed"]:
                print(f"- failed: {result['command']}")
                print(result["stderr"] or result["stdout"])
        return 1

    print("DAILY MONEY UPDATE STATE: PASS")
    print(f"live_amazon_links: {report['live_amazon_links']}")
    print(f"metrics_need_update: {report['metrics_need_update']}")
    print(f"next_money_action: {report['next_money_action']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

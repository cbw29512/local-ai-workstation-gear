"""
Hourly money operator.

State:
- Runs local-only monetization checks.
- Uses existing safe doctors and gates.
- Writes a report for Chris.
- Does not commit, push, publish, spend, or outreach.

Safety:
- Local automation only.
- No product swaps.
- No git commits.
- No git pushes.
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
REGISTRY = ROOT / "data/amazon_links/approved_amazon_links.json"
REPORT_JSON = ROOT / "reports/money_operator/latest_money_operator.json"
REPORT_MD = ROOT / "reports/money_operator/latest_money_operator.md"
LOG_FILE = ROOT / "logs/hourly_money_operator.log"


COMMANDS = [
    ["python3", "scripts/amazon_link_registry_doctor.py"],
    ["python3", "scripts/live_generated_affiliate_links_doctor.py"],
    ["python3", "scripts/money_layer_doctor.py"],
    ["python3", "scripts/click_tracking_doctor.py"],
    ["python3", "scripts/run_daily_money_update.py"],
]


def setup_logging() -> None:
    """Create operator log file."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )


def load_json(path: Path) -> dict[str, Any]:
    """Load JSON with useful failure context."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        logging.exception("Failed to load %s: %s", path, exc)
        raise


def run_command(command: list[str]) -> tuple[int, str]:
    """Run a local command and capture output."""
    try:
        result = subprocess.run(
            command,
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
    except Exception as exc:
        logging.exception("Failed command %s: %s", command, exc)
        return 1, str(exc)

    output = "\n".join(part for part in [result.stdout, result.stderr] if part)
    return result.returncode, output.strip()


def live_link_summary() -> dict[str, Any]:
    """Summarize live Amazon links."""
    registry = load_json(REGISTRY)
    live = [row for row in registry.get("links", []) if row.get("live_enabled") is True]

    return {
        "registry_links": len(registry.get("links", [])),
        "live_enabled_links": len(live),
        "live_slugs": [row.get("slug") for row in live],
    }


def write_reports(payload: dict[str, Any]) -> None:
    """Write JSON and Markdown reports."""
    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        "# Hourly Money Operator",
        "",
        f"Status: `{payload['status']}`",
        f"Created at: `{payload['created_at']}`",
        f"Live Amazon links: `{payload['live_summary']['live_enabled_links']}`",
        "",
        "## Next Action",
        "",
        payload["next_action"],
        "",
        "## Live Slugs",
    ]

    for slug in payload["live_summary"]["live_slugs"]:
        lines.append(f"- `{slug}`")

    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    """Run hourly money operator."""
    setup_logging()
    command_results = []

    for command in COMMANDS:
        code, output = run_command(command)
        command_results.append(
            {"command": " ".join(command), "exit_code": code, "output": output}
        )

        if code != 0:
            payload = {
                "created_at": datetime.now(timezone.utc).isoformat(),
                "status": "needs_review",
                "live_summary": live_link_summary(),
                "command_results": command_results,
                "next_action": f"Fix failing command: {' '.join(command)}",
            }
            write_reports(payload)
            print("RESULT: NEEDS REVIEW")
            print(payload["next_action"])
            return code

    summary = live_link_summary()
    next_action = "Monitor live products and update Amazon metrics snapshot."

    if summary["live_enabled_links"] < 4:
        next_action = "Run money live gate; fewer than 4 live Amazon links are enabled."

    payload = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "pass",
        "live_summary": summary,
        "command_results": command_results,
        "next_action": next_action,
    }

    write_reports(payload)

    print("RESULT: PASS")
    print(f"live_enabled_links: {summary['live_enabled_links']}")
    print(f"report: {REPORT_MD}")
    print(f"next_action: {next_action}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""
Run local AI money monitor once.

Safety:
- Read-only.
- No affiliate link changes.
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

from webmaster.money_status import build_money_status, setup_logging


REPORT_JSON = ROOT / "reports" / "money_monitor" / "money_status.json"
REPORT_MD = ROOT / "reports" / "money_monitor" / "money_status.md"


def render_markdown(report: dict) -> str:
    """Render money monitor report."""
    rows = []

    for item in report["live_items"]:
        rows.append(
            f"- Slot {item['slot']} `{item['slug']}`: "
            f"`{item['product_name']}` "
            f"(clicks={item['clicks_30d']}, "
            f"affiliate_clicks={item['affiliate_clicks_30d']}, "
            f"impressions={item['impressions_30d']}, "
            f"snapshot={item['snapshot_status']})"
        )

    if not rows:
        rows.append("- No live Amazon products yet.")

    return f"""# Money Monitor Report

Status: `{report["status"]}`

Live Amazon links: `{report["live_amazon_links"]}`

Metrics need update: `{report["metrics_need_update"]}`

Next money action: `{report["next_money_action"]}`

## Live Items

{chr(10).join(rows)}

## Safety Locks

- Affiliate link changes allowed: `{report["affiliate_link_changes_allowed"]}`
- Product swap allowed: `{report["product_swap_allowed"]}`
- Git commit allowed: `{report["git_commit_allowed"]}`
- Git push allowed: `{report["git_push_allowed"]}`
- Publish allowed: `{report["publish_allowed"]}`
"""


def write_outputs(report: dict) -> None:
    """Write money monitor reports."""
    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(report, indent=2), encoding="utf-8")
    REPORT_MD.write_text(render_markdown(report), encoding="utf-8")


def main() -> int:
    """Run money monitor once."""
    setup_logging()

    try:
        report = build_money_status()
        write_outputs(report)
    except Exception as exc:
        print("MONEY MONITOR RESULT: ERROR")
        print(exc)
        return 1

    print("MONEY MONITOR RESULT: PASS")
    print(f"live_amazon_links: {report['live_amazon_links']}")
    print(f"metrics_need_update: {report['metrics_need_update']}")
    print(f"next_money_action: {report['next_money_action']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

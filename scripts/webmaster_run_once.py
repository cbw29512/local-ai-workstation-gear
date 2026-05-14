"""
Run the local AI webmaster supervisor once.

This is safe for hourly automation.
No commits, pushes, affiliate changes, external actions, or spending.
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from webmaster.io import load_json, setup_logging, write_json, write_text
from webmaster.monthly import build_monthly_packet
from webmaster.paths import ITEMS_JSON, LATEST_JSON, LATEST_MD, REPORT_DIR, STATE_JSON
from webmaster.report import build_report, render_markdown


def monthly_packet_path() -> Path:
    """Return this month's swap proposal path."""
    month = datetime.now(timezone.utc).strftime("%Y-%m")
    return REPORT_DIR / f"monthly_swap_proposal_{month}.json"


def main() -> int:
    """Run one supervisor cycle."""
    setup_logging()

    try:
        inventory = load_json(ITEMS_JSON)
        state = load_json(STATE_JSON)
        report = build_report(inventory, state)

        write_json(LATEST_JSON, report)
        write_text(LATEST_MD, render_markdown(report))

        packet_path = monthly_packet_path()
        if not packet_path.exists():
            write_json(packet_path, build_monthly_packet(inventory))
    except Exception as exc:
        print("RESULT: ERROR")
        print(exc)
        return 1

    print("RESULT:", report["status"].upper())
    print(f"latest_json: {LATEST_JSON}")
    print(f"latest_markdown: {LATEST_MD}")
    print(f"item_count: {report['item_count']}")
    print(f"site_page_count: {report['site_page_count']}")
    print(f"wrong_brand_hits: {len(report['wrong_brand_hits'])}")
    print(f"missing_disclosure_pages: {len(report['missing_disclosure_pages'])}")
    print("next_required_gate:", report["next_required_gate"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

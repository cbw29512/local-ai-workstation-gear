"""
Hourly site webmaster operator.

State:
- Checks live affiliate pages for basic page health.
- Checks disclosure, Amazon buttons, click tracking, and redirect references.
- Writes local report for Chris review.

Safety:
- No publishing.
- No git commits or pushes.
- No product swaps.
- No affiliate link changes.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data/amazon_links/approved_amazon_links.json"
REPORT_JSON = ROOT / "reports/site_webmaster/latest_site_webmaster_report.json"
REPORT_MD = ROOT / "reports/site_webmaster/latest_site_webmaster_report.md"
LOG_FILE = ROOT / "logs/hourly_site_webmaster_operator.log"


def setup_logging() -> None:
    """Create webmaster operator log."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )


def load_json(path: Path) -> dict[str, Any]:
    """Load JSON with clear failure context."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        logging.exception("Failed to load %s: %s", path, exc)
        raise


def live_rows() -> list[dict[str, Any]]:
    """Return live approved registry rows."""
    registry = load_json(REGISTRY)

    return [
        row
        for row in registry.get("links", [])
        if row.get("approved_by_chris") is True
        and row.get("live_enabled") is True
    ]


def page_path(slug: str) -> Path:
    """Return local page path for slug."""
    return ROOT / "sites" / slug / "index.html"


def check_page(row: dict[str, Any]) -> dict[str, Any]:
    """Check one live affiliate page."""
    slug = str(row.get("slug", ""))
    asin = str(row.get("asin", ""))
    affiliate_url = str(row.get("affiliate_url") or "")
    path = page_path(slug)

    problems: list[str] = []
    optimization_notes: list[str] = []

    if not path.is_file():
        problems.append("missing site page")
        return {
            "slug": slug,
            "path": str(path),
            "status": "needs_review",
            "problems": problems,
            "optimization_notes": optimization_notes,
        }

    html = path.read_text(encoding="utf-8", errors="replace")

    checks = {
        "amazon_disclosure": "Amazon Associate" in html or "As an Amazon Associate" in html,
        "affiliate_url_present": affiliate_url in html,
        "asin_present": asin in html,
        "click_tracking_present": "data-affiliate" in html or "affiliate" in html.lower(),
        "button_or_cta_present": "<button" in html.lower() or "href=" in html.lower(),
        "title_present": "<title>" in html.lower(),
        "meta_description_present": "name=\"description\"" in html.lower(),
    }

    for name, passed in checks.items():
        if not passed:
            problems.append(f"missing_or_failed_check: {name}")

    if "PASTE_CHRIS_APPROVED" in html:
        problems.append("placeholder affiliate text still present")

    if len(html) < 1500:
        optimization_notes.append("page may be thin; consider adding more useful buyer context")

    if "last updated" not in html.lower():
        optimization_notes.append("consider adding visible last-updated text")

    status = "pass" if not problems else "needs_review"

    return {
        "slug": slug,
        "path": str(path),
        "status": status,
        "problems": problems,
        "optimization_notes": optimization_notes,
    }


def write_reports(payload: dict[str, Any]) -> None:
    """Write JSON and Markdown reports."""
    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        "# Site Webmaster Report",
        "",
        f"Status: `{payload['status']}`",
        f"Created at: `{payload['created_at']}`",
        f"Checked pages: `{payload['checked_pages']}`",
        "",
        "## Next Action",
        "",
        payload["next_action"],
        "",
        "## Page Checks",
        "",
    ]

    for page in payload["pages"]:
        lines.extend(
            [
                f"### `{page['slug']}`",
                f"- Status: `{page['status']}`",
                f"- Path: `{page['path']}`",
                f"- Problems: `{len(page['problems'])}`",
            ]
        )

        for problem in page["problems"]:
            lines.append(f"  - {problem}")

        if page["optimization_notes"]:
            lines.append("- Optimization notes:")
            for note in page["optimization_notes"]:
                lines.append(f"  - {note}")

        lines.append("")

    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    """Run site webmaster operator."""
    setup_logging()

    try:
        pages = [check_page(row) for row in live_rows()]
    except Exception as exc:
        print("RESULT: ERROR")
        print(exc)
        return 1

    problem_count = sum(len(page["problems"]) for page in pages)
    status = "pass" if problem_count == 0 else "needs_review"
    next_action = "Monitor pages and review optimization notes."

    if problem_count:
        next_action = "Review site webmaster report and fix failed page checks."

    payload = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "checked_pages": len(pages),
        "problem_count": problem_count,
        "pages": pages,
        "publish_allowed": False,
        "git_push_allowed": False,
        "product_swap_allowed": False,
        "next_action": next_action,
    }

    write_reports(payload)

    print(f"RESULT: {status.upper()}")
    print(f"checked_pages: {len(pages)}")
    print(f"problem_count: {problem_count}")
    print(f"report: {REPORT_MD}")
    print(f"next_action: {next_action}")

    return 0 if status == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

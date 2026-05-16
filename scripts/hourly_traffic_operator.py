"""
Hourly traffic operator for live Amazon affiliate pages.

State:
- Reads approved live Amazon links.
- Generates reviewable traffic copy for each live page.
- Writes local reports for Chris.

Safety:
- Does not post.
- Does not publish.
- Does not spend.
- Does not outreach.
- Does not commit or push.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data/amazon_links/approved_amazon_links.json"
REPORT_JSON = ROOT / "reports/traffic_operator/latest_traffic_operator.json"
REPORT_MD = ROOT / "reports/traffic_operator/latest_traffic_operator.md"
LOG_FILE = ROOT / "logs/hourly_traffic_operator.log"


def setup_logging() -> None:
    """Create traffic operator log."""
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


def live_links(registry: dict[str, Any]) -> list[dict[str, Any]]:
    """Return Chris-approved live Amazon rows."""
    return [
        row
        for row in registry.get("links", [])
        if row.get("approved_by_chris") is True
        and row.get("live_enabled") is True
        and row.get("affiliate_url")
    ]


def display_name(row: dict[str, Any]) -> str:
    """Return the best product display name."""
    return str(
        row.get("product_name")
        or row.get("title")
        or row.get("slug")
        or "Amazon product"
    )


def build_assets(row: dict[str, Any]) -> dict[str, Any]:
    """Build traffic copy for one live product page."""
    name = display_name(row)
    slug = row.get("slug", "")
    page_path = f"sites/{slug}/index.html"

    return {
        "slot": row.get("slot"),
        "slug": slug,
        "product_name": name,
        "page_path": page_path,
        "youtube_shorts_hooks": [
            f"Your local AI setup gets messy fast. This is one simple upgrade I would check first: {name}.",
            f"Before you buy random AI workstation gear, here is one item that actually solves a specific setup problem.",
            f"If your AI setup feels cluttered, slow, or storage-starved, this product category is worth checking."
        ],
        "pinterest_titles": [
            f"{name} for a cleaner local AI setup",
            f"Simple AI workstation gear idea: {name}",
            f"Local AI desk setup upgrade to consider"
        ],
        "social_captions": [
            f"Small setup upgrades can make local AI work feel less chaotic. I added a quick page for {name}.",
            f"Building a local AI workstation? This is one of the gear categories I would compare before buying.",
            f"Not a magic fix, but a practical setup item worth reviewing if your AI workspace needs cleanup."
        ],
        "reddit_safe_angles": [
            f"What is one underrated hardware/accessory upgrade that made your local AI setup easier to use?",
            f"For people running local models, what storage or workstation gear ended up mattering more than expected?",
            f"How do you keep your local AI desk/workstation setup organized without overbuying gear?"
        ],
        "safety_notes": [
            "No income claims.",
            "No price, rating, or review claims unless manually verified.",
            "Use as reviewable draft copy only.",
            "Do not spam communities; adapt to each platform."
        ]
    }


def write_reports(payload: dict[str, Any]) -> None:
    """Write JSON and Markdown reports."""
    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        "# Hourly Traffic Operator",
        "",
        f"Status: `{payload['status']}`",
        f"Created at: `{payload['created_at']}`",
        f"Live pages: `{payload['live_page_count']}`",
        "",
        "## Next Action",
        "",
        payload["next_action"],
        ""
    ]

    for item in payload["items"]:
        lines.extend(
            [
                f"## {item['product_name']}",
                "",
                f"Slug: `{item['slug']}`",
                f"Page: `{item['page_path']}`",
                "",
                "### YouTube Shorts Hooks",
                *[f"- {hook}" for hook in item["youtube_shorts_hooks"]],
                "",
                "### Pinterest Titles",
                *[f"- {title}" for title in item["pinterest_titles"]],
                "",
                "### Social Captions",
                *[f"- {caption}" for caption in item["social_captions"]],
                "",
                "### Reddit-Safe Angles",
                *[f"- {angle}" for angle in item["reddit_safe_angles"]],
                "",
            ]
        )

    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    """Run hourly traffic operator."""
    setup_logging()

    try:
        registry = load_json(REGISTRY)
        links = live_links(registry)
        items = [build_assets(row) for row in links]
    except Exception as exc:
        print("RESULT: ERROR")
        print(exc)
        return 1

    next_action = "Review traffic packet and manually approve any posts before publishing."

    payload = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "pass",
        "live_page_count": len(items),
        "items": items,
        "publish_allowed": False,
        "outreach_allowed": False,
        "spending_allowed": False,
        "next_action": next_action,
    }

    write_reports(payload)

    print("RESULT: PASS")
    print(f"traffic_items: {len(items)}")
    print(f"report: {REPORT_MD}")
    print(f"next_action: {next_action}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""
Generate Amazon affiliate URLs from approved candidate queue.

State:
- Reads Chris-approved universal Amazon tag.
- Reads approved candidate queue.
- Generates product-specific affiliate URLs from approved ASINs.

Safety:
- Writes staged generated links only.
- No product swaps.
- No commits or pushes.
- No publishing.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
TAG_FILE = ROOT / "data/amazon_links/approved_universal_tag.json"
QUEUE = ROOT / "data/product_candidates/approved_candidate_queue.json"
OUT_JSON = ROOT / "data/amazon_links/generated_affiliate_links_from_queue.json"
OUT_MD = ROOT / "data/amazon_links/generated_affiliate_links_from_queue.md"
LOG_FILE = ROOT / "logs/generate_affiliate_links_from_approved_queue.log"


def setup_logging() -> None:
    """Create generator log."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )


def load_json(path: Path) -> dict[str, Any]:
    """Load JSON with useful error context."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        logging.exception("Failed to load %s: %s", path, exc)
        raise


def affiliate_url(asin: str, tag: str) -> str:
    """Build product-specific Amazon affiliate URL."""
    return f"https://www.amazon.com/dp/{asin}/ref=nosim?tag={tag}"


def build_link(item: dict[str, Any], tag: str) -> dict[str, Any]:
    """Build one staged affiliate link row."""
    asin = str(item.get("asin", "")).strip()

    return {
        "slot": item.get("slot"),
        "slug": item.get("slug"),
        "title": item.get("title"),
        "product_name": item.get("product_name"),
        "brand": item.get("brand"),
        "asin": asin,
        "source_amazon_url": item.get("amazon_url"),
        "affiliate_url": affiliate_url(asin, tag),
        "approved_by_chris": True,
        "generated_from_universal_tag": True,
        "ready_for_registry_intake": True,
        "live_enabled": False,
        "affiliate_link_changes_allowed": True,
        "product_swap_allowed": False,
        "git_commit_allowed": False,
        "git_push_allowed": False,
        "publish_allowed": False,
        "next_required_gate": "registry_intake_then_page_injection"
    }


def render_markdown(payload: dict[str, Any]) -> str:
    """Render generated links summary."""
    rows = [
        f"- Slot {item['slot']} `{item['slug']}` — {item['product_name']} — `{item['affiliate_url']}`"
        for item in payload["links"]
    ]

    return f"""# Generated Amazon Affiliate Links

Status: `{payload["status"]}`

Amazon tag: `{payload["amazon_tag"]}`

Generated links: `{payload["link_count"]}`

## Links

{chr(10).join(rows) if rows else "- None"}

## Safety

- Live enabled: `False`
- Product swaps allowed: `False`
- Git push allowed: `False`
- Publish allowed: `False`
"""


def main() -> int:
    """Generate staged affiliate links."""
    setup_logging()

    try:
        tag_data = load_json(TAG_FILE)
        queue = load_json(QUEUE)
        tag = str(tag_data["amazon_tag"])

        links = [
            build_link(item, tag)
            for item in queue.get("approved_items", [])
            if item.get("asin")
        ]

        payload = {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "status": "generated_affiliate_links_ready",
            "source": "approved_candidate_queue",
            "amazon_tag": tag,
            "link_count": len(links),
            "links": links,
            "affiliate_link_generation_allowed": True,
            "product_swap_allowed": False,
            "git_commit_allowed": False,
            "git_push_allowed": False,
            "publish_allowed": False,
            "next_required_gate": "registry_intake_then_page_injection"
        }

        OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        OUT_MD.write_text(render_markdown(payload), encoding="utf-8")
    except Exception as exc:
        print("RESULT: ERROR")
        print(exc)
        return 1

    print("RESULT: PASS")
    print(f"generated_links: {len(links)}")
    print(f"output: {OUT_JSON}")
    print("next_required_gate: registry_intake_then_page_injection")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

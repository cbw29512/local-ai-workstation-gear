"""
Sync Amazon affiliate URL aliases in registry.

State:
- New generated links use affiliate_url.
- Older renderers may expect approved_affiliate_url.
- Placeholder approved_affiliate_url values are treated as missing.

Safety:
- Registry field sync only.
- No product swaps.
- No commits or pushes.
- No publishing.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data/amazon_links/approved_amazon_links.json"
LOG_FILE = ROOT / "logs/sync_amazon_affiliate_url_aliases.log"
PLACEHOLDER = "PASTE_CHRIS_APPROVED_AMAZON_AFFILIATE_URL_HERE"


def setup_logging() -> None:
    """Create sync log."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )


def load_json(path: Path) -> dict[str, Any]:
    """Load JSON safely."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        logging.exception("Failed to load %s: %s", path, exc)
        raise


def write_json(path: Path, payload: dict[str, Any]) -> None:
    """Write JSON safely."""
    try:
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    except Exception as exc:
        logging.exception("Failed to write %s: %s", path, exc)
        raise


def is_missing_or_placeholder(value: Any) -> bool:
    """Return true when an affiliate URL alias needs replacement."""
    text = str(value or "").strip()
    return not text or text == PLACEHOLDER


def main() -> int:
    """Sync affiliate_url and approved_affiliate_url fields."""
    setup_logging()

    try:
        data = load_json(REGISTRY)
        changed = 0

        for row in data.get("links", []):
            affiliate_url = row.get("affiliate_url")
            approved_url = row.get("approved_affiliate_url")

            if affiliate_url and is_missing_or_placeholder(approved_url):
                row["approved_affiliate_url"] = affiliate_url
                changed += 1

            elif approved_url and not affiliate_url and approved_url != PLACEHOLDER:
                row["affiliate_url"] = approved_url
                changed += 1

        write_json(REGISTRY, data)
    except Exception as exc:
        print("RESULT: ERROR")
        print(exc)
        return 1

    print("RESULT: PASS")
    print(f"aliases_synced: {changed}")
    print("next_required_gate: render_all_live_amazon_links")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""
Enable generated Amazon affiliate links for live page injection.

State:
- Reads approved Amazon link registry.
- Enables only rows generated from the approved universal Amazon tag.
- Requires approved_by_chris true and a valid affiliate URL.

Safety:
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
REGISTRY = ROOT / "data/amazon_links/approved_amazon_links.json"
LOG_FILE = ROOT / "logs/enable_generated_affiliate_links_for_live.log"
APPROVED_TAG = "maxyourheal06-20"


def setup_logging() -> None:
    """Create enablement log."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )


def load_json(path: Path) -> dict[str, Any]:
    """Load JSON safely with useful error context."""
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


def can_enable(row: dict[str, Any]) -> tuple[bool, str]:
    """Return whether a registry row can be enabled."""
    slug = row.get("slug", "unknown")
    asin = str(row.get("asin") or "")
    url = str(row.get("affiliate_url") or "")

    if row.get("generated_from_universal_tag") is not True:
        return False, f"{slug}: not generated from universal tag"

    if row.get("approved_by_chris") is not True:
        return False, f"{slug}: not approved_by_chris"

    if not asin:
        return False, f"{slug}: missing ASIN"

    if not url:
        return False, f"{slug}: missing affiliate_url"

    if f"/dp/{asin}" not in url:
        return False, f"{slug}: affiliate_url missing ASIN path"

    if f"tag={APPROVED_TAG}" not in url:
        return False, f"{slug}: affiliate_url missing approved tag"

    return True, f"{slug}: enable"


def main() -> int:
    """Enable generated affiliate links for live injection."""
    setup_logging()

    try:
        registry = load_json(REGISTRY)
        enabled = 0
        skipped: list[str] = []
        now = datetime.now(timezone.utc).isoformat()

        for row in registry.get("links", []):
            ok, reason = can_enable(row)

            if not ok:
                skipped.append(reason)
                continue

            if row.get("live_enabled") is not True:
                row["live_enabled"] = True
                row["live_enabled_at"] = now
                row["ready_for_page_injection"] = True
                enabled += 1

        registry["updated_at"] = now
        registry["next_required_gate"] = "inject_links_into_pages"
        registry["publish_allowed"] = False
        write_json(REGISTRY, registry)
    except Exception as exc:
        print("RESULT: ERROR")
        print(exc)
        return 1

    print("RESULT: PASS")
    print(f"enabled_generated_links: {enabled}")
    print(f"skipped_count: {len(skipped)}")
    print("next_required_gate: inject_links_into_pages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

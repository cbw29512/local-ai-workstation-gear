"""
Intake generated Amazon affiliate URLs into the approved link registry.

State:
- Reads generated affiliate links from approved queue.
- Upserts them into the existing Amazon link registry.
- Keeps live publishing disabled.

Safety:
- No product swaps.
- No commits or pushes.
- No publishing.
"""

from __future__ import annotations

import json
import logging
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "data/amazon_links/generated_affiliate_links_from_queue.json"
REGISTRY = ROOT / "data/amazon_links/approved_amazon_links.json"
BACKUP = ROOT / "data/amazon_links/approved_amazon_links.backup.json"
LOG_FILE = ROOT / "logs/intake_generated_affiliate_links.log"


def setup_logging() -> None:
    """Create intake log."""
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


def write_json(path: Path, payload: dict[str, Any]) -> None:
    """Write JSON with deterministic formatting."""
    try:
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    except Exception as exc:
        logging.exception("Failed to write %s: %s", path, exc)
        raise


def key_for(row: dict[str, Any]) -> tuple[str, str]:
    """Return slug/ASIN key."""
    return str(row.get("slug", "")), str(row.get("asin", ""))


def build_existing_index(links: list[dict[str, Any]]) -> dict[tuple[str, str], int]:
    """Build lookup index for existing registry links."""
    index: dict[tuple[str, str], int] = {}

    for position, row in enumerate(links):
        index[key_for(row)] = position

    return index


def registry_row(source: dict[str, Any]) -> dict[str, Any]:
    """Build registry row from generated link."""
    return {
        "slot": source.get("slot"),
        "slug": source.get("slug"),
        "title": source.get("title"),
        "product_name": source.get("product_name"),
        "brand": source.get("brand"),
        "asin": source.get("asin"),
        "source_amazon_url": source.get("source_amazon_url"),
        "affiliate_url": source.get("affiliate_url"),
        "approved_by_chris": True,
        "generated_from_universal_tag": True,
        "ready_for_page_injection": True,
        "live_enabled": False,
        "product_swap_allowed": False,
        "git_commit_allowed": False,
        "git_push_allowed": False,
        "publish_allowed": False,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }


def upsert_links(registry: dict[str, Any], generated: dict[str, Any]) -> int:
    """Upsert generated links into registry."""
    links = registry.setdefault("links", [])

    if not isinstance(links, list):
        raise TypeError("registry links field must be a list")

    index = build_existing_index(links)
    changed = 0

    for source in generated.get("links", []):
        row = registry_row(source)
        key = key_for(row)

        if key in index:
            links[index[key]].update(row)
        else:
            links.append(row)

        changed += 1

    registry["updated_at"] = datetime.now(timezone.utc).isoformat()
    registry["next_required_gate"] = "inject_links_into_pages"
    registry["publish_allowed"] = False
    return changed


def main() -> int:
    """Run generated link intake."""
    setup_logging()

    try:
        generated = load_json(GENERATED)
        registry = load_json(REGISTRY)

        if generated.get("status") != "generated_affiliate_links_ready":
            raise ValueError("generated links file is not ready")

        shutil.copyfile(REGISTRY, BACKUP)
        changed = upsert_links(registry, generated)
        write_json(REGISTRY, registry)
    except Exception as exc:
        print("RESULT: ERROR")
        print(exc)
        return 1

    print("RESULT: PASS")
    print(f"registry_updated_links: {changed}")
    print(f"backup: {BACKUP}")
    print("next_required_gate: inject_links_into_pages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

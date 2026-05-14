"""
Build approved candidate queue.

State:
- Reads primary cloud clarification.
- Reads backlog cloud clarifications if present.
- Writes one durable queue of products waiting for Chris-approved affiliate URLs.

Safety:
- No affiliate links are created.
- No product swaps.
- No commits, pushes, or publishing.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PRIMARY = ROOT / "data/product_candidates/cloud_candidate_clarification.json"
BACKLOG = ROOT / "data/product_candidates/backlog_cloud_clarifications.json"
QUEUE_JSON = ROOT / "data/product_candidates/approved_candidate_queue.json"
QUEUE_MD = ROOT / "data/product_candidates/approved_candidate_queue.md"
LOG_FILE = ROOT / "logs/approved_candidate_queue.log"


def setup_logging() -> None:
    """Create queue generation log."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )


def load_optional(path: Path) -> dict[str, Any]:
    """Load optional JSON file."""
    if not path.is_file():
        return {}

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        logging.exception("Failed to load %s: %s", path, exc)
        raise


def write_text(path: Path, content: str) -> None:
    """Write text with useful error context."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    except Exception as exc:
        logging.exception("Failed to write %s: %s", path, exc)
        raise


def write_json(path: Path, payload: dict[str, Any]) -> None:
    """Write JSON with deterministic formatting."""
    write_text(path, json.dumps(payload, indent=2))


def locked_flags() -> dict[str, bool]:
    """Return safety locks."""
    return {
        "affiliate_link_changes_allowed": False,
        "product_swap_allowed": False,
        "git_commit_allowed": False,
        "git_push_allowed": False,
        "publish_allowed": False,
    }


def approved_row(source: str, item: dict[str, Any]) -> dict[str, Any]:
    """Normalize an approved cloud clarification row."""
    return {
        "source": source,
        "slot": item.get("slot"),
        "slug": item.get("slug"),
        "title": item.get("title"),
        "product_name": item.get("best_candidate_product_name"),
        "brand": item.get("best_candidate_brand"),
        "asin": item.get("best_candidate_asin"),
        "amazon_url": item.get("best_candidate_amazon_url"),
        "page_angle": item.get("page_angle"),
        "risk_notes": item.get("risk_notes", []),
        "chris_approval_checklist": item.get("chris_approval_checklist", []),
        "approved_affiliate_url": "",
        "approved_by_chris": False,
        "live_enabled": False,
        "next_required_gate": "chris_affiliate_url_for_approved_candidate",
        **locked_flags(),
    }


def collect_primary(primary: dict[str, Any]) -> list[dict[str, Any]]:
    """Collect approved primary candidate."""
    if primary.get("status") != "cloud_candidate_clarified":
        return []

    if primary.get("final_decision") != "approve":
        return []

    return [approved_row("primary_cloud_clarification", primary)]


def collect_backlog(backlog: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Collect approved and held backlog candidates."""
    approved: list[dict[str, Any]] = []
    held: list[dict[str, Any]] = []

    for item in backlog.get("items", []):
        decision = item.get("final_decision")

        if decision == "approve":
            approved.append(approved_row("backlog_cloud_clarification", item))
        else:
            held.append(
                {
                    "slot": item.get("slot"),
                    "slug": item.get("slug"),
                    "title": item.get("title"),
                    "product_name": item.get("best_candidate_product_name"),
                    "asin": item.get("best_candidate_asin"),
                    "final_decision": decision,
                    "next_required_gate": item.get("next_required_gate"),
                    "reason": item.get("reasons", []),
                }
            )

    return approved, held


def dedupe(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Deduplicate queue rows by slug then ASIN."""
    seen: set[tuple[str, str]] = set()
    clean: list[dict[str, Any]] = []

    for row in rows:
        key = (str(row.get("slug")), str(row.get("asin")))

        if key in seen:
            continue

        seen.add(key)
        clean.append(row)

    return clean


def build_queue() -> dict[str, Any]:
    """Build approved candidate queue."""
    setup_logging()
    primary = load_optional(PRIMARY)
    backlog = load_optional(BACKLOG)

    backlog_approved, held = collect_backlog(backlog)
    approved = dedupe(collect_primary(primary) + backlog_approved)

    return {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "approved_candidate_queue_ready",
        "approved_count": len(approved),
        "held_count": len(held),
        "approved_items": approved,
        "held_items": held,
        "next_required_gate": "chris_affiliate_url_for_approved_candidates",
        **locked_flags(),
    }


def render_markdown(queue: dict[str, Any]) -> str:
    """Render queue as Markdown."""
    rows = []

    for item in queue["approved_items"]:
        rows.append(
            f"- Slot {item['slot']} `{item['slug']}`: "
            f"{item['product_name']} / ASIN `{item['asin']}`"
        )

    held_rows = []

    for item in queue["held_items"]:
        held_rows.append(
            f"- Slot {item['slot']} `{item['slug']}`: "
            f"{item['product_name']} / decision `{item['final_decision']}`"
        )

    return f"""# Approved Candidate Queue

Status: `{queue["status"]}`

Approved waiting for Chris affiliate URL: `{queue["approved_count"]}`

Held candidates: `{queue["held_count"]}`

## Approved Items

{chr(10).join(rows) if rows else "- None"}

## Held Items

{chr(10).join(held_rows) if held_rows else "- None"}

## Safety Locks

- Affiliate link changes allowed: `{queue["affiliate_link_changes_allowed"]}`
- Product swap allowed: `{queue["product_swap_allowed"]}`
- Git commit allowed: `{queue["git_commit_allowed"]}`
- Git push allowed: `{queue["git_push_allowed"]}`
- Publish allowed: `{queue["publish_allowed"]}`
"""


def write_queue() -> dict[str, Any]:
    """Build and write approved candidate queue."""
    queue = build_queue()
    write_json(QUEUE_JSON, queue)
    write_text(QUEUE_MD, render_markdown(queue))
    return queue

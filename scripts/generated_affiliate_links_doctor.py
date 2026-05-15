"""
Validate generated Amazon affiliate links.

Read-only doctor.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LINKS = ROOT / "data/amazon_links/generated_affiliate_links_from_queue.json"


def main() -> int:
    """Validate generated links."""
    problems: list[str] = []

    if not LINKS.is_file():
        problems.append("missing generated affiliate links file")
    else:
        data = json.loads(LINKS.read_text(encoding="utf-8"))

        if data.get("status") != "generated_affiliate_links_ready":
            problems.append("bad status")

        if data.get("amazon_tag") != "maxyourheal06-20":
            problems.append("amazon_tag mismatch")

        if data.get("link_count", 0) < 1:
            problems.append("expected at least one generated link")

        for item in data.get("links", []):
            slug = item.get("slug", "unknown")
            asin = str(item.get("asin", ""))
            url = str(item.get("affiliate_url", ""))

            if not asin:
                problems.append(f"{slug}: missing ASIN")

            if f"/dp/{asin}/" not in url:
                problems.append(f"{slug}: affiliate URL missing ASIN path")

            if "tag=maxyourheal06-20" not in url:
                problems.append(f"{slug}: affiliate URL missing approved tag")

            if item.get("live_enabled") is not False:
                problems.append(f"{slug}: live_enabled must remain false")

        for locked in ["product_swap_allowed", "git_commit_allowed", "git_push_allowed", "publish_allowed"]:
            if data.get(locked) is not False:
                problems.append(f"{locked} must be false")

    print("RESULT:")

    if problems:
        print("GENERATED AFFILIATE LINKS STATE: NEEDS REVIEW")
        for problem in problems:
            print(f"- {problem}")
        return 1

    print("GENERATED AFFILIATE LINKS STATE: PASS")
    print("next_required_gate: registry_intake_then_page_injection")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

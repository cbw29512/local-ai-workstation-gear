"""
Run the money live gate for approved Amazon affiliate links.

State:
- Reads Amazon link registry.
- If only one link is live, enables generated affiliate links.
- Injects approved live links into pages.
- Generates redirects.
- Marks live products.
- Runs money/click doctors.

Safety:
- No git commit.
- No git push.
- No product swaps.
- No publishing outside existing local files.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data/amazon_links/approved_amazon_links.json"


def load_json(path: Path) -> dict[str, Any]:
    """Load JSON with useful failure context."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise RuntimeError(f"failed to load {path}: {exc}") from exc


def live_count() -> int:
    """Return count of live-enabled Amazon links."""
    registry = load_json(REGISTRY)
    return sum(1 for row in registry.get("links", []) if row.get("live_enabled") is True)


def run(command: list[str]) -> int:
    """Run a command and stream output."""
    print()
    print("===", " ".join(command), "===")

    result = subprocess.run(command, cwd=ROOT, text=True)

    if result.returncode != 0:
        print("RESULT: STOPPED")
        print(f"failed_command: {' '.join(command)}")

    return result.returncode


def require_script(path: str) -> bool:
    """Stop clearly when an expected script is missing."""
    full_path = ROOT / path

    if full_path.is_file():
        return True

    print("RESULT: STOPPED")
    print(f"missing required script: {path}")
    return False


def main() -> int:
    """Run money live gate."""
    required = [
        "scripts/enable_generated_affiliate_links_for_live.py",
        "scripts/live_generated_affiliate_links_doctor.py",
        "scripts/inject_approved_amazon_links.py",
        "scripts/generate_amazon_redirects.py",
        "scripts/mark_live_amazon_products.py",
        "scripts/amazon_link_registry_doctor.py",
        "scripts/money_layer_doctor.py",
        "scripts/click_tracking_doctor.py",
        "scripts/run_daily_money_update.py",
    ]

    for script in required:
        if not require_script(script):
            return 1

    before = live_count()
    print("RESULT:")
    print(f"live_enabled_links_before: {before}")

    if before < 4:
        steps = [
            ["python3", "scripts/enable_generated_affiliate_links_for_live.py"],
            ["python3", "scripts/live_generated_affiliate_links_doctor.py"],
        ]

        for step in steps:
            if run(step) != 0:
                return 1

    steps = [
        ["python3", "scripts/amazon_link_registry_doctor.py"],
        ["python3", "scripts/inject_approved_amazon_links.py"],
        ["python3", "scripts/generate_amazon_redirects.py"],
        ["python3", "scripts/mark_live_amazon_products.py"],
        ["python3", "scripts/amazon_link_registry_doctor.py"],
        ["python3", "scripts/live_generated_affiliate_links_doctor.py"],
        ["python3", "scripts/money_layer_doctor.py"],
        ["python3", "scripts/click_tracking_doctor.py"],
        ["python3", "scripts/run_daily_money_update.py"],
    ]

    for step in steps:
        if run(step) != 0:
            return 1

    after = live_count()

    print()
    print("RESULT: PASS")
    print(f"live_enabled_links_after: {after}")
    print("next_required_gate: review_git_status_and_commit")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

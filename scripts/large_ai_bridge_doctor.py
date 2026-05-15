"""
Validate Large AI bridge contract and response file.

State:
- Large AI bridge may be manual ChatGPT or future API-backed mode.
- Current mode is manual ChatGPT.
- The bridge validates safety locks before any local import.

Safety:
- Read-only doctor.
- No affiliate links.
- No product swaps.
- No commits, pushes, or publishing.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "data/large_ai_bridge/large_ai_bridge_contract.json"
REQUEST = ROOT / "data/large_ai_bridge/current_request.md"
RESPONSE = ROOT / "data/large_ai_bridge/current_response.json"
LOG_FILE = ROOT / "logs/large_ai_bridge_doctor.log"


def setup_logging() -> None:
    """Create doctor log file."""
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


def require_file(path: Path, label: str) -> list[str]:
    """Validate required file exists."""
    if path.is_file():
        return []

    return [f"missing {label}: {path}"]


def validate_locks(data: dict[str, Any], label: str) -> list[str]:
    """Validate safety locks are closed."""
    problems: list[str] = []

    for key in [
        "affiliate_links_created",
        "publish_recommended",
        "product_swap_allowed",
        "git_commit_allowed",
        "git_push_allowed",
        "publish_allowed",
    ]:
        if data.get(key) is not False:
            problems.append(f"{label}: {key} must be false")

    return problems


def main() -> int:
    """Run Large AI bridge doctor."""
    setup_logging()
    problems: list[str] = []

    problems.extend(require_file(CONTRACT, "contract"))
    problems.extend(require_file(REQUEST, "request"))
    problems.extend(require_file(RESPONSE, "response"))

    if CONTRACT.is_file():
        contract = load_json(CONTRACT)

        if contract.get("status") != "large_ai_bridge_active":
            problems.append("contract status must be large_ai_bridge_active")

        if contract.get("provider_mode") != "manual_chatgpt":
            problems.append("provider_mode must be manual_chatgpt for this stage")

        rules = contract.get("safety_rules", {})
        for key in [
            "affiliate_link_changes_allowed",
            "product_swap_allowed",
            "git_commit_allowed",
            "git_push_allowed",
            "publish_allowed",
            "spending_allowed",
            "outreach_allowed",
        ]:
            if rules.get(key) is not False:
                problems.append(f"contract safety_rules.{key} must be false")

    if RESPONSE.is_file():
        response = load_json(RESPONSE)
        problems.extend(validate_locks(response, "response"))

    print("RESULT:")

    if problems:
        print("LARGE AI BRIDGE STATE: NEEDS REVIEW")
        for problem in problems:
            print(f"- {problem}")
        return 1

    print("LARGE AI BRIDGE STATE: PASS")
    print("provider_mode: manual_chatgpt")
    print("next_required_gate: large_ai_response_paste")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

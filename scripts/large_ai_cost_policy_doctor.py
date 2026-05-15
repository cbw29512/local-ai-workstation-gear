"""
Validate Large AI cost-control policy.

State:
- Local AI handles routine hourly work.
- Large AI is only used for high-value handoffs.
- API calls are disabled by default.

Safety:
- Read-only doctor.
- No affiliate links.
- No product swaps.
- No commits, pushes, publishing, spending, or outreach.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "data/large_ai_bridge/large_ai_cost_policy.json"
LOG_FILE = ROOT / "logs/large_ai_cost_policy_doctor.log"


def setup_logging() -> None:
    """Create doctor log file."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )


def load_json(path: Path) -> dict[str, Any]:
    """Load JSON with clear error context."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        logging.exception("Failed to load %s: %s", path, exc)
        raise


def validate_policy(data: dict[str, Any]) -> list[str]:
    """Validate cost policy gates."""
    problems: list[str] = []

    if data.get("status") != "large_ai_cost_policy_active":
        problems.append("status must be large_ai_cost_policy_active")

    if data.get("default_provider_mode") != "manual_chatgpt":
        problems.append("default_provider_mode must be manual_chatgpt")

    if data.get("api_calls_enabled") is not False:
        problems.append("api_calls_enabled must be false by default")

    if data.get("hourly_large_ai_calls_allowed") is not False:
        problems.append("hourly_large_ai_calls_allowed must be false")

    if data.get("routine_monitoring_provider") != "local_ai_only":
        problems.append("routine_monitoring_provider must be local_ai_only")

    limits = data.get("future_api_mode_limits", {})
    if limits.get("daily_request_limit", 0) > 3:
        problems.append("daily_request_limit should stay at or below 3")

    if limits.get("write_only_to_staging") is not True:
        problems.append("future API mode must write only to staging")

    locks = data.get("safety_locks", {})
    for key in [
        "affiliate_link_changes_allowed",
        "product_swap_allowed",
        "git_commit_allowed",
        "git_push_allowed",
        "publish_allowed",
        "spending_allowed",
        "outreach_allowed",
    ]:
        if locks.get(key) is not False:
            problems.append(f"safety_locks.{key} must be false")

    return problems


def main() -> int:
    """Run Large AI cost policy doctor."""
    setup_logging()

    try:
        data = load_json(POLICY)
        problems = validate_policy(data)
    except Exception as exc:
        print("RESULT:")
        print("LARGE AI COST POLICY STATE: NEEDS REVIEW")
        print(f"- {exc}")
        return 1

    print("RESULT:")

    if problems:
        print("LARGE AI COST POLICY STATE: NEEDS REVIEW")
        for problem in problems:
            print(f"- {problem}")
        return 1

    print("LARGE AI COST POLICY STATE: PASS")
    print("provider_mode: manual_chatgpt")
    print("api_calls_enabled: false")
    print("hourly_large_ai_calls_allowed: false")
    print("next_required_gate: manual_large_ai_handoff_only")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

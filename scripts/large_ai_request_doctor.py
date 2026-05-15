"""
Validate Large AI request packet.

Read-only doctor.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUEST = ROOT / "data/large_ai_bridge/current_requests/home-organization-request.json"
REQUEST_MD = ROOT / "data/large_ai_bridge/current_requests/home-organization-request.md"


def main() -> int:
    """Validate Large AI request."""
    problems: list[str] = []

    if not REQUEST.is_file():
        problems.append("missing request JSON")
    else:
        data = json.loads(REQUEST.read_text(encoding="utf-8"))

        if data.get("status") != "large_ai_request_ready":
            problems.append(f"bad status: {data.get('status')}")

        if data.get("provider_mode") != "manual_chatgpt":
            problems.append("provider_mode must be manual_chatgpt")

        if data.get("api_call_allowed") is not False:
            problems.append("api_call_allowed must be false")

        if data.get("manual_chatgpt_required") is not True:
            problems.append("manual_chatgpt_required must be true")

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

    if not REQUEST_MD.is_file():
        problems.append("missing request Markdown handoff")

    print("RESULT:")

    if problems:
        print("LARGE AI REQUEST STATE: NEEDS REVIEW")
        for problem in problems:
            print(f"- {problem}")
        return 1

    print("LARGE AI REQUEST STATE: PASS")
    print("provider_mode: manual_chatgpt")
    print("next_required_gate: paste_large_ai_response")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""
Generate Large AI request only when needed.

State:
- Reads Large AI cost policy.
- Checks current vertical workflow state.
- Creates a manual ChatGPT handoff only for high-value tasks.

Safety:
- No API calls.
- No affiliate links.
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

POLICY = ROOT / "data/large_ai_bridge/large_ai_cost_policy.json"
PROMPT = ROOT / "data/site_portfolio/cloud_vertical_active_prompts/home-organization-active-prompt.md"
STAGED = ROOT / "data/site_portfolio/cloud_vertical_results/staged-home-organization.json"

REQUEST_JSON = ROOT / "data/large_ai_bridge/current_requests/home-organization-request.json"
REQUEST_MD = ROOT / "data/large_ai_bridge/current_requests/home-organization-request.md"
LOG_FILE = ROOT / "logs/generate_large_ai_request.log"


def setup_logging() -> None:
    """Create request-generation log."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )


def load_json(path: Path) -> dict[str, Any]:
    """Load JSON with clear failure context."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        logging.exception("Failed to load %s: %s", path, exc)
        raise


def read_text(path: Path) -> str:
    """Read text with clear failure context."""
    if not path.is_file():
        raise FileNotFoundError(f"missing file: {path}")

    return path.read_text(encoding="utf-8")


def staged_needs_large_ai() -> bool:
    """Return true when staged result still needs cloud product research."""
    data = load_json(STAGED)
    return (
        data.get("status") == "awaiting_cloud_vertical_research"
        and len(data.get("items", [])) == 0
    )


def api_allowed(policy: dict[str, Any]) -> bool:
    """Return whether API calls are allowed by policy."""
    return policy.get("api_calls_enabled") is True


def build_request(policy: dict[str, Any]) -> dict[str, Any]:
    """Build one Large AI request packet."""
    return {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "large_ai_request_ready",
        "provider_mode": policy.get("default_provider_mode", "manual_chatgpt"),
        "task_type": "cloud_vertical_product_research",
        "reason": "Home organization vertical needs 24 Amazon-only products.",
        "source_prompt": str(PROMPT),
        "target_response": str(STAGED),
        "api_call_allowed": api_allowed(policy),
        "manual_chatgpt_required": not api_allowed(policy),
        "expected_output": {
            "status": "cloud_vertical_research_completed",
            "vertical_slug": "home-organization",
            "items": 24
        },
        "safety_locks": {
            "affiliate_link_changes_allowed": False,
            "product_swap_allowed": False,
            "git_commit_allowed": False,
            "git_push_allowed": False,
            "publish_allowed": False,
            "spending_allowed": False,
            "outreach_allowed": False
        },
        "next_required_gate": "paste_large_ai_response"
    }


def render_markdown(request: dict[str, Any], prompt: str) -> str:
    """Render manual ChatGPT handoff."""
    return f"""# Large AI Manual Handoff

Status: `{request["status"]}`

Provider mode: `{request["provider_mode"]}`

Task type: `{request["task_type"]}`

Reason:
{request["reason"]}

Target response file:
`{request["target_response"]}`

API call allowed: `{request["api_call_allowed"]}`

Manual ChatGPT required: `{request["manual_chatgpt_required"]}`

## Instructions

Paste the prompt below into ChatGPT / Large AI.

Return JSON only. No commentary.

---

{prompt}
"""


def main() -> int:
    """Generate Large AI request if needed."""
    setup_logging()

    try:
        policy = load_json(POLICY)

        if policy.get("api_calls_enabled") is True:
            print("RESULT: STOPPED")
            print("api_calls_enabled is true; this manual gate expects API disabled")
            return 1

        if not staged_needs_large_ai():
            print("RESULT: PASS")
            print("large_ai_needed: false")
            print("next_required_gate: local_validation_or_chris_review")
            return 0

        request = build_request(policy)
        prompt = read_text(PROMPT)

        REQUEST_JSON.parent.mkdir(parents=True, exist_ok=True)
        REQUEST_JSON.write_text(json.dumps(request, indent=2), encoding="utf-8")
        REQUEST_MD.write_text(render_markdown(request, prompt), encoding="utf-8")
    except Exception as exc:
        print("RESULT: ERROR")
        print(exc)
        return 1

    print("RESULT: PASS")
    print("large_ai_needed: true")
    print(f"request_json: {REQUEST_JSON}")
    print(f"request_md: {REQUEST_MD}")
    print("next_required_gate: paste_large_ai_response")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

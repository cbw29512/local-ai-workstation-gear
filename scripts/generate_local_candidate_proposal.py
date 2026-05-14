"""
Generate local AI Amazon candidate proposal.

Safety:
- Proposal only.
- No affiliate links.
- No product swaps.
- No commits or pushes.
"""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from webmaster.candidate_cloud_packet import render_cloud_packet
from webmaster.candidate_io import setup_logging, write_json, write_text
from webmaster.candidate_paths import CLOUD_PACKET_MD, PROPOSAL_JSON
from webmaster.candidate_selector import build_proposal


def main() -> int:
    """Generate local candidate proposal and cloud packet."""
    setup_logging()

    try:
        proposal = build_proposal()
        write_json(PROPOSAL_JSON, proposal)
        write_text(CLOUD_PACKET_MD, render_cloud_packet(proposal))
    except Exception as exc:
        print("RESULT: ERROR")
        print(exc)
        return 1

    print("RESULT: PASS")
    print(f"proposal_status: {proposal['status']}")
    print(f"slug: {proposal.get('slug', 'none')}")
    print(f"next_required_gate: {proposal['next_required_gate']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

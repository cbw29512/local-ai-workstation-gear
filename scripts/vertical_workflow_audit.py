"""
Audit the non-tech vertical research workflow.

State:
- Prompt is for large/cloud AI.
- Staged JSON is where returned cloud JSON is pasted.
- Active result is what the validator checks.
- Handoff decides which vertical/result file is active.

Safety:
- Read-only audit.
- No affiliate links.
- No product swaps.
- No commits or pushes.
- No publishing.
"""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from webmaster.vertical_workflow_checks import gather_audit_state
from webmaster.vertical_workflow_report import print_report


def main() -> int:
    """Run vertical workflow audit."""
    problems, staged, active = gather_audit_state()
    return print_report(problems, staged, active)


if __name__ == "__main__":
    raise SystemExit(main())

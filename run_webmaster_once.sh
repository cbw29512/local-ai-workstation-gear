#!/bin/bash
set -euo pipefail

cd /Users/chris/Desktop/local-ai-workstation-gear

if command -v python3 >/dev/null 2>&1; then
  python3 scripts/webmaster_run_once.py
else
  python scripts/webmaster_run_once.py
fi

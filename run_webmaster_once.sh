#!/bin/bash
set -euo pipefail

cd /Users/chris/Code/local-ai-workstation-gear

/usr/bin/python3 scripts/webmaster_run_once.py
/usr/bin/python3 scripts/webmaster_autopilot_run_once.py
/usr/bin/python3 scripts/money_monitor_run_once.py
/usr/bin/python3 scripts/candidate_factory_run_once.py

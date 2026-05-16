#!/bin/bash
set -euo pipefail

cd /Users/chris/Code/local-ai-workstation-gear

/usr/bin/python3 scripts/webmaster_run_once.py
/usr/bin/python3 scripts/webmaster_autopilot_run_once.py
/usr/bin/python3 scripts/money_monitor_run_once.py
/usr/bin/python3 scripts/candidate_factory_run_once.py
/usr/bin/python3 scripts/generate_candidate_backlog.py
/usr/bin/python3 scripts/candidate_backlog_doctor.py
/usr/bin/python3 scripts/generate_approved_candidate_queue.py
/usr/bin/python3 scripts/approved_candidate_queue_doctor.py
/usr/bin/python3 scripts/generate_non_tech_vertical_proposals.py
/usr/bin/python3 scripts/non_tech_vertical_proposals_doctor.py
/usr/bin/python3 scripts/generate_cloud_vertical_research_packets.py
/usr/bin/python3 scripts/cloud_vertical_research_packets_doctor.py
/usr/bin/python3 scripts/cloud_vertical_result_doctor.py
/usr/bin/python3 scripts/hourly_money_operator.py
/usr/bin/python3 scripts/hourly_traffic_operator.py
/usr/bin/python3 scripts/hourly_site_webmaster_operator.py

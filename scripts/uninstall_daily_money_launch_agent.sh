#!/bin/bash
set -euo pipefail

LABEL="com.chris.local-ai-workstation-money-daily"
PLIST="$HOME/Library/LaunchAgents/${LABEL}.plist"

launchctl bootout "gui/$(id -u)" "$PLIST" 2>/dev/null || true
rm -f "$PLIST"

echo "removed ${LABEL}"

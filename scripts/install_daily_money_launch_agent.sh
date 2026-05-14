#!/bin/bash
set -euo pipefail

LABEL="com.chris.local-ai-workstation-money-daily"
PLIST="$HOME/Library/LaunchAgents/${LABEL}.plist"
PROJECT="/Users/chris/Code/local-ai-workstation-gear"

mkdir -p "$PROJECT/logs"

cat > "$PLIST" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "https://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
  <dict>
    <key>Label</key>
    <string>${LABEL}</string>

    <key>ProgramArguments</key>
    <array>
      <string>/usr/bin/python3</string>
      <string>${PROJECT}/scripts/run_daily_money_update.py</string>
    </array>

    <key>WorkingDirectory</key>
    <string>${PROJECT}</string>

    <key>StartCalendarInterval</key>
    <dict>
      <key>Hour</key>
      <integer>9</integer>
      <key>Minute</key>
      <integer>10</integer>
    </dict>

    <key>RunAtLoad</key>
    <true/>

    <key>StandardOutPath</key>
    <string>${PROJECT}/logs/daily_money_launchd.out.log</string>

    <key>StandardErrorPath</key>
    <string>${PROJECT}/logs/daily_money_launchd.err.log</string>
  </dict>
</plist>
PLIST

chmod 644 "$PLIST"
plutil -lint "$PLIST"

launchctl bootout "gui/$(id -u)" "$PLIST" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$PLIST"
launchctl kickstart -k "gui/$(id -u)/${LABEL}" 2>/dev/null || true

echo "installed ${LABEL}"
launchctl list | grep "$LABEL" || true

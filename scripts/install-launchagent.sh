#!/usr/bin/env bash
set -euo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"
PYTHON="$REPO/.venv/bin/python"
SRC="$REPO/docs/com.bg3.modalert.plist"
DST="$HOME/Library/LaunchAgents/com.bg3.modalert.plist"
mkdir -p "$HOME/Library/LaunchAgents"
sed -e "s#__REPO__#${REPO//\\/\\\\}#g" \
    -e "s#__PYTHON__#${PYTHON//\\/\\\\}#g" \
    "$SRC" > "$DST"
launchctl unload "$DST" 2>/dev/null || true
launchctl load "$DST"
echo "Installed: $DST"
echo "Run now with: launchctl start com.bg3.modalert"

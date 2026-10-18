#!/usr/bin/env bash
# Ghost of Tsushima — generated from palette.json by src/desktop.py
CONFIG_DIR="${CONFIG_DIR:-$HOME/.config/sketchybar}"
# shellcheck source-path=SCRIPTDIR/.. source=colors.sh
source "$CONFIG_DIR/colors.sh"

IFACE="$(networksetup -listallhardwareports 2>/dev/null | awk '/Wi-Fi|AirPort/{getline; print $2; exit}')"
IFACE="${IFACE:-en0}"
IP="$(ipconfig getifaddr "$IFACE" 2>/dev/null)"

if [ -z "$IP" ]; then
  sketchybar --set "$NAME" icon="" icon.color="$SMOKE" label="offline"
  exit 0
fi

# Recent macOS hides the SSID from command-line tools; fall back to a plain label.
SSID="$(ipconfig getsummary "$IFACE" 2>/dev/null | awk -F ' SSID : ' '/ SSID : /{print $2; exit}')"
case "$SSID" in
  ""|"<redacted>") SSID="$(networksetup -getairportnetwork "$IFACE" 2>/dev/null | sed -n 's/^Current Wi-Fi Network: //p')" ;;
esac
SSID="${SSID:-online}"

sketchybar --set "$NAME" icon="" icon.color="$SKY" label="$SSID"

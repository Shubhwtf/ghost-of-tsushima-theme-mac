#!/usr/bin/env bash
# Ghost of Tsushima — generated from palette.json by src/desktop.py
# Focus space $1: uses yabai when it is installed, otherwise the Ctrl+<n> shortcut
# (enable "Switch to Desktop n" in System Settings > Keyboard > Shortcuts > Mission Control).
sid="$1"
if command -v yabai >/dev/null 2>&1; then
  yabai -m space --focus "$sid" 2>/dev/null && exit 0
fi
case "$sid" in
  1) code=18 ;; 2) code=19 ;; 3) code=20 ;; 4) code=21 ;; 5) code=23 ;;
  6) code=22 ;; 7) code=26 ;; 8) code=28 ;; 9) code=25 ;; *) exit 0 ;;
esac
osascript -e "tell application \"System Events\" to key code $code using control down" >/dev/null 2>&1

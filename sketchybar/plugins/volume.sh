#!/usr/bin/env bash
# Ghost of Tsushima — generated from palette.json by src/desktop.py
# On volume_change SketchyBar puts the new volume (0-100) in $INFO.
if [ "$SENDER" = "volume_change" ]; then
  VOLUME="$INFO"
else
  VOLUME="$(osascript -e 'output volume of (get volume settings)' 2>/dev/null)"
fi
VOLUME="${VOLUME:-0}"

case "$VOLUME" in
  [6-9][0-9]|100) ICON="" ;;
  [3-5][0-9]) ICON="" ;;
  [1-9]|[1-2][0-9]) ICON="" ;;
  *) ICON="" ;;
esac

sketchybar --set "$NAME" icon="$ICON" label="${VOLUME}%"

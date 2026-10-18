#!/usr/bin/env bash
# Ghost of Tsushima — generated from palette.json by src/desktop.py
CONFIG_DIR="${CONFIG_DIR:-$HOME/.config/sketchybar}"
# shellcheck source-path=SCRIPTDIR/.. source=colors.sh
source "$CONFIG_DIR/colors.sh"

BATT="$(pmset -g batt)"
PERCENT="$(printf '%s' "$BATT" | grep -Eo '[0-9]+%' | head -n1 | tr -d '%')"
if [ -z "$PERCENT" ]; then
  sketchybar --set "$NAME" drawing=off   # desktop Mac: no battery
  exit 0
fi

case "$PERCENT" in
  100|9[0-9]) ICON=""; COLOR="$PAPER" ;;
  [6-8][0-9]) ICON=""; COLOR="$PAPER" ;;
  [3-5][0-9]) ICON=""; COLOR="$GOLD" ;;
  [1-2][0-9]) ICON=""; COLOR="$VERMILION" ;;
  *) ICON=""; COLOR="$CRIMSON" ;;
esac
if printf '%s' "$BATT" | grep -q 'AC Power'; then
  ICON=""
  COLOR="$GOLD_HI"
fi

sketchybar --set "$NAME" drawing=on icon="$ICON" icon.color="$COLOR" label="${PERCENT}%"

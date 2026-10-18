#!/usr/bin/env bash
# Ghost of Tsushima — generated from palette.json by src/desktop.py
# Highlights the focused space with a lacquer-red tab. SketchyBar sets $NAME and $SELECTED.
CONFIG_DIR="${CONFIG_DIR:-$HOME/.config/sketchybar}"
# shellcheck source-path=SCRIPTDIR/.. source=colors.sh
source "$CONFIG_DIR/colors.sh"

if [ "$SELECTED" = "true" ]; then
  sketchybar --set "$NAME" background.drawing=on icon.highlight=on
else
  sketchybar --set "$NAME" background.drawing=off icon.highlight=off
fi

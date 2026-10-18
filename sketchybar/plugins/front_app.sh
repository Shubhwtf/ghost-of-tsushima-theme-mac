#!/usr/bin/env bash
# Ghost of Tsushima — generated from palette.json by src/desktop.py
# $INFO holds the name of the newly focused application.
if [ "$SENDER" = "front_app_switched" ]; then
  sketchybar --set "$NAME" label="$INFO"
fi

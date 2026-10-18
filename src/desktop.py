#!/usr/bin/env python3
"""Generate the macOS desktop layer from palette.json: SketchyBar (bar, items,
plugins), JankyBorders and VS Code / Cursor colours.

Nerd Font glyphs are written with chr() so the shell scripts contain real
characters (macOS /bin/bash 3.2 cannot expand \\u escapes).

usage: desktop.py [ROOT]
"""
import json
import os
import stat
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from palette import C, NAME, ROLE  # noqa: E402
from emblem import emblem_svg  # noqa: E402

ROOT = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HDR = f"{NAME} — generated from palette.json by src/desktop.py"

GL = {k: chr(v) for k, v in {
    "clock": 0xF017, "cal": 0xF073, "vol_mute": 0xF6A9, "vol_low": 0xF026, "vol_mid": 0xF027, "vol_hi": 0xF028,
    "bat_0": 0xF244, "bat_25": 0xF243, "bat_50": 0xF242, "bat_75": 0xF241, "bat_100": 0xF240, "bolt": 0xF0E7,
    "wifi": 0xF1EB, "wifi_off": 0xF0B1, "diamond": 0x25C6,
}.items()}


def argb(h, a="ff"):
    return f"0x{a}{h.lstrip('#')}"


def write(rel, text, exe=False):
    path = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(text)
    if exe:
        os.chmod(path, os.stat(path).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    print("wrote", rel)


def sketchybar():
    cols = "\n".join(f"export {k.upper()}={argb(v)}" for k, v in C.items())
    write("sketchybar/colors.sh", f"""#!/usr/bin/env bash
# {HDR}
# Colours are 0xAARRGGBB.
{cols}

export BAR_COLOR=0xf00b0a0a
export BAR_BORDER={argb(C['blood'])}
export ITEM_BG={argb(C['ash'])}
export ACCENT={argb(C['lacquer'])}
export TRANSPARENT=0x00000000
""", exe=True)

    kanji = ["一", "二", "三", "四", "五", "六", "七", "八", "九", "十"]
    write("sketchybar/sketchybarrc", f"""#!/usr/bin/env bash
# 冥人 Ghost of Tsushima — SketchyBar
# ~/.config/sketchybar/sketchybarrc   (needs: brew install sketchybar, a Nerd Font)

CONFIG_DIR="${{CONFIG_DIR:-$HOME/.config/sketchybar}}"
PLUGIN_DIR="$CONFIG_DIR/plugins"
# shellcheck source-path=SCRIPTDIR source=colors.sh
source "$CONFIG_DIR/colors.sh"

FONT="JetBrainsMono Nerd Font"

# ---- the bar: ink, blurred, a hairline of blood red underneath --------------
sketchybar --bar position=top \\
                 height=34 \\
                 color="$BAR_COLOR" \\
                 blur_radius=30 \\
                 border_width=1 \\
                 border_color="$BAR_BORDER" \\
                 padding_left=10 \\
                 padding_right=10 \\
                 shadow=off \\
                 topmost=off \\
                 sticky=on

sketchybar --default icon.font="$FONT:Bold:15.0" \\
                     icon.color="$PAPER" \\
                     label.font="$FONT:Bold:13.0" \\
                     label.color="$PAPER" \\
                     icon.padding_left=6 \\
                     icon.padding_right=4 \\
                     label.padding_left=4 \\
                     label.padding_right=8 \\
                     background.height=24 \\
                     background.corner_radius=6 \\
                     updates=when_shown

# ---- left: red ensō, kanji spaces, front app ---------------------------------
sketchybar --add item enso left \\
           --set enso background.image="$CONFIG_DIR/icons/enso.png" \\
                      background.image.scale=0.5 \\
                      background.color="$TRANSPARENT" \\
                      background.drawing=on \\
                      icon.drawing=off \\
                      label.drawing=off \\
                      width=34 \\
                      padding_left=2 \\
                      padding_right=6 \\
                      click_script="open -a 'Mission Control'"

SPACE_ICONS=({" ".join(f'"{k}"' for k in kanji)})
for i in "${{!SPACE_ICONS[@]}}"; do
  sid=$((i + 1))
  sketchybar --add space "space.$sid" left \\
             --set "space.$sid" associated_space="$sid" \\
                                icon="${{SPACE_ICONS[i]}}" \\
                                icon.font="Hiragino Mincho ProN:W6:14.0" \\
                                icon.color="$SMOKE" \\
                                icon.highlight_color="$PAPER_HI" \\
                                icon.padding_left=9 \\
                                icon.padding_right=9 \\
                                label.drawing=off \\
                                background.color="$LACQUER" \\
                                background.height=24 \\
                                background.drawing=off \\
                                script="$PLUGIN_DIR/space.sh" \\
                                click_script="$PLUGIN_DIR/space_click.sh $sid"
done

sketchybar --add item divider left \\
           --set divider icon="{GL['diamond']}" \\
                         icon.font="$FONT:Bold:9.0" \\
                         icon.color="$LACQUER" \\
                         label.drawing=off \\
                         padding_left=6 \\
                         padding_right=2

sketchybar --add item front_app left \\
           --set front_app icon.drawing=off \\
                           label.color="$PAPER_HI" \\
                           label.font="$FONT:Bold:13.0" \\
                           script="$PLUGIN_DIR/front_app.sh" \\
           --subscribe front_app front_app_switched

# ---- right: clock, battery, volume, wifi in one ash capsule ------------------
sketchybar --add item clock right \\
           --set clock update_freq=15 \\
                       icon="{GL['clock']}" \\
                       icon.color="$VERMILION" \\
                       script="$PLUGIN_DIR/clock.sh" \\
           --subscribe clock system_woke

sketchybar --add item battery right \\
           --set battery update_freq=120 \\
                         script="$PLUGIN_DIR/battery.sh" \\
           --subscribe battery system_woke power_source_change

sketchybar --add item volume right \\
           --set volume icon.color="$GOLD" \\
                        script="$PLUGIN_DIR/volume.sh" \\
           --subscribe volume volume_change

sketchybar --add item wifi right \\
           --set wifi update_freq=30 \\
                      icon.color="$SKY" \\
                      script="$PLUGIN_DIR/wifi.sh" \\
           --subscribe wifi wifi_change system_woke

sketchybar --add bracket status clock battery volume wifi \\
           --set status background.color="$ASH" \\
                        background.border_color="$STONE" \\
                        background.border_width=1 \\
                        background.corner_radius=8 \\
                        background.height=26

sketchybar --update
""", exe=True)

    write("sketchybar/plugins/space.sh", f"""#!/usr/bin/env bash
# {HDR}
# Highlights the focused space with a lacquer-red tab. SketchyBar sets $NAME and $SELECTED.
CONFIG_DIR="${{CONFIG_DIR:-$HOME/.config/sketchybar}}"
# shellcheck source-path=SCRIPTDIR/.. source=colors.sh
source "$CONFIG_DIR/colors.sh"

if [ "$SELECTED" = "true" ]; then
  sketchybar --set "$NAME" background.drawing=on icon.highlight=on
else
  sketchybar --set "$NAME" background.drawing=off icon.highlight=off
fi
""", exe=True)

    write("sketchybar/plugins/space_click.sh", f"""#!/usr/bin/env bash
# {HDR}
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
osascript -e "tell application \\"System Events\\" to key code $code using control down" >/dev/null 2>&1
""", exe=True)

    write("sketchybar/plugins/front_app.sh", f"""#!/usr/bin/env bash
# {HDR}
# $INFO holds the name of the newly focused application.
if [ "$SENDER" = "front_app_switched" ]; then
  sketchybar --set "$NAME" label="$INFO"
fi
""", exe=True)

    write("sketchybar/plugins/clock.sh", f"""#!/usr/bin/env bash
# {HDR}
sketchybar --set "$NAME" label="$(date '+%a %d %b  %H:%M')"
""", exe=True)

    write("sketchybar/plugins/battery.sh", f"""#!/usr/bin/env bash
# {HDR}
CONFIG_DIR="${{CONFIG_DIR:-$HOME/.config/sketchybar}}"
# shellcheck source-path=SCRIPTDIR/.. source=colors.sh
source "$CONFIG_DIR/colors.sh"

BATT="$(pmset -g batt)"
PERCENT="$(printf '%s' "$BATT" | grep -Eo '[0-9]+%' | head -n1 | tr -d '%')"
if [ -z "$PERCENT" ]; then
  sketchybar --set "$NAME" drawing=off   # desktop Mac: no battery
  exit 0
fi

case "$PERCENT" in
  100|9[0-9]) ICON="{GL['bat_100']}"; COLOR="$PAPER" ;;
  [6-8][0-9]) ICON="{GL['bat_75']}"; COLOR="$PAPER" ;;
  [3-5][0-9]) ICON="{GL['bat_50']}"; COLOR="$GOLD" ;;
  [1-2][0-9]) ICON="{GL['bat_25']}"; COLOR="$VERMILION" ;;
  *) ICON="{GL['bat_0']}"; COLOR="$CRIMSON" ;;
esac
if printf '%s' "$BATT" | grep -q 'AC Power'; then
  ICON="{GL['bolt']}"
  COLOR="$GOLD_HI"
fi

sketchybar --set "$NAME" drawing=on icon="$ICON" icon.color="$COLOR" label="${{PERCENT}}%"
""", exe=True)

    write("sketchybar/plugins/volume.sh", f"""#!/usr/bin/env bash
# {HDR}
# On volume_change SketchyBar puts the new volume (0-100) in $INFO.
if [ "$SENDER" = "volume_change" ]; then
  VOLUME="$INFO"
else
  VOLUME="$(osascript -e 'output volume of (get volume settings)' 2>/dev/null)"
fi
VOLUME="${{VOLUME:-0}}"

case "$VOLUME" in
  [6-9][0-9]|100) ICON="{GL['vol_hi']}" ;;
  [3-5][0-9]) ICON="{GL['vol_mid']}" ;;
  [1-9]|[1-2][0-9]) ICON="{GL['vol_low']}" ;;
  *) ICON="{GL['vol_mute']}" ;;
esac

sketchybar --set "$NAME" icon="$ICON" label="${{VOLUME}}%"
""", exe=True)

    write("sketchybar/plugins/wifi.sh", f"""#!/usr/bin/env bash
# {HDR}
CONFIG_DIR="${{CONFIG_DIR:-$HOME/.config/sketchybar}}"
# shellcheck source-path=SCRIPTDIR/.. source=colors.sh
source "$CONFIG_DIR/colors.sh"

IFACE="$(networksetup -listallhardwareports 2>/dev/null | awk '/Wi-Fi|AirPort/{{getline; print $2; exit}}')"
IFACE="${{IFACE:-en0}}"
IP="$(ipconfig getifaddr "$IFACE" 2>/dev/null)"

if [ -z "$IP" ]; then
  sketchybar --set "$NAME" icon="{GL['wifi_off']}" icon.color="$SMOKE" label="offline"
  exit 0
fi

# Recent macOS hides the SSID from command-line tools; fall back to a plain label.
SSID="$(ipconfig getsummary "$IFACE" 2>/dev/null | awk -F ' SSID : ' '/ SSID : /{{print $2; exit}}')"
case "$SSID" in
  ""|"<redacted>") SSID="$(networksetup -getairportnetwork "$IFACE" 2>/dev/null | sed -n 's/^Current Wi-Fi Network: //p')" ;;
esac
SSID="${{SSID:-online}}"

sketchybar --set "$NAME" icon="{GL['wifi']}" icon.color="$SKY" label="$SSID"
""", exe=True)

    # the ensō for the bar: rendered from the emblem, 64 px (shown at 32)
    icon = os.path.join(ROOT, "sketchybar", "icons", "enso.png")
    os.makedirs(os.path.dirname(icon), exist_ok=True)
    subprocess.run(["rsvg-convert", "-w", "64", "-h", "64", "-o", icon], input=emblem_svg(1024, small=True).encode(),
                   check=True)
    print("wrote sketchybar/icons/enso.png")


def borders():
    write("borders/bordersrc", f"""#!/usr/bin/env bash
# {HDR}
# JankyBorders: ~/.config/borders/bordersrc (brew install FelixKratz/formulae/borders)
# Focused window: lacquer red. Everything else: ash.
options=(
  style=round
  width=5.0
  hidpi=on
  order=above
  active_color={argb(C['lacquer'])}
  inactive_color={argb(C['ash'])}
)

borders "${{options[@]}}"
""", exe=True)


def vscode():
    c = C
    ui = {
        "editor.background": ROLE["background"], "editor.foreground": c["paper"],
        "editor.lineHighlightBackground": c["ash"], "editor.selectionBackground": c["blood"],
        "editor.selectionHighlightBackground": c["blood"] + "88", "editor.findMatchBackground": c["gold"] + "88",
        "editor.findMatchHighlightBackground": c["gold"] + "44", "editorCursor.foreground": c["vermilion"],
        "editorLineNumber.foreground": c["slate"], "editorLineNumber.activeForeground": c["vermilion"],
        "editorIndentGuide.background1": c["ash"], "editorIndentGuide.activeBackground1": c["blood"],
        "editorBracketMatch.border": c["gold"], "editorWhitespace.foreground": c["stone"],
        "editorGutter.addedBackground": c["moss"], "editorGutter.modifiedBackground": c["gold"],
        "editorGutter.deletedBackground": c["crimson"], "editorError.foreground": c["crimson"],
        "editorWarning.foreground": c["gold"], "editorInfo.foreground": c["sky"],
        "activityBar.background": c["ink"], "activityBar.foreground": c["paper"],
        "activityBar.inactiveForeground": c["smoke"], "activityBar.activeBorder": c["lacquer"],
        "activityBarBadge.background": c["lacquer"], "activityBarBadge.foreground": c["paper_hi"],
        "sideBar.background": c["ink"], "sideBar.foreground": c["rice"], "sideBar.border": c["ink"],
        "sideBarTitle.foreground": c["vermilion"], "sideBarSectionHeader.background": c["ink"],
        "sideBarSectionHeader.foreground": c["gold"], "list.activeSelectionBackground": c["stone"],
        "list.activeSelectionForeground": c["paper_hi"], "list.hoverBackground": c["ash"],
        "list.inactiveSelectionBackground": c["ash"], "list.highlightForeground": c["vermilion"],
        "list.focusOutline": c["lacquer"], "focusBorder": c["lacquer"],
        "titleBar.activeBackground": c["ink"], "titleBar.activeForeground": c["paper"],
        "titleBar.inactiveBackground": c["ink"], "titleBar.inactiveForeground": c["smoke"],
        "statusBar.background": c["ink"], "statusBar.foreground": c["mist"], "statusBar.border": c["blood"],
        "statusBar.debuggingBackground": c["lacquer"], "statusBar.noFolderBackground": c["ink"],
        "statusBarItem.remoteBackground": c["lacquer"], "statusBarItem.remoteForeground": c["paper_hi"],
        "tab.activeBackground": ROLE["background"], "tab.activeForeground": c["paper_hi"],
        "tab.activeBorderTop": c["lacquer"], "tab.inactiveBackground": c["ink"],
        "tab.inactiveForeground": c["smoke"], "tab.border": c["ink"], "editorGroupHeader.tabsBackground": c["ink"],
        "panel.background": c["ink"], "panel.border": c["stone"], "panelTitle.activeBorder": c["lacquer"],
        "panelTitle.activeForeground": c["paper"], "terminal.background": ROLE["background"],
        "terminal.foreground": c["paper"], "terminalCursor.foreground": c["vermilion"],
        "button.background": c["lacquer"], "button.foreground": c["paper_hi"], "button.hoverBackground": c["crimson"],
        "badge.background": c["lacquer"], "badge.foreground": c["paper_hi"],
        "input.background": c["ash"], "input.border": c["stone"], "inputOption.activeBorder": c["lacquer"],
        "dropdown.background": c["ash"], "quickInput.background": c["ash"],
        "progressBar.background": c["lacquer"], "textLink.foreground": c["sky"],
        "scrollbarSlider.background": c["stone"] + "99", "scrollbarSlider.hoverBackground": c["slate"],
        "scrollbarSlider.activeBackground": c["blood"], "gitDecoration.modifiedResourceForeground": c["gold"],
        "gitDecoration.untrackedResourceForeground": c["moss"], "gitDecoration.deletedResourceForeground": c["crimson"],
        "editorWidget.background": c["ash"], "editorSuggestWidget.background": c["ash"],
        "editorSuggestWidget.selectedBackground": c["blood"], "peekView.border": c["lacquer"],
        "breadcrumb.foreground": c["smoke"], "breadcrumb.focusForeground": c["paper"],
    }
    names = ["Black", "Red", "Green", "Yellow", "Blue", "Magenta", "Cyan", "White"]
    from palette import ANSI
    for i, n in enumerate(names):
        ui[f"terminal.ansi{n}"] = ANSI[i]
        ui[f"terminal.ansiBright{n}"] = ANSI[i + 8]
    tok = {"textMateRules": [
        {"scope": ["comment", "punctuation.definition.comment"], "settings": {"foreground": c["smoke"], "fontStyle": "italic"}},
        {"scope": ["keyword", "storage.type", "storage.modifier", "keyword.control"], "settings": {"foreground": c["crimson"]}},
        {"scope": ["string", "string.quoted"], "settings": {"foreground": c["moss"]}},
        {"scope": ["constant.numeric", "constant.language", "constant"], "settings": {"foreground": c["ember"]}},
        {"scope": ["entity.name.function", "support.function", "meta.function-call"], "settings": {"foreground": c["gold_hi"]}},
        {"scope": ["entity.name.type", "entity.name.class", "support.type", "support.class"], "settings": {"foreground": c["sky"]}},
        {"scope": ["variable.parameter"], "settings": {"foreground": c["pampas"], "fontStyle": "italic"}},
        {"scope": ["variable.other.property", "variable.other.member", "support.type.property-name"], "settings": {"foreground": c["pampas"]}},
        {"scope": ["keyword.operator", "punctuation"], "settings": {"foreground": c["mist"]}},
        {"scope": ["entity.name.tag"], "settings": {"foreground": c["crimson"]}},
        {"scope": ["entity.other.attribute-name"], "settings": {"foreground": c["gold"], "fontStyle": "italic"}},
        {"scope": ["keyword.control.import", "keyword.control.from", "meta.import"], "settings": {"foreground": c["sakura"]}},
        {"scope": ["markup.heading"], "settings": {"foreground": c["vermilion"], "fontStyle": "bold"}},
    ]}
    settings = {
        "// generated": HDR,
        "workbench.colorTheme": "Default Dark Modern",
        "workbench.colorCustomizations": ui,
        "editor.tokenColorCustomizations": tok,
        "editor.fontFamily": "'JetBrainsMono Nerd Font', Menlo, monospace",
        "editor.fontLigatures": True,
        "editor.cursorStyle": "line",
        "editor.cursorBlinking": "smooth",
        "terminal.integrated.fontFamily": "'JetBrainsMono Nerd Font'",
    }
    write("vscode/settings.json", json.dumps(settings, indent=2, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    sketchybar()
    borders()
    vscode()

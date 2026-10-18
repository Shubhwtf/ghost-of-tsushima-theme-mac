#!/usr/bin/env bash
# 冥人 Ghost of Tsushima — macOS appearance
#
# usage: macos/defaults.sh [--extras] [--backup DIR]
#
#   (no option)  dark mode, red accent colour, red text highlight
#   --extras     also tidy the Dock and Finder (each tweak listed below)
#   --backup DIR where to write restore-defaults.sh (default ~/.got-backup-<timestamp>)
#
# Every value is read before it is changed and written to restore-defaults.sh,
# so running that script puts each setting back exactly as it was.
set -euo pipefail

if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "defaults.sh: not macOS, nothing to do"
  exit 0
fi

EXTRAS=0
BACKUP="$HOME/.got-backup-$(date +%Y%m%d-%H%M%S)"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --extras) EXTRAS=1 ;;
    --backup) BACKUP="$2"; shift ;;
    -h|--help) sed -n '2,12p' "$0"; exit 0 ;;
    *) echo "unknown option: $1" >&2; exit 1 ;;
  esac
  shift
done

mkdir -p "$BACKUP"
RESTORE="$BACKUP/restore-defaults.sh"
if [[ ! -f "$RESTORE" ]]; then
  printf '#!/usr/bin/env bash\n# Restores the macOS settings changed by the Ghost of Tsushima theme.\n' > "$RESTORE"
  chmod +x "$RESTORE"
fi

# set_default <domain> <key> <type> <value>
# Records the current value (or its absence) in restore-defaults.sh, then writes the new one.
set_default() {
  local domain="$1" key="$2" type="$3" value="$4" old
  if old="$(defaults read "$domain" "$key" 2>/dev/null)"; then
    printf 'defaults write %q %q %s %q\n' "$domain" "$key" "$type" "$old" >> "$RESTORE"
  else
    printf 'defaults delete %q %q 2>/dev/null || true\n' "$domain" "$key" >> "$RESTORE"
  fi
  defaults write "$domain" "$key" "$type" "$value"
}

red=$'\e[38;2;225;61;67m'; dim=$'\e[38;2;131;122;115m'; off=$'\e[0m'
say() { printf '%s◆%s %s\n' "$red" "$off" "$*"; }

# ---- appearance ----------------------------------------------------------------
say "Dark mode"
# AppleInterfaceStyle=Dark is what System Settings writes; System Events applies it live.
set_default -g AppleInterfaceStyle -string Dark
osascript -e 'tell application "System Events" to tell appearance preferences to set dark mode to true' >/dev/null 2>&1 || true

say "Accent colour: red"
# -1 graphite, 0 red, 1 orange, 2 yellow, 3 green, 4 blue (default = key absent), 5 purple, 6 pink
set_default -g AppleAccentColor -int 0

say "Text highlight colour: red"
set_default -g AppleHighlightColor -string "1.000000 0.733333 0.721569 Red"

# Sidebar icons follow the accent colour; medium size suits the bar font.
set_default -g NSTableViewDefaultSizeMode -int 2

if [[ $EXTRAS -eq 1 ]]; then
  say "Dock: auto-hide, no delay, no recent apps, scale effect"
  set_default com.apple.dock autohide -bool true
  set_default com.apple.dock autohide-delay -float 0
  set_default com.apple.dock autohide-time-modifier -float 0.4
  set_default com.apple.dock show-recents -bool false
  set_default com.apple.dock mineffect -string scale
  # SketchyBar draws its own bar: hide the menu bar unless the pointer is at the top
  set_default -g _HIHideMenuBar -bool true

  say "Finder: path bar, status bar, file extensions, folders first"
  set_default com.apple.finder ShowPathbar -bool true
  set_default com.apple.finder ShowStatusBar -bool true
  set_default -g AppleShowAllExtensions -bool true
  set_default com.apple.finder _FXSortFoldersFirst -bool true
  printf 'killall Dock Finder SystemUIServer 2>/dev/null || true\n' >> "$RESTORE"
  killall Dock Finder 2>/dev/null || true
fi

printf 'echo "macOS settings restored. Log out and back in if colours look stale."\n' >> "$RESTORE"
say "Done. To undo: ${RESTORE}"
printf '  %sSome apps pick up the accent colour after they restart.%s\n' "$dim" "$off"

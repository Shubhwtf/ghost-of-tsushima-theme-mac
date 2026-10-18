#!/usr/bin/env bash
# 冥人 Ghost of Tsushima — uninstaller
#
# usage: ./uninstall.sh [--keep-defaults]
#
# Moves every file the installer put down into ~/.got-removed-<timestamp>,
# restores the configs you had before from the oldest ~/.got-backup-*,
# removes the theme's lines from ~/.zshrc and, on macOS, puts the appearance
# settings back with restore-defaults.sh. Nothing is deleted.
set -euo pipefail

CONF="${XDG_CONFIG_HOME:-$HOME/.config}"
STATE="$CONF/ghost-of-tsushima"
MANIFEST="$STATE/installed.txt"
OUT="$HOME/.got-removed-$(date +%Y%m%d-%H%M%S)"
KEEP_DEFAULTS=0
[[ "${1:-}" == "--keep-defaults" ]] && KEEP_DEFAULTS=1
[[ "${1:-}" == "-h" || "${1:-}" == "--help" ]] && { sed -n '2,10p' "$0"; exit 0; }

red=$'\e[38;2;226;61;67m'; off=$'\e[0m'
[[ -t 1 ]] || { red=""; off=""; }
say() { printf '%s◆%s %s\n' "$red" "$off" "$*"; }

# stash <path>: move one installed path out of the way, mirroring it under $OUT
stash() {
    local p="$1" rel
    [[ -e "$p" || -L "$p" ]] || return 0
    rel="${p#"$HOME"/}"
    mkdir -p "$OUT/$(dirname "$rel")"
    mv "$p" "$OUT/$rel"
}

# the oldest backup holds the configs from before the first install
FIRST_BK=""
if [[ -f "$STATE/backups.txt" ]]; then
    FIRST_BK="$(head -n1 "$STATE/backups.txt")"
fi

if [[ -f "$MANIFEST" ]]; then
    say "Removing theme files (moved to $OUT)"
    while IFS= read -r p; do
        [[ -n "$p" ]] && stash "$p"
    done < "$MANIFEST"
fi

if [[ -n "$FIRST_BK" && -d "$FIRST_BK" ]]; then
    say "Restoring your previous configs from $FIRST_BK"
    (cd "$FIRST_BK" && find . -mindepth 1 \( -type f -o -type l \) ! -path './.replaced-*' ! -name 'restore-defaults.sh' -print) |
    while IFS= read -r f; do
        f="${f#./}"
        case "$f" in .replaced-*) continue ;; esac
        mkdir -p "$HOME/$(dirname "$f")"
        [[ -e "$HOME/$f" ]] && stash "$HOME/$f"
        cp -a "$FIRST_BK/$f" "$HOME/$f"
    done
fi

if [[ -f "$HOME/.zshrc" ]] && grep -q '# ghost-of-tsushima' "$HOME/.zshrc"; then
    say "Removing the theme lines from ~/.zshrc"
    mkdir -p "$OUT"
    cp "$HOME/.zshrc" "$OUT/zshrc.before-uninstall"
    grep -v '# ghost-of-tsushima' "$OUT/zshrc.before-uninstall" > "$HOME/.zshrc" || true
fi

if [[ "$(uname -s)" == "Darwin" ]]; then
    if [[ "$(defaults read com.apple.Terminal 'Default Window Settings' 2>/dev/null || true)" == "Ghost of Tsushima" ]]; then
        defaults write com.apple.Terminal "Default Window Settings" -string "Basic"
        defaults write com.apple.Terminal "Startup Window Settings" -string "Basic"
        say "Terminal.app is back on the Basic profile"
    fi
    if command -v brew >/dev/null 2>&1; then
        [[ -d "$CONF/sketchybar" ]] || brew services stop sketchybar >/dev/null 2>&1 || true
        [[ -f "$CONF/borders/bordersrc" ]] || brew services stop borders >/dev/null 2>&1 || true
    fi
    if [[ $KEEP_DEFAULTS -eq 0 && -f "$STATE/backups.txt" ]]; then
        # replay every restore script, newest first, so the oldest values win
        tail -r "$STATE/backups.txt" 2>/dev/null | while IFS= read -r b; do
            [[ -x "$b/restore-defaults.sh" ]] && bash "$b/restore-defaults.sh"
        done
    fi
fi

[[ -d "$STATE" ]] && stash "$STATE"
say "Uninstalled. Your backups in ~/.got-backup-* are untouched."

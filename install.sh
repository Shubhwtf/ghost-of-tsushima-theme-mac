#!/usr/bin/env bash
# 冥人 Ghost of Tsushima theme for macOS — installer
# https://github.com/Shubhwtf/ghost-of-tsushima-theme-mac
#
# Every file it touches is backed up to ~/.got-backup-<timestamp> first.
# Existing configs are moved into that backup, never deleted.
# On Linux only the cross-platform parts (terminals, shell, Neovim) are installed.
set -euo pipefail

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONF="${XDG_CONFIG_HOME:-$HOME/.config}"
STAMP="$(date +%Y%m%d-%H%M%S)"
BK="$HOME/.got-backup-$STAMP"
STATE="$CONF/ghost-of-tsushima"
MANIFEST="$STATE/installed.txt"
OS="$(uname -s)"
VARIANT="red"

red=$'\e[38;2;226;61;67m'; gold=$'\e[38;2;201;164;92m'; dim=$'\e[38;2;131;122;115m'; off=$'\e[0m'
if [[ ! -t 1 || -n "${NO_COLOR:-}" ]]; then red=""; gold=""; dim=""; off=""; fi
say()  { printf '%s◆%s %s\n' "$red" "$off" "$*"; }
note() { printf '  %s%s%s\n' "$dim" "$*" "$off"; }
is_mac() { [[ "$OS" == "Darwin" ]]; }
have() { command -v "$1" >/dev/null 2>&1; }

usage() {
    cat <<EOF
${red}冥人${off} ${gold}GHOST OF TSUSHIMA${off} for macOS

usage: ./install.sh [options]

  --variant V        red (default) or kurosawa, the black-and-white mode; re-run with
                     the other one to switch (your backups are kept)
  --all              terminals, shell, Neovim and the desktop layer
  --terminal         Terminal.app, iTerm2, Ghostty, kitty, Alacritty, WezTerm,
                     btop, bat, delta, lazygit and fastfetch themes
  --shell            starship prompt, zsh highlighting, fzf and eza colours
  --nvim             the full Neovim config with the ensō dashboard
  --desktop          SketchyBar, JankyBorders and macOS appearance (dark mode, red accent)
  --extras           with --desktop: also tidy the Dock and Finder (see macos/defaults.sh)
  --brew             install the tools with Homebrew (sketchybar, borders, starship, ...)
  --wallpaper NAME   render or fetch a wallpaper and set it as the desktop:
                     an original (Higanbana, ToriiAtDawn, Standoff, Kurosawa,
                     GuidingWind, GuidingWindPaper), a number from
                     scripts/wallpapers.py --list, or a path to an image
  -h, --help         show this help

examples:
  ./install.sh --brew --all --wallpaper Higanbana
  ./install.sh --terminal --shell
  ./install.sh --variant kurosawa --all --wallpaper Kurosawa
EOF
}

DO_TERM=0; DO_SHELL=0; DO_NVIM=0; DO_DESK=0; DO_BREW=0; EXTRAS=0; WALL=""
[[ $# -eq 0 ]] && { usage; exit 0; }
while [[ $# -gt 0 ]]; do
    case "$1" in
        --all) DO_TERM=1; DO_SHELL=1; DO_NVIM=1; DO_DESK=1 ;;
        --terminal) DO_TERM=1 ;;
        --shell) DO_SHELL=1 ;;
        --nvim) DO_NVIM=1 ;;
        --desktop) DO_DESK=1 ;;
        --extras) EXTRAS=1 ;;
        --variant) [[ $# -ge 2 ]] || { echo "--variant needs red or kurosawa" >&2; exit 1; }; VARIANT="$2"; shift ;;
        --brew) DO_BREW=1 ;;
        --wallpaper) [[ $# -ge 2 ]] || { echo "--wallpaper needs a name" >&2; exit 1; }; WALL="$2"; shift ;;
        -h|--help) usage; exit 0 ;;
        *) echo "unknown option: $1" >&2; usage; exit 1 ;;
    esac
    shift
done

case "$VARIANT" in
    red) NAME="Ghost of Tsushima"; SLUG="ghost-of-tsushima"; SFX="" ;;
    kurosawa) NAME="Ghost of Tsushima Kurosawa"; SLUG="ghost-of-tsushima-kurosawa"; SFX="-kurosawa" ;;
    *) echo "unknown variant: $VARIANT (use red or kurosawa)" >&2; exit 1 ;;
esac

# ------------------------------------------------------------------ helpers
mkdir -p "$STATE"
touch "$MANIFEST"

# backup <path>: copy an existing file/dir into the backup, mirroring its path under $HOME
backup() {
    local p="$1" rel
    [[ -e "$p" || -L "$p" ]] || return 0
    rel="${p#"$HOME"/}"
    mkdir -p "$BK/$(dirname "$rel")"
    [[ -e "$BK/$rel" ]] || cp -a "$p" "$BK/$rel"
}

# put <src> <dest>: back up dest, then install src there (files or directories)
put() {
    local src="$1" dest="$2"
    backup "$dest"
    mkdir -p "$(dirname "$dest")"
    if [[ -d "$src" ]]; then
        if [[ -e "$dest" ]]; then
            # move the old directory aside (it is already in the backup) instead of deleting it
            mv "$dest" "$BK/.replaced-$(basename "$dest")-$$"
        fi
        cp -R "$src" "$dest"
    else
        cp "$src" "$dest"
    fi
    grep -qxF "$dest" "$MANIFEST" 2>/dev/null || printf '%s\n' "$dest" >> "$MANIFEST"
}

# ours <path>: true when the installer put this file there (so switching variants may replace it)
ours() { grep -qxF "$1" "$MANIFEST" 2>/dev/null; }

# put_if_absent <src> <dest>: install only when the user has no file of their own there
put_if_absent() {
    if [[ -e "$2" ]] && ! ours "$2"; then
        note "kept your $(basename "$2"); theme file installed next to it"
        return 1
    fi
    put "$1" "$2"
}

# set_kv <file> <key> <line>: replace the line that starts with key, or append it
set_kv() {
    local file="$1" key="$2" line="$3" tmp
    backup "$file"
    tmp="$(mktemp)"
    if grep -q "^${key}" "$file" 2>/dev/null; then
        awk -v k="$key" -v l="$line" 'index($0, k) == 1 { print l; next } { print }' "$file" > "$tmp"
    else
        { cat "$file" 2>/dev/null || true; printf '%s\n' "$line"; } > "$tmp"
    fi
    cat "$tmp" > "$file"
    rm -f "$tmp"
}

# ------------------------------------------------------------------ brew
install_brew() {
    if ! is_mac; then note "--brew is for macOS; install the tools with your package manager"; return; fi
    if ! have brew; then
        say "Homebrew is not installed"
        # shellcheck disable=SC2016
        note '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
        return
    fi
    say "Homebrew: taps and formulae"
    brew tap FelixKratz/formulae
    brew install sketchybar borders starship fastfetch btop bat git-delta eza fzf lazygit neovim \
                 tree-sitter zsh-syntax-highlighting zsh-autosuggestions librsvg ripgrep fd || true
    say "Homebrew: fonts and Ghostty"
    brew install --cask font-jetbrains-mono-nerd-font ghostty || true
    note "optional: pip3 install numpy pillow   (to render the original wallpapers yourself)"
}

# ------------------------------------------------------------------ terminals
install_terminal() {
    if is_mac; then
        say "Terminal.app profile"
        local prof="$SRC/terminal/terminal-app/$NAME.terminal"
        backup "$HOME/Library/Preferences/com.apple.Terminal.plist"
        open "$prof"           # imports the profile (Terminal opens one themed window)
        sleep 2
        defaults write com.apple.Terminal "Default Window Settings" -string "$NAME"
        defaults write com.apple.Terminal "Startup Window Settings" -string "$NAME"
        note "new Terminal windows now use '$NAME'"

        say "iTerm2 dynamic profile"
        put "$SRC/terminal/iterm2/$SLUG.json" "$HOME/Library/Application Support/iTerm2/DynamicProfiles/$SLUG.json"
        note "iTerm2 › Settings › Profiles › '$NAME' › Other Actions › Set as Default"
    else
        note "skipping Terminal.app and iTerm2 (macOS only)"
    fi

    say "Ghostty"
    put "$SRC/terminal/ghostty/$SLUG" "$CONF/ghostty/themes/$SLUG"
    put "$SRC/dotfiles/ghostty/config$SFX" "$CONF/ghostty/config"

    say "kitty"
    put "$SRC/terminal/kitty/$SLUG.conf" "$CONF/kitty/themes/$SLUG.conf"
    put "$SRC/dotfiles/kitty/kitty$SFX.conf" "$CONF/kitty/kitty.conf"
    pkill -USR1 -x kitty 2>/dev/null || true

    say "Alacritty"
    put "$SRC/terminal/alacritty/$SLUG.toml" "$CONF/alacritty/themes/$SLUG.toml"
    put_if_absent "$SRC/terminal/alacritty/alacritty$SFX.toml" "$CONF/alacritty/alacritty.toml" ||
        note "add to alacritty.toml:  [general] import = [\"~/.config/alacritty/themes/$SLUG.toml\"]"

    say "WezTerm"
    put "$SRC/terminal/wezterm/wezterm$SFX.lua" "$CONF/wezterm/$SLUG.lua"
    if { [[ ! -e "$CONF/wezterm/wezterm.lua" ]] || ours "$CONF/wezterm/wezterm.lua"; } && [[ ! -e "$HOME/.wezterm.lua" ]]; then
        put "$SRC/terminal/wezterm/wezterm$SFX.lua" "$CONF/wezterm/wezterm.lua"
    else
        note "your wezterm config is untouched; the full theme config is in $CONF/wezterm/$SLUG.lua"
    fi

    say "btop"
    put "$SRC/terminal/btop/$SLUG.theme" "$CONF/btop/themes/$SLUG.theme"
    if [[ -f "$CONF/btop/btop.conf" ]]; then
        set_kv "$CONF/btop/btop.conf" "color_theme" "color_theme = \"$SLUG\""
    else
        mkdir -p "$CONF/btop"
        printf 'color_theme = "%s"\ntheme_background = True\n' "$SLUG" > "$CONF/btop/btop.conf"
        printf '%s\n' "$CONF/btop/btop.conf" >> "$MANIFEST"
    fi

    say "bat and delta"
    put "$SRC/terminal/bat/$SLUG.tmTheme" "$CONF/bat/themes/$SLUG.tmTheme"
    if have bat; then bat cache --build >/dev/null 2>&1 || true; fi
    put "$SRC/terminal/delta/$SLUG.gitconfig" "$CONF/delta/$SLUG.gitconfig"
    if have delta && have git; then
        backup "$HOME/.gitconfig"
        if ! git config --global --get-all include.path 2>/dev/null | grep -q "$SLUG.gitconfig"; then
            git config --global --add include.path "$CONF/delta/$SLUG.gitconfig"
        fi
        git config --global delta.features "$SLUG"
        note "delta uses the theme (core.pager is left as you had it)"
    fi

    say "lazygit"
    local lg="$CONF/lazygit"
    is_mac && lg="$HOME/Library/Application Support/lazygit"
    put_if_absent "$SRC/terminal/lazygit/config$SFX.yml" "$lg/config.yml" ||
        put "$SRC/terminal/lazygit/config$SFX.yml" "$lg/$SLUG.yml"

    say "fastfetch"
    put "$SRC/terminal/fastfetch/config$SFX.jsonc" "$CONF/fastfetch/config.jsonc"
    put "$SRC/terminal/fastfetch/ghost$SFX.ansi" "$CONF/fastfetch/ghost$SFX.ansi"
}

# ------------------------------------------------------------------ shell
install_shell() {
    say "starship prompt"
    put "$SRC/shell/starship$SFX.toml" "$CONF/starship.toml"

    say "zsh colours (syntax highlighting, autosuggestions, fzf, eza, bat)"
    put "$SRC/shell/$SLUG.zsh" "$STATE/$SLUG.zsh"
    local rc="$HOME/.zshrc" line="source \"$STATE/$SLUG.zsh\"  # ghost-of-tsushima"
    backup "$rc"
    touch "$rc"
    if grep -q '^source ".*\.zsh"  # ghost-of-tsushima$' "$rc"; then
        # switching variants: swap the one theme line, keep everything else
        local tmp
        tmp="$(mktemp)"
        awk -v l="$line" '/^source ".*\.zsh"  # ghost-of-tsushima$/ { print l; next } { print }' "$rc" > "$tmp"
        cat "$tmp" > "$rc"
        rm -f "$tmp"
        note "your .zshrc now sources the $VARIANT theme"
    elif ! grep -q '# ghost-of-tsushima' "$rc"; then
        if is_mac && have brew; then
            local bp
            bp="$(brew --prefix)"
            {
                printf '\n# ghost-of-tsushima: plugins (if installed)\n'
                printf '[ -f "%s/share/zsh-autosuggestions/zsh-autosuggestions.zsh" ] && source "%s/share/zsh-autosuggestions/zsh-autosuggestions.zsh"  # ghost-of-tsushima\n' "$bp" "$bp"
                printf '[ -f "%s/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh" ] && source "%s/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh"  # ghost-of-tsushima\n' "$bp" "$bp"
            } >> "$rc"
        fi
        printf '%s\n' "$line" >> "$rc"
        note "added one source line to ~/.zshrc (open a new shell to see it)"
    else
        printf '%s\n' "$line" >> "$rc"
    fi
}

# ------------------------------------------------------------------ nvim
install_nvim() {
    say "Neovim config"
    put "$SRC/dotfiles/nvim" "$CONF/nvim"
    local init="$CONF/nvim/init.lua" tmp
    tmp="$(mktemp)"
    awk -v v="$VARIANT" '/^vim.g.got_variant = / { print "vim.g.got_variant = vim.g.got_variant or \"" v "\""; next } { print }' "$init" > "$tmp"
    cat "$tmp" > "$init"
    rm -f "$tmp"
    note "colorscheme: $SLUG"
    have tree-sitter || note "install the tree-sitter CLI so nvim-treesitter can build parsers (brew install tree-sitter)"
    note "open nvim once; lazy.nvim installs the plugins"
}

# ------------------------------------------------------------------ desktop
install_desktop() {
    if ! is_mac; then note "skipping SketchyBar, borders and macOS defaults (macOS only)"; return; fi
    say "SketchyBar"
    put "$SRC/sketchybar" "$CONF/sketchybar"
    cp "$SRC/sketchybar/colors$SFX.sh" "$CONF/sketchybar/colors.sh"
    cp "$SRC/sketchybar/icons/enso$SFX.png" "$CONF/sketchybar/icons/enso.png"
    chmod +x "$CONF/sketchybar/sketchybarrc" "$CONF/sketchybar/colors.sh" "$CONF/sketchybar/plugins/"*.sh
    if have brew && have sketchybar; then
        brew services restart sketchybar >/dev/null 2>&1 || sketchybar --reload || true
    else
        note "brew install FelixKratz/formulae/sketchybar  (or ./install.sh --brew)"
    fi

    say "JankyBorders"
    put "$SRC/borders/bordersrc$SFX" "$CONF/borders/bordersrc"
    chmod +x "$CONF/borders/bordersrc"
    if have brew && have borders; then
        brew services restart borders >/dev/null 2>&1 || true
    else
        note "brew install FelixKratz/formulae/borders  (or ./install.sh --brew)"
    fi

    say "macOS appearance"
    local args=(--backup "$BK")
    [[ $EXTRAS -eq 1 ]] && args+=(--extras)
    bash "$SRC/macos/defaults.sh" "${args[@]}"
}

# ------------------------------------------------------------------ wallpaper
install_wallpaper() {
    local name="$1" picker="$SRC/scripts/wallpapers.py"
    have python3 || { say "--wallpaper needs python3"; return; }
    case "$(printf '%s' "$name" | tr '[:upper:]' '[:lower:]')" in
        higanbana|toriiatdawn|standoff|kurosawa|guidingwind|guidingwindpaper|*-bw)
            python3 "$picker" --variant "$VARIANT" --originals "$name" --set-first ;;
        *)
            if [[ -f "$name" ]]; then
                python3 "$picker" --set "$name"
            elif [[ "$name" =~ ^[0-9,\ -]+$ ]]; then
                python3 "$picker" --get "$name" --set-first
            else
                say "unknown wallpaper '$name'; see: python3 scripts/wallpapers.py --list"
            fi ;;
    esac
}

# ------------------------------------------------------------------ run
if [[ "$VARIANT" == kurosawa ]]; then red=$'\e[38;2;245;245;245m'; gold=$'\e[38;2;184;184;184m'; fi
[[ ! -t 1 || -n "${NO_COLOR:-}" ]] && { red=""; gold=""; }
printf '\n%s冥人%s  %sGHOST OF TSUSHIMA%s  %s\n\n' "$red" "$off" "$gold" "$off" "$([[ $VARIANT == kurosawa ]] && echo '· KUROSAWA MODE')"
[[ $DO_BREW -eq 1 ]] && install_brew
[[ $DO_TERM -eq 1 ]] && install_terminal
[[ $DO_SHELL -eq 1 ]] && install_shell
[[ $DO_NVIM -eq 1 ]] && install_nvim
[[ $DO_DESK -eq 1 ]] && install_desktop
[[ -n "$WALL" ]] && install_wallpaper "$WALL"

printf '%s\n' "$VARIANT" > "$STATE/variant"
if [[ -d "$BK" ]]; then
    printf '%s\n' "$BK" >> "$STATE/backups.txt"
    say "Your previous configs are in $BK"
fi
say "Done. The wind will guide you."

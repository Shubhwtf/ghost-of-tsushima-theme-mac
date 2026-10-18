#!/usr/bin/env python3
"""Generate the shell layer from palette.json: starship prompt, zsh colours
(syntax highlighting, autosuggestions, fzf, eza, bat) and fastfetch.

usage: shell.py [ROOT]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from palette import C, MONO, NAME, ROLE, SLUG, SUFFIX, rgb  # noqa: E402
import halfblock  # noqa: E402

ROOT = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HEADER = f"{NAME} — generated from palette.json by src/shell.py"


def write(rel, text):
    path = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(text)
    print("wrote", rel)


# Nerd Font glyphs as TOML escapes (never raw private-use characters)
G = {
    "round_l": r"", "round_r": r"", "slant": r"", "slant_l": r"",
    "branch": r"", "lock": r"", "clock": r"", "timer": r"",
    "node": r"", "python": r"", "rust": r"", "go": r"", "lua": r"",
    "bun": r"", "docker": r"", "katana": r"\U000f04e5", "home": r"",
    "folder": r"", "code": r"", "apple": r"",
}


def starship():
    if MONO:   # no hue to tell success from failure: change the glyph and the weight instead
        CHAR = (f'success_symbol = "[{G["katana"]} ❯](fg:mist)"\n'
                f'error_symbol = "[{G["katana"]} ✗](bold fg:paper_hi)"\n'
                f'vimcmd_symbol = "[{G["katana"]} ❮](bold fg:rice)"')
    else:
        CHAR = (f'success_symbol = "[{G["katana"]} ❯](bold fg:crimson)"\n'
                f'error_symbol = "[{G["katana"]} ❯](bold fg:gold)"\n'
                f'vimcmd_symbol = "[{G["katana"]} ❮](bold fg:moss)"')
    pal = "\n".join(f'{k} = "{v}"' for k, v in C.items())
    t = f"""# {HEADER}
# 冥人 — ink, lacquer and gold leaf. Needs a Nerd Font.
"$schema" = "https://starship.rs/config-schema.json"

palette = "{SLUG.replace('-', '_')}"
add_newline = true
command_timeout = 800

format = \"\"\"
[{G['round_l']}](fg:lacquer)\\
[ 冥 ](bold fg:paper_hi bg:lacquer)\\
[{G['slant']}](fg:lacquer bg:blood)\\
$directory\\
[{G['slant']}](fg:blood bg:stone)\\
$git_branch\\
$git_status\\
[{G['slant']}](fg:stone bg:ash)\\
$nodejs$python$rust$golang$lua$bun$docker_context\\
[{G['slant']}](fg:ash)\\
$fill\\
$cmd_duration\\
$time
$character\"\"\"

[palettes.{SLUG.replace('-', '_')}]
{pal}

[directory]
style = "bold fg:paper_hi bg:blood"
format = "[ $path ]($style)[$read_only]($read_only_style)"
read_only = "{G['lock']} "
read_only_style = "fg:gold_hi bg:blood"
truncation_length = 3
truncation_symbol = "…/"
home_symbol = "{G['home']} ~"

[directory.substitutions]
"Documents" = "{G['folder']} Documents"
"Developer" = "{G['code']} Developer"
"Projects" = "{G['code']} Projects"

[git_branch]
symbol = "{G['branch']}"
style = "bg:stone"
format = "[[ $symbol $branch ](fg:gold_hi bg:stone)]($style)"

[git_status]
style = "bg:stone"
format = "[[($all_status$ahead_behind )](fg:blossom bg:stone)]($style)"
conflicted = "⚔"
ahead = "⇡${{count}}"
behind = "⇣${{count}}"
diverged = "⇕"
modified = "~"
staged = "+"
untracked = "?"
deleted = "✗"
stashed = "≡"

[nodejs]
symbol = "{G['node']}"
style = "bg:ash"
format = "[[ $symbol( $version) ](fg:moss bg:ash)]($style)"

[python]
symbol = "{G['python']}"
style = "bg:ash"
format = "[[ $symbol( $version)( \\\\($virtualenv\\\\)) ](fg:sky bg:ash)]($style)"

[rust]
symbol = "{G['rust']}"
style = "bg:ash"
format = "[[ $symbol( $version) ](fg:ember bg:ash)]($style)"

[golang]
symbol = "{G['go']}"
style = "bg:ash"
format = "[[ $symbol( $version) ](fg:jade bg:ash)]($style)"

[lua]
symbol = "{G['lua']}"
style = "bg:ash"
format = "[[ $symbol( $version) ](fg:sky bg:ash)]($style)"

[bun]
symbol = "{G['bun']}"
style = "bg:ash"
format = "[[ $symbol( $version) ](fg:pampas bg:ash)]($style)"

[docker_context]
symbol = "{G['docker']}"
style = "bg:ash"
format = "[[ $symbol( $context) ](fg:sky bg:ash)]($style)"

[fill]
symbol = " "

[cmd_duration]
min_time = 1500
format = "[{G['timer']} $duration ](fg:gold)"

[time]
disabled = false
time_format = "%H:%M"
format = "[{G['round_l']}](fg:ash)[ {G['clock']} $time ](fg:mist bg:ash)[{G['round_r']}](fg:ash)"

[character]
{CHAR}

[username]
show_always = false
style_user = "fg:pampas"
format = "[$user ]($style)"

[hostname]
ssh_only = true
format = "[@$hostname ](fg:pampas)"
"""
    write(f"shell/starship{SUFFIX}.toml", t)


def ansi_fg(h):
    r, g, b = rgb(h)
    return f"38;2;{r};{g};{b}"


def zsh():
    fzf = ",".join([
        f"bg+:{C['stone']}", f"bg:{ROLE['background']}", f"spinner:{C['vermilion']}", f"hl:{C['crimson']}",
        f"fg:{C['rice']}", f"header:{C['gold']}", f"info:{C['gold']}", f"pointer:{C['vermilion']}",
        f"marker:{C['vermilion']}", f"fg+:{C['paper_hi']}", f"prompt:{C['crimson']}", f"hl+:{C['vermilion']}",
        f"border:{C['slate']}", f"gutter:{ROLE['background']}", f"query:{C['paper']}", f"label:{C['gold']}",
        f"preview-bg:{C['ink']}", f"separator:{C['stone']}", f"scrollbar:{C['lacquer']}"])
    eza = ":".join([
        "reset",
        f"di={ansi_fg(C['sky'])};1", f"ex={ansi_fg(C['crimson'])};1", f"fi={ansi_fg(C['paper'])}",
        f"ln={ansi_fg(C['jade'])}", f"or={ansi_fg(C['vermilion'])};4", f"so={ansi_fg(C['sakura'])}",
        f"pi={ansi_fg(C['gold'])}", f"bd={ansi_fg(C['gold'])};1", f"cd={ansi_fg(C['gold'])}",
        f"ur={ansi_fg(C['gold'])}", f"uw={ansi_fg(C['crimson'])}", f"ux={ansi_fg(C['moss'])}", f"ue={ansi_fg(C['moss'])};1",
        f"gr={ansi_fg(C['gold'])}", f"gw={ansi_fg(C['crimson'])}", f"gx={ansi_fg(C['moss'])}",
        f"tr={ansi_fg(C['gold'])}", f"tw={ansi_fg(C['crimson'])}", f"tx={ansi_fg(C['moss'])}",
        f"su={ansi_fg(C['vermilion'])};1", f"sf={ansi_fg(C['vermilion'])}", f"xa={ansi_fg(C['smoke'])}",
        f"sn={ansi_fg(C['pampas'])}", f"sb={ansi_fg(C['smoke'])}", f"df={ansi_fg(C['pampas'])}", f"ds={ansi_fg(C['smoke'])}",
        f"uu={ansi_fg(C['mist'])}", f"un={ansi_fg(C['vermilion'])}", f"gu={ansi_fg(C['mist'])}", f"gn={ansi_fg(C['vermilion'])}",
        f"da={ansi_fg(C['smoke'])}", f"in={ansi_fg(C['smoke'])}", f"bl={ansi_fg(C['smoke'])}",
        f"hd={ansi_fg(C['gold'])};4", f"lp={ansi_fg(C['jade'])}", f"cc={ansi_fg(C['vermilion'])}",
        f"ga={ansi_fg(C['moss'])}{';1' if MONO else ''}", f"gm={ansi_fg(C['gold'])}", f"gd={ansi_fg(C['crimson'])}{';9' if MONO else ''}",
        f"gv={ansi_fg(C['sky'])}", f"gt={ansi_fg(C['sakura'])}", f"gi={ansi_fg(C['slate'])}",
        f"xx={ansi_fg(C['slate'])}", f"im={ansi_fg(C['sakura'])}", f"vi={ansi_fg(C['sakura'])}",
        f"mu={ansi_fg(C['sky'])}", f"co={ansi_fg(C['gold'])}", f"tm={ansi_fg(C['smoke'])}",
        f"bu={ansi_fg(C['gold_hi'])};4", f"sc={ansi_fg(C['moss'])}",
        f"*.md={ansi_fg(C['pampas'])}", f"*.lua={ansi_fg(C['sky'])}", f"*.json={ansi_fg(C['gold'])}",
        f"*.toml={ansi_fg(C['gold'])}"])
    t = f"""# {HEADER}
# 冥人 — source this from ~/.zshrc (the installer adds the line for you):
#   source ~/.config/ghost-of-tsushima/{SLUG}.zsh
# Load it AFTER zsh-syntax-highlighting / zsh-autosuggestions if you use them.

# ---- zsh-syntax-highlighting -------------------------------------------
typeset -gA ZSH_HIGHLIGHT_STYLES
ZSH_HIGHLIGHT_STYLES[default]='fg={C['paper']}'
ZSH_HIGHLIGHT_STYLES[unknown-token]='fg={C['crimson']},bold{',underline' if MONO else ''}'
ZSH_HIGHLIGHT_STYLES[reserved-word]='fg={C['crimson']}{',bold' if MONO else ''}'
ZSH_HIGHLIGHT_STYLES[alias]='fg={C['gold_hi']}'
ZSH_HIGHLIGHT_STYLES[suffix-alias]='fg={C['gold_hi']},underline'
ZSH_HIGHLIGHT_STYLES[global-alias]='fg={C['gold_hi']}'
ZSH_HIGHLIGHT_STYLES[builtin]='fg={C['gold']}'
ZSH_HIGHLIGHT_STYLES[function]='fg={C['gold_hi']}'
ZSH_HIGHLIGHT_STYLES[command]='fg={C['gold_hi']}'
ZSH_HIGHLIGHT_STYLES[precommand]='fg={C['sakura']},italic'
ZSH_HIGHLIGHT_STYLES[commandseparator]='fg={C['vermilion']}'
ZSH_HIGHLIGHT_STYLES[hashed-command]='fg={C['gold']}'
ZSH_HIGHLIGHT_STYLES[autodirectory]='fg={C['sky']},underline'
ZSH_HIGHLIGHT_STYLES[path]='fg={C['paper']},underline'
ZSH_HIGHLIGHT_STYLES[path_pathseparator]='fg={C['smoke']},underline'
ZSH_HIGHLIGHT_STYLES[path_prefix]='fg={C['paper']},underline'
ZSH_HIGHLIGHT_STYLES[globbing]='fg={C['sky']}'
ZSH_HIGHLIGHT_STYLES[history-expansion]='fg={C['sakura']}'
ZSH_HIGHLIGHT_STYLES[command-substitution-delimiter]='fg={C['mist']}'
ZSH_HIGHLIGHT_STYLES[process-substitution-delimiter]='fg={C['mist']}'
ZSH_HIGHLIGHT_STYLES[single-hyphen-option]='fg={C['sky']}'
ZSH_HIGHLIGHT_STYLES[double-hyphen-option]='fg={C['sky']}'
ZSH_HIGHLIGHT_STYLES[back-quoted-argument]='fg={C['jade']}'
ZSH_HIGHLIGHT_STYLES[single-quoted-argument]='fg={C['moss']}{',italic' if MONO else ''}'
ZSH_HIGHLIGHT_STYLES[double-quoted-argument]='fg={C['moss']}{',italic' if MONO else ''}'
ZSH_HIGHLIGHT_STYLES[dollar-quoted-argument]='fg={C['moss']}'
ZSH_HIGHLIGHT_STYLES[dollar-double-quoted-argument]='fg={C['jade']}'
ZSH_HIGHLIGHT_STYLES[back-double-quoted-argument]='fg={C['jade']}'
ZSH_HIGHLIGHT_STYLES[assign]='fg={C['pampas']}'
ZSH_HIGHLIGHT_STYLES[redirection]='fg={C['vermilion']}'
ZSH_HIGHLIGHT_STYLES[comment]='fg={C['smoke']},italic'
ZSH_HIGHLIGHT_STYLES[arg0]='fg={C['gold_hi']}'
ZSH_HIGHLIGHT_STYLES[bracket-error]='fg={C['crimson']},bold'
ZSH_HIGHLIGHT_STYLES[bracket-level-1]='fg={C['gold']}'
ZSH_HIGHLIGHT_STYLES[bracket-level-2]='fg={C['sakura']}'
ZSH_HIGHLIGHT_STYLES[bracket-level-3]='fg={C['sky']}'
ZSH_HIGHLIGHT_STYLES[cursor-matchingbracket]='fg={C['ink']},bg={C['gold']}'

# ---- zsh-autosuggestions -------------------------------------------------
ZSH_AUTOSUGGEST_HIGHLIGHT_STYLE='fg={C['suggest']}{',italic' if MONO else ''}'

# ---- fzf -------------------------------------------------------------------
export FZF_DEFAULT_OPTS="${{FZF_DEFAULT_OPTS:+$FZF_DEFAULT_OPTS }}--color={fzf} --border=rounded --prompt='❯ ' --pointer='◆' --marker='✓' --separator='─' --scrollbar='│' --info=inline-right"

# ---- eza ---------------------------------------------------------------------
export EZA_COLORS="{eza}"

# ---- bat / delta / less --------------------------------------------------------
export BAT_THEME="{NAME}"
export LESS_TERMCAP_md=$'\\e[1;{ansi_fg(C['crimson'])}m'
export LESS_TERMCAP_me=$'\\e[0m'
export LESS_TERMCAP_us=$'\\e[4;{ansi_fg(C['gold'])}m'
export LESS_TERMCAP_ue=$'\\e[0m'
export LESS_TERMCAP_so=$'\\e[{ansi_fg(C['paper_hi'])};48;2;{";".join(map(str, rgb(C['blood'])))}m'
export LESS_TERMCAP_se=$'\\e[0m'

# ---- BSD ls (macOS) and GNU ls ----------------------------------------------------
export CLICOLOR=1
export LSCOLORS="exfxcxdxbxegedabagacad"

# ---- prompt ----------------------------------------------------------------------
if [[ -z "$GOT_NO_STARSHIP" ]] && command -v starship >/dev/null 2>&1; then
  export STARSHIP_CONFIG="${{STARSHIP_CONFIG:-$HOME/.config/starship.toml}}"
  eval "$(starship init zsh)"
fi
"""
    write(f"shell/{SLUG}.zsh", t)


def fastfetch():
    write(f"terminal/fastfetch/ghost{SUFFIX}.ansi", halfblock.ansi(30))
    k = C["crimson"]
    t = f"""// {HEADER}
// ~/.config/fastfetch/config.jsonc
{{
  "$schema": "https://github.com/fastfetch-cli/fastfetch/raw/dev/doc/json_schema.json",
  "logo": {{
    "type": "file-raw",
    "source": "~/.config/fastfetch/ghost{SUFFIX}.ansi",
    "padding": {{ "top": 1, "left": 2, "right": 4 }}
  }},
  "display": {{
    "separator": "  ",
    "color": {{ "keys": "{k}", "title": "{C['paper_hi']}", "output": "{C['paper']}", "separator": "{C['slate']}" }},
    "key": {{ "width": 12 }},
    "bar": {{ "char": {{ "elapsed": "━", "total": "━" }}, "color": {{ "elapsed": "{C['lacquer']}", "total": "{C['stone']}" }} }},
    "percent": {{ "type": ["bar", "num"], "color": {{ "green": "{C['moss']}", "yellow": "{C['gold']}", "red": "{C['crimson']}" }} }}
  }},
  "modules": [
    {{ "type": "custom", "format": "{{#1;38;2;{";".join(map(str, rgb(C['crimson'])))}}}冥人  {{#0;38;2;{";".join(map(str, rgb(C['paper_hi'])))}}}GHOST OF TSUSHIMA" }},
    {{ "type": "custom", "format": "{{#38;2;{";".join(map(str, rgb(C['slate'])))}}}──────────────────────────────" }},
    {{ "type": "title", "key": "\\uf007 user", "format": "{{user-name}}{{#38;2;{";".join(map(str, rgb(C['smoke'])))}}}@{{#}}{{host-name}}" }},
    {{ "type": "os", "key": "\\uf179 os" }},
    {{ "type": "host", "key": "\\uf109 host" }},
    {{ "type": "kernel", "key": "\\uf013 kernel" }},
    {{ "type": "uptime", "key": "\\uf017 uptime" }},
    {{ "type": "packages", "key": "\\uf487 pkgs" }},
    {{ "type": "shell", "key": "\\uf120 shell" }},
    {{ "type": "terminal", "key": "\\ue795 term" }},
    {{ "type": "terminalfont", "key": "\\uf031 font" }},
    {{ "type": "cpu", "key": "\\uf2db cpu", "showPeCoreCount": true }},
    {{ "type": "gpu", "key": "\\uf26c gpu" }},
    {{ "type": "memory", "key": "\\uefc5 memory" }},
    {{ "type": "disk", "key": "\\uf0a0 disk", "folders": "/" }},
    {{ "type": "battery", "key": "\\uf240 battery" }},
    "break",
    {{ "type": "colors", "symbol": "circle", "paddingLeft": 2 }}
  ]
}}
"""
    write(f"terminal/fastfetch/config{SUFFIX}.jsonc", t)


if __name__ == "__main__":
    starship()
    zsh()
    fastfetch()

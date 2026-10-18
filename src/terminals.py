#!/usr/bin/env python3
"""Generate every terminal theme from palette.json.

usage: [GOT_VARIANT=kurosawa] terminals.py [ROOT]   (writes into ROOT/terminal/...)
"""
import json
import os
import plistlib
import sys
import uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from palette import ANSI, C, MONO, NAME, ROLE, SLUG, SUFFIX, rgbf  # noqa: E402

ROOT = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T = os.path.join(ROOT, "terminal")
HEADER = f"{NAME} — generated from palette.json by src/terminals.py"

BG, FG = ROLE["background"], ROLE["foreground"]
SEL_BG, SEL_FG = ROLE["selection_bg"], ROLE["selection_fg"]
CUR, CUR_TXT = ROLE["cursor"], ROLE["cursor_text"]
ANSI_KEYS = ["Black", "Red", "Green", "Yellow", "Blue", "Magenta", "Cyan", "White"]


def write(rel, text, mode="w"):
    path = os.path.join(T, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, mode) as f:
        f.write(text)
    return path


# ------------------------------------------------------------------ Terminal.app
def nscolor(hexc):
    """NSKeyedArchiver blob for an NSColor in calibrated RGB (NSColorSpace 1)."""
    r, g, b = rgbf(hexc)
    archive = {
        "$archiver": "NSKeyedArchiver",
        "$objects": [
            "$null",
            {"$class": plistlib.UID(2), "NSColorSpace": 1, "NSRGB": f"{r:.10f} {g:.10f} {b:.10f}".encode() + b"\x00"},
            {"$classes": ["NSColor", "NSObject"], "$classname": "NSColor"},
        ],
        "$top": {"root": plistlib.UID(1)},
        "$version": 100000,
    }
    return plistlib.dumps(archive, fmt=plistlib.FMT_BINARY)


def nsfont(name, size):
    archive = {
        "$archiver": "NSKeyedArchiver",
        "$objects": [
            "$null",
            {"$class": plistlib.UID(3), "NSName": plistlib.UID(2), "NSSize": float(size), "NSfFlags": 16},
            name,
            {"$classes": ["NSFont", "NSObject"], "$classname": "NSFont"},
        ],
        "$top": {"root": plistlib.UID(1)},
        "$version": 100000,
    }
    return plistlib.dumps(archive, fmt=plistlib.FMT_BINARY)


def terminal_app():
    p = {
        "name": NAME,
        "type": "Window Settings",
        "ProfileCurrentVersion": 2.07,
        "BackgroundColor": nscolor(BG),
        "TextColor": nscolor(FG),
        "TextBoldColor": nscolor(C["paper_hi"]),
        "SelectionColor": nscolor(SEL_BG),
        "CursorColor": nscolor(CUR),
        "Font": nsfont("JetBrainsMonoNFM-Regular", 14),
        "FontAntialias": True,
        "FontWidthSpacing": 1.0,
        "FontHeightSpacing": 1.1,
        "UseBoldFonts": True,
        "UseBrightBold": False,
        "CursorType": 2,            # 0 block, 1 underline, 2 vertical bar
        "CursorBlink": True,
        "BackgroundBlur": 0.3,
        "BackgroundBlurInactive": 0.3,
        "BackgroundAlphaInactive": 0.92,
        "columnCount": 120,
        "rowCount": 34,
        "ShowActiveProcessInTitle": True,
        "ShowWindowSettingsNameInTitle": False,
        "ShowDimensionsInTitle": False,
        "useOptionAsMetaKey": True,
        "Bell": False,
        "VisualBell": False,
        "shellExitAction": 1,
    }
    for i, key in enumerate(ANSI_KEYS):
        p[f"ANSI{key}Color"] = nscolor(ANSI[i])
        p[f"ANSIBright{key}Color"] = nscolor(ANSI[i + 8])
    data = plistlib.dumps(p, fmt=plistlib.FMT_XML)
    path = write(f"terminal-app/{NAME}.terminal", data, "wb")
    # round-trip validation: the profile and every colour blob must decode
    back = plistlib.loads(open(path, "rb").read())
    assert back["name"] == NAME
    for k, v in back.items():
        if k.endswith("Color"):
            arch = plistlib.loads(v)
            obj = arch["$objects"][arch["$top"]["root"].data]
            assert obj["NSColorSpace"] == 1 and obj["NSRGB"].endswith(b"\x00"), k
    return path


# ------------------------------------------------------------------ iTerm2
def iterm_color(h, alpha=1.0):
    r, g, b = rgbf(h)
    return {"Alpha Component": alpha, "Blue Component": b, "Color Space": "sRGB",
            "Green Component": g, "Red Component": r}


def iterm_colors():
    d = {f"Ansi {i} Color": iterm_color(ANSI[i]) for i in range(16)}
    d.update({
        "Background Color": iterm_color(BG),
        "Foreground Color": iterm_color(FG),
        "Bold Color": iterm_color(C["paper_hi"]),
        "Cursor Color": iterm_color(CUR),
        "Cursor Text Color": iterm_color(CUR_TXT),
        "Cursor Guide Color": iterm_color(C["ash"], 0.6),
        "Selection Color": iterm_color(SEL_BG),
        "Selected Text Color": iterm_color(SEL_FG),
        "Link Color": iterm_color(C["sky"]),
        "Badge Color": iterm_color(C["lacquer"], 0.5),
        "Match Background Color": iterm_color(C["gold"]),
        "Tab Color": iterm_color(C["ink"]),
        "Underline Color": iterm_color(C["crimson"]),
    })
    return d


def iterm():
    cols = iterm_colors()
    p1 = write(f"iterm2/{NAME}.itermcolors", plistlib.dumps(cols, fmt=plistlib.FMT_XML), "wb")
    profile = {
        "Name": NAME,
        "Guid": str(uuid.uuid5(uuid.NAMESPACE_URL, "https://github.com/Shubhwtf/ghost-of-tsushima-theme-mac/" + SLUG)).upper(),
        "Badge Text": "",
        "Normal Font": "JetBrainsMonoNFM-Regular 14",
        "Non Ascii Font": "JetBrainsMonoNFM-Regular 14",
        "Use Non-ASCII Font": False,
        "ASCII Ligatures": True,
        "Use Bold Font": True,
        "Use Bright Bold": False,
        "Horizontal Spacing": 1.0,
        "Vertical Spacing": 1.1,
        "Columns": 120,
        "Rows": 34,
        "Side Margins": 14,
        "Top/Bottom Margins": 12,
        "Transparency": 0.04,
        "Blur": True,
        "Blur Radius": 14,
        "Cursor Type": 1,
        "Blinking Cursor": True,
        "Unlimited Scrollback": True,
        "Option Key Sends": 2,
        "Right Option Key Sends": 2,
        "Silence Bell": True,
        "Minimum Contrast": 0.0,
        "Tags": [SLUG],
    }
    profile.update(cols)
    p2 = write(f"iterm2/{SLUG}.json", json.dumps({"Profiles": [profile]}, indent=2) + "\n")
    return p1, p2


# ------------------------------------------------------------------ Ghostty
def ghostty():
    lines = [f"# {HEADER}"]
    lines += [f"palette = {i}={ANSI[i]}" for i in range(16)]
    lines += [f"background = {BG}", f"foreground = {FG}", f"cursor-color = {CUR}", f"cursor-text = {CUR_TXT}",
              f"selection-background = {SEL_BG}", f"selection-foreground = {SEL_FG}",
              f"split-divider-color = {C['slate']}", ""]
    return write(f"ghostty/{SLUG}", "\n".join(lines))


# ------------------------------------------------------------------ kitty
def kitty():
    t = f"""# vim:ft=kitty
# {HEADER}
# ink {C['ink']} · paper {C['paper']} · lacquer {C['lacquer']} · gold leaf {C['gold']}

background            {BG}
foreground            {FG}
selection_background  {SEL_BG}
selection_foreground  {SEL_FG}
url_color             {C['sky']}
cursor                {CUR}
cursor_text_color     {CUR_TXT}
cursor_trail_color    {C['lacquer']}

active_border_color   {ROLE['focus']}
inactive_border_color {C['slate']}
bell_border_color     {C['gold']}
visual_bell_color     {C['blood']}

wayland_titlebar_color {C['ink']}
macos_titlebar_color   {C['ink']}

active_tab_foreground   {C['paper_hi']}
active_tab_background   {C['lacquer']}
inactive_tab_foreground {C['mist']}
inactive_tab_background {C['ash']}
tab_bar_background      {C['ink']}
tab_bar_margin_color    {C['ink']}

mark1_foreground {C['ink']}
mark1_background {C['gold']}
mark2_foreground {C['ink']}
mark2_background {C['sky']}
mark3_foreground {C['paper_hi']}
mark3_background {C['lacquer']}

"""
    names = ["black", "red", "green", "yellow", "blue", "magenta", "cyan", "white"]
    for i in range(16):
        t += f"# {'bright ' if i > 7 else ''}{names[i % 8]}\ncolor{i:<2} {ANSI[i]}\n"
    return write(f"kitty/{SLUG}.conf", t)


# ------------------------------------------------------------------ Alacritty
def alacritty():
    n = ["black", "red", "green", "yellow", "blue", "magenta", "cyan", "white"]
    t = f"""# {HEADER}
# Import it from alacritty.toml:
#   [general]
#   import = ["~/.config/alacritty/themes/{SLUG}.toml"]

[colors.primary]
background = "{BG}"
foreground = "{FG}"
dim_foreground = "{C['mist']}"
bright_foreground = "{C['paper_hi']}"

[colors.cursor]
text = "{CUR_TXT}"
cursor = "{CUR}"

[colors.vi_mode_cursor]
text = "{CUR_TXT}"
cursor = "{C['gold']}"

[colors.selection]
text = "{SEL_FG}"
background = "{SEL_BG}"

[colors.search.matches]
foreground = "{C['ink']}"
background = "{C['gold']}"

[colors.search.focused_match]
foreground = "{C['paper_hi']}"
background = "{C['lacquer']}"

[colors.hints.start]
foreground = "{C['ink']}"
background = "{C['gold']}"

[colors.hints.end]
foreground = "{C['ink']}"
background = "{C['pampas']}"

[colors.footer_bar]
foreground = "{C['paper']}"
background = "{C['ash']}"

[colors.normal]
""" + "".join(f'{n[i]} = "{ANSI[i]}"\n' for i in range(8)) + "\n[colors.bright]\n" + \
        "".join(f'{n[i]} = "{ANSI[i + 8]}"\n' for i in range(8))
    p = write(f"alacritty/{SLUG}.toml", t)
    cfg = f"""# Alacritty config — {NAME}
[general]
import = ["~/.config/alacritty/themes/{SLUG}.toml"]
live_config_reload = true

[window]
padding = {{ x = 14, y = 12 }}
dynamic_padding = true
decorations = "Buttonless"
opacity = 0.95
blur = true
option_as_alt = "Both"
dimensions = {{ columns = 120, lines = 34 }}

[font]
normal = {{ family = "JetBrainsMono Nerd Font", style = "Regular" }}
bold = {{ family = "JetBrainsMono Nerd Font", style = "Bold" }}
italic = {{ family = "JetBrainsMono Nerd Font", style = "Italic" }}
size = 14.0
offset = {{ x = 0, y = 3 }}

[cursor]
style = {{ shape = "Beam", blinking = "On" }}
unfocused_hollow = true
thickness = 0.18

[scrolling]
history = 10000

[selection]
save_to_clipboard = true
"""
    write(f"alacritty/alacritty{SUFFIX}.toml", cfg)
    return p


# ------------------------------------------------------------------ WezTerm
def wezterm():
    q = lambda xs: "{ " + ", ".join(f'"{x}"' for x in xs) + " }"
    t = f"""-- {HEADER}
-- Drop this file in ~/.config/wezterm/wezterm.lua, or copy the colour scheme table into yours.
local wezterm = require("wezterm")
local config = wezterm.config_builder and wezterm.config_builder() or {{}}

local scheme = {{
  foreground = "{FG}",
  background = "{BG}",
  cursor_bg = "{CUR}",
  cursor_fg = "{CUR_TXT}",
  cursor_border = "{CUR}",
  selection_fg = "{SEL_FG}",
  selection_bg = "{SEL_BG}",
  scrollbar_thumb = "{C['stone']}",
  split = "{C['slate']}",
  visual_bell = "{C['blood']}",
  compose_cursor = "{C['gold']}",
  ansi = {q(ANSI[:8])},
  brights = {q(ANSI[8:])},
  tab_bar = {{
    background = "{C['ink']}",
    active_tab = {{ bg_color = "{C['lacquer']}", fg_color = "{C['paper_hi']}", intensity = "Bold" }},
    inactive_tab = {{ bg_color = "{C['ash']}", fg_color = "{C['mist']}" }},
    inactive_tab_hover = {{ bg_color = "{C['stone']}", fg_color = "{C['paper']}" }},
    new_tab = {{ bg_color = "{C['ink']}", fg_color = "{C['smoke']}" }},
    new_tab_hover = {{ bg_color = "{C['blood']}", fg_color = "{C['paper_hi']}" }},
  }},
}}

config.color_schemes = {{ ["{NAME}"] = scheme }}
config.color_scheme = "{NAME}"
config.font = wezterm.font("JetBrainsMono Nerd Font")
config.font_size = 14.0
config.line_height = 1.1
config.window_padding = {{ left = 14, right = 14, top = 12, bottom = 12 }}
config.window_decorations = "RESIZE|INTEGRATED_BUTTONS"
config.window_background_opacity = 0.95
config.macos_window_background_blur = 20
config.use_fancy_tab_bar = false
config.tab_bar_at_bottom = false
config.hide_tab_bar_if_only_one_tab = true
config.default_cursor_style = "BlinkingBar"
config.send_composed_key_when_left_alt_is_pressed = false
config.send_composed_key_when_right_alt_is_pressed = false
config.initial_cols = 120
config.initial_rows = 34

return config
"""
    return write(f"wezterm/wezterm{SUFFIX}.lua", t)


# ------------------------------------------------------------------ btop
def btop():
    t = f"""# {HEADER}
theme[main_bg]="{BG}"
theme[main_fg]="{FG}"
theme[title]="{C['gold']}"
theme[hi_fg]="{C['crimson']}"
theme[selected_bg]="{C['blood']}"
theme[selected_fg]="{C['paper_hi']}"
theme[inactive_fg]="{C['smoke']}"
theme[graph_text]="{C['mist']}"
theme[meter_bg]="{C['stone']}"
theme[proc_misc]="{C['gold']}"

theme[cpu_box]="{ROLE['focus']}"
theme[mem_box]="{C['gold']}"
theme[net_box]="{C['indigo']}"
theme[proc_box]="{C['slate']}"
theme[div_line]="{C['stone']}"

theme[temp_start]="{ROLE['grad_start']}"
theme[temp_mid]="{ROLE['grad_mid']}"
theme[temp_end]="{ROLE['grad_end']}"

theme[cpu_start]="{ROLE['grad_start']}"
theme[cpu_mid]="{ROLE['grad_mid']}"
theme[cpu_end]="{ROLE['grad_end']}"

theme[free_start]="{C['stone']}"
theme[free_mid]="{C['patina']}"
theme[free_end]="{C['jade']}"

theme[cached_start]="{C['stone']}"
theme[cached_mid]="{C['indigo']}"
theme[cached_end]="{C['sky']}"

theme[available_start]="{C['stone']}"
theme[available_mid]="{C['gold']}"
theme[available_end]="{C['gold_hi']}"

theme[used_start]="{ROLE['grad_start']}"
theme[used_mid]="{ROLE['grad_mid']}"
theme[used_end]="{ROLE['grad_end']}"

theme[download_start]="{C['stone']}"
theme[download_mid]="{C['indigo']}"
theme[download_end]="{C['sky']}"

theme[upload_start]="{C['stone']}"
theme[upload_mid]="{C['lacquer']}"
theme[upload_end]="{C['vermilion']}"

theme[process_start]="{ROLE['grad_start']}"
theme[process_mid]="{ROLE['grad_mid']}"
theme[process_end]="{ROLE['grad_end']}"
"""
    return write(f"btop/{SLUG}.theme", t)


# ------------------------------------------------------------------ bat / delta
def tmtheme():
    def s(name, scope, fg=None, style=None, bg=None):
        st = {}
        if fg:
            st["foreground"] = fg
        if bg:
            st["background"] = bg
        if style is not None:
            st["fontStyle"] = style
        return {"name": name, "scope": scope, "settings": st}
    settings = [{"settings": {
        "background": BG, "foreground": FG, "caret": CUR, "lineHighlight": C["ash"],
        "selection": SEL_BG, "selectionForeground": SEL_FG, "invisibles": C["slate"],
        "gutter": BG, "gutterForeground": C["smoke"], "findHighlight": C["gold"],
        "guide": C["stone"], "activeGuide": C["gold"]}}]
    settings += [
        s("Comment", "comment, punctuation.definition.comment", C["smoke"], "italic"),
        s("String", "string, string.quoted", C["moss"]),
        s("Escape", "constant.character.escape, string.regexp", C["jade"]),
        s("Number", "constant.numeric", C["ember"]),
        s("Constant", "constant, constant.language, support.constant", C["ember"], "bold" if MONO else None),
        s("Keyword", "keyword, storage.modifier, keyword.control", C["crimson"], "bold" if MONO else None),
        s("Operator", "keyword.operator", C["mist"]),
        s("Storage", "storage.type", C["crimson"], "italic"),
        s("Function", "entity.name.function, support.function, meta.function-call", C["gold_hi"]),
        s("Class", "entity.name.type, entity.name.class, support.type, support.class", C["sky"], "italic" if MONO else None),
        s("Inherited", "entity.other.inherited-class", C["sky"], "italic"),
        s("Variable", "variable, variable.other", FG),
        s("Parameter", "variable.parameter", C["pampas"], "italic"),
        s("Language var", "variable.language", C["sakura"], "italic"),
        s("Member", "variable.other.member, variable.other.property, meta.property-name", C["pampas"]),
        s("Tag", "entity.name.tag", C["crimson"]),
        s("Attribute", "entity.other.attribute-name", C["gold"], "italic"),
        s("Import", "keyword.control.import, keyword.other.import, meta.import", C["sakura"]),
        s("Punctuation", "punctuation, meta.brace", C["mist"]),
        s("Heading", "markup.heading, entity.name.section", C["vermilion"], "bold"),
        s("Bold", "markup.bold", None, "bold"),
        s("Italic", "markup.italic", None, "italic"),
        s("Link", "markup.underline.link, string.other.link", C["sky"], "underline"),
        s("Code", "markup.raw, markup.inline.raw", C["jade"]),
        s("Quote", "markup.quote", C["mist"], "italic"),
        s("List", "markup.list punctuation.definition.list", C["gold"]),
        s("Inserted", "markup.inserted", C["paper_hi"] if MONO else C["moss"], "bold" if MONO else None),
        s("Deleted", "markup.deleted", C["smoke"] if MONO else C["crimson"], "strikethrough" if MONO else None),
        s("Changed", "markup.changed", C["gold"]),
        s("Diff header", "meta.diff.header, meta.diff.range", C["sky"]),
        s("Invalid", "invalid", C["paper_hi"], "underline" if MONO else None, C["blood"]),
        s("JSON key", "support.type.property-name, meta.mapping.key string", C["gold"]),
    ]
    theme = {"name": NAME, "author": "Shubhwtf", "uuid": str(uuid.uuid5(uuid.NAMESPACE_DNS, SLUG + ".tmTheme")),
             "semanticClass": "theme.dark.ghost-of-tsushima", "colorSpaceName": "sRGB", "settings": settings}
    return write(f"bat/{SLUG}.tmTheme", plistlib.dumps(theme, fmt=plistlib.FMT_XML), "wb")


def delta():
    if MONO:   # no hue: deleted lines sink darker and strike through, added lines rise brighter and bold
        diff = f"""    minus-style = syntax "{C['diff_delete']}"
    minus-emph-style = "{C['smoke']}" "{C['diff_delete_emph']}" strike
    minus-non-emph-style = syntax "{C['diff_delete']}"
    plus-style = syntax "{C['diff_add']}"
    plus-emph-style = "{C['paper_hi']}" "{C['diff_add_emph']}" bold ul
    plus-non-emph-style = syntax "{C['diff_add']}"
    zero-style = syntax
    line-numbers-minus-style = "{C['smoke']}" strike
    line-numbers-plus-style = "{C['paper_hi']}" bold
    line-numbers-zero-style = "{C['slate']}""" + '"'
    else:
        diff = f"""    minus-style = syntax "{C['diff_delete']}"
    minus-emph-style = syntax "{C['diff_delete_emph']}"
    minus-non-emph-style = syntax "{C['diff_delete']}"
    plus-style = syntax "{C['diff_add']}"
    plus-emph-style = syntax "{C['diff_add_emph']}"
    plus-non-emph-style = syntax "{C['diff_add']}"
    zero-style = syntax
    line-numbers-minus-style = "{C['crimson']}"
    line-numbers-plus-style = "{C['moss']}"
    line-numbers-zero-style = "{C['slate']}""" + '"'
    t = f"""# {HEADER}
# Add to ~/.gitconfig:
#   [include]
#       path = ~/.config/delta/{SLUG}.gitconfig
#   [delta]
#       features = {SLUG}
[delta "{SLUG}"]
    dark = true
    syntax-theme = {NAME}
    line-numbers = true
    side-by-side = false
    navigate = true
    file-style = "{C['paper_hi']}" bold
    file-decoration-style = "{ROLE['focus']}" ul
    file-added-label = [+]
    file-removed-label = [-]
    file-modified-label = [~]
    hunk-header-style = file line-number syntax
    hunk-header-decoration-style = "{C['slate']}" box
    hunk-header-file-style = "{C['gold']}"
    hunk-header-line-number-style = "{C['sky']}"
{diff}
    line-numbers-left-style = "{C['stone']}"
    line-numbers-right-style = "{C['stone']}"
    commit-decoration-style = "{C['gold']}" box
    commit-style = "{C['gold']}" bold
    blame-palette = "{C['charcoal']} {C['ash']} {C['stone']}"
    merge-conflict-begin-symbol = ▼
    merge-conflict-end-symbol = ▲
    merge-conflict-ours-diff-header-style = "{C['gold']}" bold
    merge-conflict-theirs-diff-header-style = "{C['sky']}" bold
"""
    return write(f"delta/{SLUG}.gitconfig", t)


def lazygit():
    t = f"""# {HEADER}
# Merge into ~/Library/Application Support/lazygit/config.yml (macOS) or ~/.config/lazygit/config.yml
gui:
  nerdFontsVersion: "3"
  border: rounded
  theme:
    activeBorderColor:
      - "{C['vermilion']}"
      - bold
    inactiveBorderColor:
      - "{C['slate']}"
    searchingActiveBorderColor:
      - "{C['gold']}"
      - bold
    optionsTextColor:
      - "{C['sky']}"
    selectedLineBgColor:
      - "{C['stone']}"
    inactiveViewSelectedLineBgColor:
      - "{C['ash']}"
    cherryPickedCommitFgColor:
      - "{C['ink']}"
    cherryPickedCommitBgColor:
      - "{C['gold']}"
    markedBaseCommitFgColor:
      - "{C['ink']}"
    markedBaseCommitBgColor:
      - "{C['sky']}"
    unstagedChangesColor:
      - "{C['crimson']}"{chr(10) + "      - bold" if MONO else ""}
    defaultFgColor:
      - "{C['paper']}"
  authorColors:
    "*": "{C['gold']}"
  branchColors:
    main: "{C['crimson']}"
    master: "{C['crimson']}"
"""
    return write(f"lazygit/config{SUFFIX}.yml", t)


def dotfiles():
    """kitty.conf and the Ghostty config, adapted to the active variant."""
    out = []
    base = os.path.join(ROOT, "dotfiles")
    if not MONO:
        return out
    k = open(os.path.join(base, "kitty", "kitty.conf")).read()
    k = k.replace("themes/ghost-of-tsushima.conf", f"themes/{SLUG}.conf")
    k = k.replace("# ink, paper, lacquer red and gold leaf", "# Kurosawa mode: black and white, no colour")
    k = k.replace("# a red brushstroke trail", "# a silver brushstroke trail")
    p = os.path.join(base, "kitty", f"kitty{SUFFIX}.conf")
    open(p, "w").write(k)
    g = open(os.path.join(base, "ghostty", "config")).read()
    g = g.replace("theme = ghost-of-tsushima", f"theme = {SLUG}")
    g = g.replace("# 冥人 Ghost of Tsushima — Ghostty", "# 冥人 Ghost of Tsushima, Kurosawa mode — Ghostty")
    g = g.replace("ink screen with a red glow", "ink screen, in black and white")
    import re
    g = re.sub(r"macos-icon-ghost-color = .*", f"macos-icon-ghost-color = {C['paper']}", g)
    g = re.sub(r"macos-icon-screen-color = .*", f"macos-icon-screen-color = {C['charcoal']},{ROLE['icon_screen']}", g)
    p2 = os.path.join(base, "ghostty", f"config{SUFFIX}")
    open(p2, "w").write(g)
    return [p, p2]


def main():
    out = [*dotfiles(), terminal_app(), *iterm(), ghostty(), kitty(), alacritty(), wezterm(), btop(), tmtheme(), delta(), lazygit()]
    for p in out:
        print("wrote", os.path.relpath(p, ROOT))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Generate the Claude Code theme and status line from palette.json.

  claude/themes/ghost-of-tsushima[-kurosawa].json   a custom theme (~/.claude/themes/),
                                                    every one of Claude Code's colour keys
  claude/statusline[-kurosawa].sh                   a status line in the starship style

usage: [GOT_VARIANT=kurosawa] claude.py [ROOT]
"""
import json
import os
import stat
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from palette import C, MONO, NAME, ROLE, SLUG, SUFFIX, mix, rgb  # noqa: E402

ROOT = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HDR = f"{NAME} — generated from palette.json by src/claude.py"


def write(rel, text, exe=False):
    path = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(text)
    if exe:
        os.chmod(path, os.stat(path).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def lift(name, t=0.35):
    """A lighter shimmer of a colour, toward bright paper."""
    return mix(C[name], C["paper_hi"], t)


def theme():
    c = C
    o = {
        # the brand colour, spinner and Clawd: lacquer red (silver in Kurosawa)
        "claude": c["crimson"], "claudeShimmer": lift("crimson"),
        "clawd_body": ROLE["emblem"], "clawd_background": c["ink"],
        "briefLabelClaude": c["crimson"], "briefLabelYou": c["sky"],
        "claudeBlue_FOR_SYSTEM_SPINNER": c["sky"], "claudeBlueShimmer_FOR_SYSTEM_SPINNER": lift("sky"),
        # modes and prompts
        "permission": c["gold_hi"], "permissionShimmer": c["pampas"],
        "autoAccept": c["gold"], "autoAcceptShimmer": c["gold_hi"],
        "planMode": c["patina"], "ide": c["sky"], "skill": c["sakura"],
        "bashBorder": c["vermilion"], "fastMode": c["vermilion"], "fastModeShimmer": c["ember"],
        "effortUltra": c["gold_hi"],
        "promptBorder": c["smoke"], "promptBorderShimmer": c["mist"],
        # text
        "text": c["paper"], "inverseText": c["ink"],
        "inactive": c["smoke"], "inactiveShimmer": c["mist"], "subtle": c["slate"],
        "suggestion": c["gold_hi"], "remember": c["sky"], "background": c["jade"],
        "success": c["moss"], "error": c["crimson"], "warning": c["gold"], "warningShimmer": c["gold_hi"],
        "merged": c["sakura"], "professionalBlue": c["sky"], "chromeYellow": c["gold"],
        "rate_limit_fill": c["gold"], "rate_limit_empty": c["stone"],
        # surfaces
        "userMessageBackground": c["ash"], "userMessageBackgroundHover": c["stone"],
        "composerSidebarBackground": c["charcoal"], "selectionBg": c["blood"],
        "bashMessageBackgroundColor": mix(c["ash"], c["blood"], 0.25),
        "memoryBackgroundColor": mix(c["ash"], c["indigo"], 0.2),
        # diffs: the same washes as the editor
        "diffAdded": c["diff_add_emph"], "diffRemoved": c["diff_delete_emph"],
        "diffAddedDimmed": c["diff_add"], "diffRemovedDimmed": c["diff_delete"],
        "diffAddedWord": mix(c["bamboo"], c["ink"], 0.25), "diffRemovedWord": mix(c["crimson"], c["ink"], 0.3),
        # subagents
        "red_FOR_SUBAGENTS_ONLY": c["crimson"], "orange_FOR_SUBAGENTS_ONLY": c["ember"],
        "yellow_FOR_SUBAGENTS_ONLY": c["gold"], "green_FOR_SUBAGENTS_ONLY": c["moss"],
        "blue_FOR_SUBAGENTS_ONLY": c["sky"], "cyan_FOR_SUBAGENTS_ONLY": c["jade"],
        "purple_FOR_SUBAGENTS_ONLY": c["blossom"], "pink_FOR_SUBAGENTS_ONLY": c["sakura"],
    }
    # the rainbow, in the theme's own pigments
    for name, col in (("red", "crimson"), ("orange", "ember"), ("yellow", "gold_hi"), ("green", "moss"),
                      ("blue", "sky"), ("indigo", "indigo"), ("violet", "sakura")):
        o[f"rainbow_{name}"] = c[col]
        o[f"rainbow_{name}_shimmer"] = lift(col, 0.45)
    if MONO:
        # without hue the diff washes need more lightness between them
        o.update({"diffAdded": c["diff_add_emph"], "diffRemoved": c["ink"],
                  "diffAddedWord": c["lacquer"], "diffRemovedWord": c["slate"]})
    # Every key is overridden, so the base only decides two things: code highlighting
    # (Monokai on "dark", the terminal's own ANSI colours on "dark-ansi") and colour depth
    # ("dark-ansi" rounds every colour to the xterm-256 palette). Red keeps the exact
    # truecolor palette; Kurosawa takes the ANSI base, where grays round to grays and code
    # is highlighted in the terminal's gray ramp, so no hue can appear.
    base = "dark-ansi" if MONO else "dark"
    data = {"name": NAME, "base": base, "overrides": dict(sorted(o.items()))}
    write(f"claude/themes/{SLUG}.json", json.dumps(data, indent=2) + "\n")
    return o


def statusline():
    def fg(n):
        return "\\033[38;2;{};{};{}m".format(*rgb(C[n]))

    def bg(n):
        return "\\033[48;2;{};{};{}m".format(*rgb(C[n]))

    seal = "lacquer" if not MONO else "paper"
    seal_fg = "paper_hi" if not MONO else "ink"
    text = f"""#!/usr/bin/env bash
# {HDR}
# Claude Code status line: ~/.claude/settings.json -> "statusLine": {{"type": "command", "command": "<this file>"}}
# Reads the session JSON on stdin and prints:  冥  model  ~/dir   branch
input="$(cat)"
field() {{ printf '%s' "$input" | sed -n "s/.*\\"$1\\"[[:space:]]*:[[:space:]]*\\"\\([^\\"]*\\)\\".*/\\1/p" | head -n1; }}
model="$(field display_name)"
dir="$(field current_dir)"
[[ -n "$dir" ]] || dir="$PWD"
branch="$(git -C "$dir" branch --show-current 2>/dev/null)"
short="${{dir/#$HOME/\\~}}"
off='\\033[0m'
out="{bg(seal)}{fg(seal_fg)}\\033[1m 冥 $off{fg(seal)}{bg('stone')}"
out+="{bg('stone')}{fg('gold_hi')}\\033[1m ${{model:-Claude}} $off{fg('stone')}{bg('ash')}"
out+="{bg('ash')}{fg('paper')} $short $off{fg('ash')}$off"
[[ -n "$branch" ]] && out+=" {fg('sky')} $branch$off"
printf '%b\\n' "$out"
"""
    write(f"claude/statusline{SUFFIX}.sh", text, exe=True)


if __name__ == "__main__":
    theme()
    statusline()

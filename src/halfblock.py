"""Render the emblem as half-block terminal art (two pixels per cell: ▀ / ▄).

grid(px)        -> rows of palette names (None = transparent), px x px pixels
ansi(px)        -> truecolor ANSI text (for fastfetch)
lua_art(px)     -> (lines, highlight spans, colours) for the Neovim dashboard
"""
import io
import os
import subprocess
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from emblem import emblem_svg  # noqa: E402
from palette import C, ROLE, rgb  # noqa: E402

INKS = {"red": ROLE["emblem"], "deep": ROLE["emblem_deep"], "blade": ROLE["blade"], "gold": ROLE["metal"],
        "hilt": C["slate"]}


def grid(px):
    svg = emblem_svg(1024, small=True)
    png = subprocess.run(["rsvg-convert", "-w", str(px * 4), "-h", str(px * 4)], input=svg.encode(),
                         capture_output=True, check=True).stdout
    im = Image.open(io.BytesIO(png)).convert("RGBA").resize((px, px), Image.LANCZOS)
    a = np.asarray(im, np.float32)
    names = list(INKS)
    cols = np.array([rgb(INKS[n]) for n in names], np.float32)
    out = []
    for y in range(px):
        row = []
        for x in range(px):
            r, g, b, al = a[y, x]
            if al < 110:
                row.append(None)
                continue
            d = ((cols - np.array([r, g, b])) ** 2).sum(axis=1)
            row.append(names[int(d.argmin())])
        out.append(row)
    # trim empty rows/cols
    while out and all(v is None for v in out[0]):
        out.pop(0)
    while out and all(v is None for v in out[-1]):
        out.pop()
    if len(out) % 2:
        out.append([None] * px)
    left = min((next((i for i, v in enumerate(r) if v), px) for r in out))
    right = max((max((i for i, v in enumerate(r) if v), default=0) for r in out))
    return [r[left:right + 1] for r in out]


def cells(px):
    g = grid(px)
    rows = []
    for y in range(0, len(g), 2):
        rows.append(list(zip(g[y], g[y + 1])))
    return rows


def ansi(px):
    def fg(n):
        r, g, b = rgb(INKS[n])
        return f"\x1b[38;2;{r};{g};{b}m"

    def bg(n):
        r, g, b = rgb(INKS[n])
        return f"\x1b[48;2;{r};{g};{b}m"
    lines = []
    for row in cells(px):
        s = ""
        for top, bot in row:
            if top is None and bot is None:
                s += "\x1b[0m "
            elif top and bot is None:
                s += "\x1b[0m" + fg(top) + "▀"
            elif bot and top is None:
                s += "\x1b[0m" + fg(bot) + "▄"
            elif top == bot:
                s += "\x1b[0m" + fg(top) + "█"
            else:
                s += fg(top) + bg(bot) + "▀"
        lines.append(s.rstrip() + "\x1b[0m")
    return "\n".join(lines) + "\n"


def lua_art(px):
    """lines + per-line [group, byte_start, byte_end] spans + group colours."""
    lines, spans, groups = [], [], {}
    for row in cells(px):
        text, line_spans, pos = "", [], 0
        for top, bot in row:
            if top is None and bot is None:
                ch, grp = " ", None
            elif top and bot is None:
                ch, grp = "▀", f"GotArt_{top}"
                groups[grp] = {"fg": INKS[top]}
            elif bot and top is None:
                ch, grp = "▄", f"GotArt_{bot}"
                groups[grp] = {"fg": INKS[bot]}
            elif top == bot:
                ch, grp = "█", f"GotArt_{top}"
                groups[grp] = {"fg": INKS[top]}
            else:
                ch, grp = "▀", f"GotArt_{top}_{bot}"
                groups[grp] = {"fg": INKS[top], "bg": INKS[bot]}
            n = len(ch.encode())
            if grp:
                if line_spans and line_spans[-1][0] == grp and line_spans[-1][2] == pos:
                    line_spans[-1][2] = pos + n
                else:
                    line_spans.append([grp, pos, pos + n])
            text += ch
            pos += n
        lines.append(text)
        spans.append(line_spans)
    w = max(len(x) for x in lines)
    lines = [x + " " * (w - len(x)) for x in lines]
    return lines, spans, groups


if __name__ == "__main__":
    sys.stdout.write(ansi(int(sys.argv[1]) if len(sys.argv) > 1 else 34))

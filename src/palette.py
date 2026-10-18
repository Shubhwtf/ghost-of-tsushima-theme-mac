"""The one Ghost of Tsushima palette. Every config in this repo is generated from palette.json."""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

with open(os.path.join(ROOT, "palette.json")) as _f:
    _DATA = json.load(_f)

NAME = _DATA["name"]
SLUG = _DATA["slug"]
C = dict(_DATA["colors"])                          # name -> "#rrggbb"
ROLE = {k: C[v] for k, v in _DATA["roles"].items()}  # role -> "#rrggbb"
ANSI = [C[n] for n in _DATA["ansi"]]               # 16 terminal colors
ANSI_NAMES = list(_DATA["ansi"])


def rgb(h):
    """'#rrggbb' -> (r, g, b) ints."""
    h = C.get(h, h).lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def rgbf(h):
    return tuple(x / 255 for x in rgb(h))


def hexc(r, g, b):
    return "#" + "".join(f"{max(0, min(255, round(x))):02x}" for x in (r, g, b))


def mix(a, b, t):
    """Blend colour a toward b by t (0..1)."""
    ra, rb = rgb(a), rgb(b)
    return hexc(*(x + (y - x) * t for x, y in zip(ra, rb)))


def luminance(h):
    def ch(c):
        c /= 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = rgb(h)
    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)


def contrast(a, b):
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


if __name__ == "__main__":
    bg = ROLE["background"]
    for n, h in C.items():
        print(f"{n:10s} {h}  on bg {contrast(h, bg):5.2f}  on ink {contrast(h, C['ink']):5.2f}")
    print("selection", round(contrast(ROLE["selection_fg"], ROLE["selection_bg"]), 2))
    print("paper on lacquer", round(contrast(C["paper_hi"], C["lacquer"]), 2))

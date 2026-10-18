"""The Ghost of Tsushima palettes. Every config in this repo is generated from palette.json.

Two variants share one set of colour names:
  red       (default) ink, washi paper, lacquer red and gold leaf
  kurosawa  pure grayscale, after the game's black-and-white film mode

Pick one with the GOT_VARIANT environment variable (red | kurosawa).
`python3 src/palette.py` prints contrast ratios and checks both variants.
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VARIANTS = ("red", "kurosawa")

with open(os.path.join(ROOT, "palette.json")) as _f:
    _DATA = json.load(_f)


def load(variant="red"):
    """Return (name, slug, colours, roles, ansi) for a variant."""
    if variant not in VARIANTS:
        raise SystemExit(f"unknown variant {variant!r}; use one of {', '.join(VARIANTS)}")
    d = _DATA if variant == "red" else _DATA["variants"][variant]
    colors = dict(d["colors"])
    roles = {k: colors[v] for k, v in d["roles"].items()}
    ansi = [colors.get(n, n) for n in d["ansi"]]
    return d["name"], d["slug"], colors, roles, ansi


VARIANT = os.environ.get("GOT_VARIANT", "red")
NAME, SLUG, C, ROLE, ANSI = load(VARIANT)
SUFFIX = "" if VARIANT == "red" else f"-{VARIANT}"      # file-name suffix
MONO = VARIANT == "kurosawa"                              # lean on bold/italic/underline


def rgb(h):
    """'#rrggbb' (or a colour name) -> (r, g, b) ints."""
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


def lightness(h):
    """CIE L* (0..100), the perceptual lightness the ANSI ramp is spaced by."""
    y = luminance(h)
    return 116 * y ** (1 / 3) - 16 if y > 216 / 24389 else y * 24389 / 27


def contrast(a, b):
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


# colours used as text on the background must reach 4.5:1
TEXT = ["smoke", "mist", "rice", "paper", "paper_hi", "crimson", "vermilion", "ember", "gold", "gold_hi",
        "pampas", "sky", "bamboo", "moss", "sakura", "blossom", "patina", "jade"]


def check(variant):
    name, _, c, role, ansi = load(variant)
    bg = role["background"]
    bad = []
    for n in TEXT:
        r = contrast(c[n], bg)
        if r < 4.5 and not (variant == "red" and n == "indigo"):
            bad.append(f"{n} {r:.2f}")
    for a in ansi[1:]:
        if contrast(a, bg) < 4.5:
            bad.append(f"ansi {a} {contrast(a, bg):.2f}")
    pairs = [("selection", role["selection_fg"], role["selection_bg"]), ("accent", c["paper_hi"], c["lacquer"]),
             ("cursor", role["cursor_text"], role["cursor"]), ("search", c["ink"], c["gold"])]
    for label, fg, b in pairs:
        if contrast(fg, b) < 4.5:
            bad.append(f"{label} {contrast(fg, b):.2f}")
    if variant == "kurosawa":
        hues = [k for k, v in c.items() if len({v[1:3], v[3:5], v[5:7]}) != 1]
        hues += [a for a in ansi if len({a[1:3], a[3:5], a[5:7]}) != 1]
        if hues:
            bad.append("not gray: " + ", ".join(hues))
        # with no hue, luminance is the only cue: every ANSI colour must be told apart from
        # every other by lightness (a ~3.3 L* ramp; >= 2.9 after 8-bit rounding), and within
        # the normal and the bright set by >= 6 L*
        lv = [lightness(a) for a in ansi]
        for i in range(16):
            for j in range(i + 1, 16):
                need = 6 if i // 8 == j // 8 else 2.9
                if abs(lv[i] - lv[j]) < need:
                    bad.append(f"ansi {i} and {j} are {abs(lv[i] - lv[j]):.1f} L* apart (need {need})")
    print(f"{name}: " + ("ok" if not bad else "FAIL " + "; ".join(bad)))
    for n in TEXT:
        print(f"  {n:10s} {c[n]}  {contrast(c[n], bg):5.2f}:1")
    for i, a in enumerate(ansi):
        print(f"  ansi {i:<5d} {a}  {contrast(a, bg):5.2f}:1  L* {lightness(a):5.1f}")
    return not bad


if __name__ == "__main__":
    import sys
    ok = all([check(v) for v in VARIANTS])
    sys.exit(0 if ok else 1)

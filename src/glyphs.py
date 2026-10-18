"""Text as SVG outlines, so rendering needs no installed fonts.

src/glyphs.json holds the outlines of the few characters the artwork uses,
extracted from OFL fonts (Shippori Mincho, Yuji Boku). Rebuild it with:

    pip install fonttools
    python3 src/glyphs.py build ShipporiMincho=/path/ShipporiMincho-ExtraBold.ttf YujiBoku=/path/YujiBoku-Regular.ttf
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "glyphs.json")
CHARS = ("冥人風導誉浜死対馬境井仁月彼岸花鳥居黒沢鬼侍道神影名誇れはでにましたくのをが、。「」・"
         "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 .,'-—")

_cache = None


def _db():
    global _cache
    if _cache is None:
        with open(DB) as f:
            _cache = json.load(f)
    return _cache


def text_svg(text, x, y, size, font="ShipporiMincho", anchor="middle", spacing=0.0, vertical=False):
    """SVG <g> with the text's outlines; (x, y) is the baseline anchor
    (for vertical text, x is the column centre and y the top)."""
    fd = _db()[font]
    em = fd["upem"]
    s = size / em
    parts = []
    if vertical:
        cy = y
        for ch in text:
            g = fd["glyphs"].get(ch)
            if g is None:
                cy += size * (1 + spacing)
                continue
            gx = x - g["adv"] * s / 2
            parts.append(f'<path transform="translate({gx:.2f},{cy + size * 0.88:.2f}) scale({s:.5f},{-s:.5f})" d="{g["d"]}"/>')
            cy += size * (1 + spacing)
        return "<g>" + "".join(parts) + "</g>"
    total = sum(fd["glyphs"].get(ch, {"adv": em * 0.5})["adv"] * s + size * spacing for ch in text) - size * spacing
    cx = x - (total / 2 if anchor == "middle" else total if anchor == "end" else 0)
    for ch in text:
        g = fd["glyphs"].get(ch, {"adv": em * 0.5, "d": ""})
        if g["d"]:
            parts.append(f'<path transform="translate({cx:.2f},{y:.2f}) scale({s:.5f},{-s:.5f})" d="{g["d"]}"/>')
        cx += g["adv"] * s + size * spacing
    return "<g>" + "".join(parts) + "</g>"


def build(specs):
    from fontTools.pens.svgPathPen import SVGPathPen
    from fontTools.ttLib import TTFont
    out = {}
    for spec in specs:
        name, path = spec.split("=", 1)
        font = TTFont(path)
        cmap = font.getBestCmap()
        gs = font.getGlyphSet()
        glyphs = {}
        for ch in CHARS:
            gname = cmap.get(ord(ch))
            if not gname:
                continue
            pen = SVGPathPen(gs, lambda v: f"{v:.0f}")
            gs[gname].draw(pen)
            glyphs[ch] = {"adv": gs[gname].width, "d": pen.getCommands()}
        out[name] = {"upem": font["head"].unitsPerEm, "glyphs": glyphs}
        print(f"{name}: {len(glyphs)} glyphs")
    with open(DB, "w") as f:
        json.dump(out, f, ensure_ascii=False, separators=(",", ":"))


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "build":
        build(sys.argv[2:])
    else:
        print(__doc__)

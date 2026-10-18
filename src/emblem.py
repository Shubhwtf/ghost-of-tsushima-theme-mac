#!/usr/bin/env python3
"""The emblem: a red ensō brush circle cut by a katana. Pure SVG (the dry
brush is built from bristle bands), so it scales to any size.

usage: emblem.py OUT_DIR   -> emblem.svg, emblem.png (1024), emblem-256.png
"""
import math
import os
import random
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from palette import C  # noqa: E402


def _f(p):
    return f"{p[0]:.2f},{p[1]:.2f}"


def enso_paths(cx, cy, r, width, seed=7, start=-2.25, sweep=5.75, bristles=26):
    """Variable-width bristle bands around a circle. Each band is broken where
    the brush runs dry, toward the end of the stroke."""
    rng = random.Random(seed)
    out = []
    n = 220
    for b in range(bristles):
        u = (b + 0.5) / bristles * 2 - 1                    # -1 inner .. 1 outer
        ink = rng.uniform(0.85, 1.0)
        dry_at = rng.uniform(0.78, 1.02) - 0.2 * abs(u) ** 1.5
        phase = rng.uniform(0, 6.28)
        segs, cur = [], []
        for i in range(n + 1):
            t = i / n
            # stroke width: quick press, full belly, long thinning tail
            prof = min(1.0, (t / 0.06) ** 0.7) * (1 - 0.5 * max(0, t - 0.6) / 0.4) ** 1.2
            prof *= 1 + 0.08 * math.sin(t * 9 + phase)
            a = start + sweep * t
            rr = r + 0.06 * r * math.sin(t * 2.2 + 0.4) + u * width / 2 * prof
            gap = t > dry_at and rng.random() < 0.55 + (t - dry_at) * 3
            if gap or abs(u) > prof + 0.02:
                if len(cur) > 2:
                    segs.append(cur)
                cur = []
                continue
            cur.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr, t))
        if len(cur) > 2:
            segs.append(cur)
        bw = width / bristles * 1.45
        for sg in segs:
            d = "M" + " L".join(_f(p) for p in sg)
            out.append(f'<path d="{d}" stroke-width="{bw * ink:.2f}"/>')
    return out


def katana_svg(x0, y0, x1, y1, scale, blade="#ece6dc", edge="#0b0a0a", gold="#c9a45c", hilt="#141212"):
    """Katana from hilt end (x0,y0) to the tip (x1,y1)."""
    L = math.hypot(x1 - x0, y1 - y0)
    ang = math.degrees(math.atan2(y1 - y0, x1 - x0))
    s = scale
    hl = L * 0.24        # tsuka length
    bl = L - hl
    g = [f'<g transform="translate({x0:.1f},{y0:.1f}) rotate({ang:.2f})">']
    # blade: gentle sori, sharp kissaki; ink outline so it reads on light and dark
    by = -s * 0.9
    g.append(f'<path d="M{hl},{-s * 0.55:.1f} C{hl + bl * 0.4:.1f},{-s * 0.75 - bl * 0.02:.1f} {hl + bl * 0.8:.1f},{-s * 0.6 - bl * 0.05:.1f} '
             f'{L:.1f},{by - bl * 0.055:.1f} L{L - s * 1.6:.1f},{s * 0.2 - bl * 0.05:.1f} '
             f'C{hl + bl * 0.75:.1f},{s * 0.55 - bl * 0.035:.1f} {hl + bl * 0.4:.1f},{s * 0.6 - bl * 0.01:.1f} {hl},{s * 0.55:.1f}Z" '
             f'fill="{blade}" stroke="{edge}" stroke-width="{s * 0.28:.2f}" stroke-linejoin="round"/>')
    # hamon line
    g.append(f'<path d="M{hl + s * 2},{s * 0.12:.1f} C{hl + bl * 0.4:.1f},{-s * 0.05 - bl * 0.012:.1f} {hl + bl * 0.75:.1f},{-s * 0.1 - bl * 0.03:.1f} '
             f'{L - s * 2.2:.1f},{-s * 0.25 - bl * 0.05:.1f}" fill="none" stroke="#b9b1a6" stroke-width="{s * 0.16:.2f}"/>')
    # habaki, tsuba, tsuka with gold diamond wrap, kashira
    g.append(f'<rect x="{hl - s * 0.2:.1f}" y="{-s * 0.75:.1f}" width="{s * 1.2:.1f}" height="{s * 1.5:.1f}" fill="{gold}" stroke="{edge}" stroke-width="{s * 0.2:.2f}"/>')
    g.append(f'<ellipse cx="{hl - s * 0.45:.1f}" cy="0" rx="{s * 0.55:.1f}" ry="{s * 2.3:.1f}" fill="{gold}" stroke="{edge}" stroke-width="{s * 0.25:.2f}"/>')
    g.append(f'<rect x="{s * 0.4:.1f}" y="{-s * 0.85:.1f}" width="{hl - s * 1.2:.1f}" height="{s * 1.7:.1f}" rx="{s * 0.5:.1f}" fill="{hilt}" stroke="{edge}" stroke-width="{s * 0.2:.2f}"/>')
    k = 0
    x = s * 1.2
    while x < hl - s * 1.6:
        g.append(f'<path d="M{x:.1f},0 L{x + s * 0.6:.1f},{-s * 0.6:.1f} L{x + s * 1.2:.1f},0 L{x + s * 0.6:.1f},{s * 0.6:.1f}Z" fill="{gold}"/>')
        x += s * 1.6
        k += 1
    g.append(f'<rect x="0" y="{-s * 0.9:.1f}" width="{s * 0.7:.1f}" height="{s * 1.8:.1f}" rx="{s * 0.3:.1f}" fill="{gold}" stroke="{edge}" stroke-width="{s * 0.2:.2f}"/>')
    g.append("</g>")
    return "".join(g)


def emblem_svg(size=1024, bg=None, red=None):
    red = red or C["lacquer"]
    cx = cy = size / 2
    r = size * 0.34
    paths = enso_paths(cx, cy, r, size * 0.12)
    body = []
    if bg:
        body.append(f'<rect width="{size}" height="{size}" rx="{size * 0.22:.0f}" fill="{bg}"/>')
    body.append(f'<g fill="none" stroke="{red}" stroke-linecap="round" stroke-linejoin="round">{"".join(paths)}</g>')
    s = size / 100
    body.append(katana_svg(size * 0.17, size * 0.83, size * 0.86, size * 0.12, s * 1.9))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {size} {size}">'
            + "".join(body) + "</svg>\n")


def main(out):
    os.makedirs(out, exist_ok=True)
    svg = os.path.join(out, "emblem.svg")
    with open(svg, "w") as f:
        f.write(emblem_svg(1024))
    subprocess.run(["rsvg-convert", "-w", "1024", "-h", "1024", svg, "-o", os.path.join(out, "emblem.png")], check=True)
    subprocess.run(["rsvg-convert", "-w", "256", "-h", "256", svg, "-o", os.path.join(out, "emblem-256.png")], check=True)
    tile = os.path.join(out, "emblem-tile.svg")
    with open(tile, "w") as f:
        f.write(emblem_svg(1024, bg=C["ink"]))
    subprocess.run(["rsvg-convert", "-w", "512", "-h", "512", tile, "-o", os.path.join(out, "emblem-tile.png")], check=True)
    print("emblem ->", out)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "assets")

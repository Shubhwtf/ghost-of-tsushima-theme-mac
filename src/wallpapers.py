#!/usr/bin/env python3
"""Original Ghost of Tsushima wallpapers, painted from code.

usage: wallpapers.py [--scene NAME ...] [--res WxH] [--out DIR] [--list]

Every scene is composed in a 3840x2160 design space and rendered at any
resolution (other aspect ratios are rendered 16:9 and centre-cropped).
Needs numpy, pillow and rsvg-convert (librsvg).
"""
import argparse
import math
import os
import random
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paint import Canvas, DW, DH, hex2f, smoothstep, catmull_pts, bez, gblur  # noqa: E402
from palette import C  # noqa: E402
import figures as F  # noqa: E402
import glyphs  # noqa: E402


# ------------------------------------------------------------------ helpers
def ridge(seed, base, amp, cells=6, octaves=6, sharp=1.0):
    """1-D fractal ridge line: returns y(x) in design units for x in 0..DW."""
    rng = np.random.default_rng(seed)
    xs = np.linspace(0, 1, 2048)
    y = np.zeros_like(xs)
    a, tot = 1.0, 0.0
    for o in range(octaves):
        n = cells * 2 ** o + 2
        pts = rng.random(n)
        y += a * np.interp(xs * (n - 1), np.arange(n), pts) if o > 2 else a * _cubic(pts, xs * (n - 1))
        tot += a
        a *= 0.5
    y = y / tot
    y = (y - y.min()) / (y.max() - y.min() + 1e-9)
    return lambda X: base - amp * np.interp(np.asarray(X) / DW, xs, y) ** sharp


def _cubic(pts, t):
    i = np.clip(np.floor(t).astype(int), 0, len(pts) - 2)
    f = t - i
    p0 = pts[np.clip(i - 1, 0, len(pts) - 1)]
    p1, p2 = pts[i], pts[i + 1]
    p3 = pts[np.clip(i + 2, 0, len(pts) - 1)]
    return 0.5 * (2 * p1 + (-p0 + p2) * f + (2 * p0 - 5 * p1 + 4 * p2 - p3) * f * f + (-p0 + 3 * p1 - 3 * p2 + p3) * f ** 3)


def below(c, yfun, soft=2.0):
    """Mask of everything below a ridge line, anti-aliased."""
    xs, ys = c.grid()
    ry = yfun(xs[0])[None, :]
    return np.clip((ys - ry) / soft + 0.5, 0, 1)


def wash(c, yfun, fade, rough_seed, rough=0.35):
    """Ink-wash mountain: darkest along the ridge, dissolving into mist below."""
    xs, ys = c.grid()
    ry = yfun(xs[0])[None, :]
    d = (ys - ry)
    n = c.noise(14, 6, rough_seed, stretch=3.0)
    edge = np.clip(d / 2.5 + 0.5, 0, 1)
    body = np.exp(-np.clip(d, 0, None) / fade * (0.7 + rough * 1.6 * n))
    return edge * body


def petals_svg(rng, n, area, size, kind="petal", wind=(-1, 0.25)):
    x0, y0, x1, y1 = area
    out = []
    for _ in range(n):
        x, y = rng.uniform(x0, x1), rng.uniform(y0, y1)
        s = size * rng.uniform(0.5, 1.3)
        a = math.atan2(wind[1], wind[0]) + rng.uniform(-0.9, 0.9)
        out.append(f'<path d="{F.leaf_path(x, y, s, a, kind)}"/>')
    return "".join(out)


def text_paths(text, x, y, size, font="ShipporiMincho", anchor="middle", spacing=0.0, vertical=False):
    return glyphs.text_svg(text, x, y, size, font, anchor, spacing, vertical)


# ------------------------------------------------------------------ Higanbana
def scene_higanbana(c, rng):
    """Moonlit field of red spider lilies, a lone samurai against a giant moon."""
    xs, ys = c.grid()
    c.img = c.vgrad([(0, "#040303"), (0.35, "#0a0809"), (0.6, "#140b0c"), (0.68, "#2a0d10"),
                     (0.72, "#170a0b"), (1, "#070505")])
    # faint ink clouds in the sky
    cl = c.noise(5, 6, 11, stretch=4.0)
    c.comp(smoothstep(0.52, 0.8, cl) * (ys < 1300), "#1c1617", 0.6)
    # moon + halo
    mx, my, mr = 2330, 760, 570
    halo = c.radial(mx, my, 1900, 2.2)
    c.screen(halo, "#4a3b36", 0.55)
    c.screen(c.radial(mx, my, 900, 2.0), "#8a6f62", 0.35)
    moon = c.svg_mask(f'<circle cx="{mx}" cy="{my}" r="{mr}" fill="#fff"/>')
    tex = c.noise(7, 7, 21)
    d = np.sqrt((xs - mx) ** 2 + (ys - my) ** 2) / mr
    tex2 = c.noise(18, 5, 22)
    shade = 0.95 - 0.13 * smoothstep(0.42, 0.78, tex) - 0.04 * smoothstep(0.5, 0.8, tex2) - 0.07 * d ** 4
    moon_col = hex2f(C["paper_hi"])[None, None, :] * shade[..., None] * np.array([1.0, 0.985, 0.95], np.float32)
    c.img = c.img * (1 - moon[..., None]) + moon_col * moon[..., None]
    # dry-brush ink cloud strokes crossing the moon
    for i, (y, x0, x1, wdt, dry) in enumerate([(1015, 1450, 3350, 70, 0.5), (1085, 1750, 3100, 46, 0.6),
                                               (640, 2050, 3050, 30, 0.7), (1160, 1250, 2650, 36, 0.55)]):
        pts = [(x0, y + 10), ((x0 + x1) / 2, y - 18), (x1, y + 6)]
        m = c.brush(catmull_pts(pts, 40), wdt, seed=40 + i, bristles=90, dry=dry * 0.6, taper=(0.3, 0.45))
        c.comp(c.blur(m, 2.5), "#0c0a0a", 0.9)
    # distant mountains, two ink layers with mist
    r1 = ridge(3, 1460, 260, cells=5)
    c.comp(wash(c, r1, 260, 31), "#1d1517", 0.95)
    mist = c.noise(6, 5, 33, stretch=5.0)
    c.screen(smoothstep(0.3, 0.9, mist) * np.exp(-((ys - 1480) / 120) ** 2), "#5a3a38", 0.5)
    r2 = ridge(4, 1575, 150, cells=7)
    c.comp(below(c, r2), "#0e0a0b")
    # red glow of the lily field on the horizon
    c.screen(np.exp(-((ys - 1600) / 70) ** 2), "#7a1419", 0.5)
    # the field: a painterly red carpet, denser and brighter toward the viewer
    hz = 1590
    field = below(c, lambda X: hz + 6 * np.sin(np.asarray(X) / 300), 3)
    depth = smoothstep(hz, DH, ys)
    n1 = c.noise(9, 6, 51, stretch=3.5)
    n2 = c.noise(30, 5, 52, stretch=2.0)
    dens = np.clip(0.25 + 0.9 * (n1 - 0.5) + 0.5 * (n2 - 0.5) + 0.35 * depth, 0, 1)
    base = hex2f("#0a0607")[None, None, :] * (1 - dens[..., None]) + hex2f(C["blood"])[None, None, :] * dens[..., None]
    base = base * (0.55 + 0.45 * depth[..., None])
    c.img = c.img * (1 - field[..., None]) + base * field[..., None]
    c.screen(np.exp(-((ys - 1592) / 45) ** 2) * field, "#5e1015", 0.6)
    # distant blooms: short red dashes
    dash = []
    for _ in range(9000):
        t = rng.random() ** 1.4
        y = hz + 4 + t * 170
        x = rng.uniform(-50, DW + 50)
        s = 3 + t * 9
        dash.append(f'<ellipse cx="{x:.0f}" cy="{y:.0f}" rx="{s * 1.3:.1f}" ry="{s * 0.45:.1f}"/>')
    c.comp(c.blur(c.svg_mask("".join(dash)), 1.2) * field, C["lacquer"], 0.75)

    def lilies(n, y0, y1, s0, s1, stem_k=2.6, avoid=None):
        pet, stam, stems = [], [], []
        pts = []
        for _ in range(n):
            t = rng.random()
            y = y0 + (y1 - y0) * t
            x = rng.uniform(-80, DW + 80)
            pts.append((x, y, s0 + (s1 - s0) * t * rng.uniform(0.75, 1.2)))
        pts.sort(key=lambda p: p[1])
        for x, y, sz in pts:
            stems.append(f'<path d="M{x:.0f},{y:.0f} q{rng.uniform(-6, 6) * sz / 40:.1f},{sz * stem_k * 0.5:.0f} '
                         f'{rng.uniform(-10, 10) * sz / 40:.1f},{sz * stem_k:.0f}" stroke-width="{max(1.6, sz * 0.045):.1f}"/>')
            p, st = F.spider_lily(x, y, sz, rng)
            pet.extend(p)
            stam.extend((d, ex, ey, sz) for d, ex, ey in st)
        return pet, stam, stems

    def draw_lilies(pet, stam, stems, col, col_hi, blur=0.0, stem_col="#070404"):
        sm = c.svg_mask('<g fill="none" stroke="#fff">' + "".join(stems) + "</g>")
        c.comp(c.blur(sm, blur) if blur else sm, stem_col)
        pm = c.svg_mask("".join(f'<path d="{d}"/>' for d in pet))
        pm = c.blur(pm, blur) if blur else pm
        c.comp(pm, col)
        st = c.svg_mask("".join(f'<path d="{d}" fill="none" stroke="#fff" stroke-width="{max(1.2, sz * 0.012):.1f}"/>'
                                f'<circle cx="{ex:.0f}" cy="{ey:.0f}" r="{max(1.6, sz * 0.02):.1f}"/>' for d, ex, ey, sz in stam))
        st = c.blur(st, blur) if blur else st
        c.comp(st, col_hi, 0.95)

    p, st, sm = lilies(900, 1700, 1860, 18, 40)
    draw_lilies(p, st, sm, "#9e1a20", "#c2262c")
    p, st, sm = lilies(260, 1860, 2020, 42, 80)
    draw_lilies(p, st, sm, C["lacquer"], C["crimson"])

    # cool moonlight bloom (before the figure, so the silhouette stays ink-black)
    c.screen(c.blur(moon, 60), "#c9b8a8", 0.16)

    # the samurai, standing in the lilies against the moon
    fig = F.samurai_stand(2290, 1985, 1190, flip=False, wind=1.15, seed=5)
    fm = c.svg_mask(fig.svg())
    c.comp(c.blur(fm, 14), "#000000", 0.45)
    c.comp(fm, "#050404")
    c.comp(c.svg_mask(fig.svg(tags=["sash"])), C["lacquer"])
    # rim of moonlight on the edges facing the moon
    rim = np.clip(fm - np.roll(c.blur(fm, 2.5), (-int(3 * c.k) or -1, int(3 * c.k) or 1), (0, 1)), 0, 1)
    c.screen(rim * smoothstep(1700, 300, ys) , "#f2e8da", 0.6)

    # foreground lilies in front of his feet, then the closest, biggest ones
    p, st, sm = lilies(120, 1960, 2080, 70, 120)
    draw_lilies(p, st, sm, C["lacquer"], C["crimson"])
    big = []
    for fx, fy, fs in [(240, 1990, 360), (620, 2130, 260), (3560, 2010, 330), (3200, 2160, 220), (1500, 2190, 200)]:
        pp, ss = F.spider_lily(fx, fy, fs, rng)
        draw_lilies(pp, [(d, ex, ey, fs) for d, ex, ey in ss],
                    [f'<path d="M{fx},{fy} q{fs * 0.1:.0f},{fs * 0.8:.0f} {fs * 0.05:.0f},{fs * 1.6:.0f}" stroke-width="{fs * 0.04:.0f}"/>'],
                    C["lacquer"], C["vermilion"], blur=3.5)

    # petals riding the wind (right to left), a few close and soft
    c.comp(c.svg_mask(petals_svg(rng, 240, (0, 250, DW, 1800), 19)), C["crimson"], 0.95)
    c.comp(c.blur(c.svg_mask(petals_svg(rng, 30, (0, 150, DW, 1900), 34)), 6), C["lacquer"], 0.9)


SCENES = {
    "Higanbana": ("Higanbana", scene_higanbana, 0.03, 0.45),
}


def render(key, w, h, seed=None):
    name, fn, grain, vig = SCENES[key]
    rw, rh = w, h
    if abs(w / h - 16 / 9) > 0.01:            # render 16:9 that covers, then crop
        if w / h > 16 / 9:
            rh = round(w * 9 / 16)
        else:
            rw = round(h * 16 / 9)
    c = Canvas(rw, rh, "#000000")
    fn(c, random.Random(seed if seed is not None else hash(key) % 10000))
    im = c.finish(grain=grain, vignette=vig, seed=7)
    if (rw, rh) != (w, h):
        l, t = (rw - w) // 2, (rh - h) // 2
        im = im.crop((l, t, l + w, t + h))
    return im


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--scene", nargs="*", default=None, help="scene keys (default: all)")
    ap.add_argument("--res", default="3840x2160")
    ap.add_argument("--out", default="wallpapers")
    ap.add_argument("--quality", type=int, default=92)
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()
    if a.list:
        for k, v in SCENES.items():
            print(f"{k:14s} {v[0]}")
        return
    w, h = (int(v) for v in a.res.lower().split("x"))
    os.makedirs(a.out, exist_ok=True)
    for key in a.scene or SCENES:
        if key not in SCENES:
            sys.exit(f"unknown scene {key}; try --list")
        im = render(key, w, h, seed=sum(map(ord, key)))
        path = os.path.join(a.out, f"GhostOfTsushima-{key}-{w}x{h}.jpg")
        im.save(path, quality=a.quality, optimize=True, progressive=True, subsampling=0)
        print(path)


if __name__ == "__main__":
    main()

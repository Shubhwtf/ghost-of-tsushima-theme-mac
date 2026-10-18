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
    stream = bez((3900, 1650), (2900, 1250), (1500, 1100), (-100, 450), 200)
    near, far_ = [], []
    for i in range(120):
        px, py = stream[rng.randrange(200)]
        px += rng.gauss(0, 170)
        py += rng.gauss(0, 120)
        sz = rng.uniform(9, 22)
        far_.append(f'<path d="{F.leaf_path(px, py, sz, rng.uniform(-0.9, 0.6), "petal")}"/>')
    for i in range(14):
        px, py = stream[rng.randrange(200)]
        near.append(f'<path d="{F.leaf_path(px + rng.gauss(0, 300), py + rng.gauss(0, 250), rng.uniform(26, 40), rng.uniform(-0.9, 0.6), "petal")}"/>')
    c.comp(c.svg_mask("".join(far_)), C["crimson"], 0.95)
    c.comp(c.blur(c.svg_mask("".join(near)), 5), C["lacquer"], 0.9)


# ------------------------------------------------------------------ shared ink pieces
def washi(c, seed, base="#ece6dc", warm=0.0):
    """Washi paper: soft cloudy density plus fine fibres."""
    xs, ys = c.grid()
    c.img[:] = hex2f(base)
    cloud = c.noise(4, 6, seed, stretch=1.3)
    c.img *= (0.965 + 0.06 * cloud)[..., None]
    rng = random.Random(seed)
    fib = []
    for _ in range(2600):
        x, y = rng.uniform(0, DW), rng.uniform(0, DH)
        a = rng.uniform(0, math.pi)
        L = rng.uniform(10, 60)
        fib.append(f'<path d="M{x:.0f},{y:.0f} q{math.cos(a) * L / 2 + rng.uniform(-6, 6):.0f},{math.sin(a) * L / 2:.0f} '
                   f'{math.cos(a) * L:.0f},{math.sin(a) * L:.0f}"/>')
    m = c.svg_mask('<g fill="none" stroke="#fff" stroke-width="1.6">' + "".join(fib) + "</g>")
    c.comp(m, "#c9bfae", 0.25)
    c.screen(c.radial(DW / 2, DH * 0.45, 2600, 1.5), "#fffaf0", 0.25 + warm)


def hanko(c, x, y, size, text, color=None, font="ShipporiMincho", rot=0.0, seed=1):
    """Red seal: square with uneven, worn edges and carved white characters."""
    color = color or C["lacquer"]
    h = size / 2
    sq = (f'<rect x="{x - h:.1f}" y="{y - h:.1f}" width="{size:.1f}" height="{size:.1f}" rx="{size * 0.06:.1f}" '
          f'transform="rotate({rot} {x} {y})"/>')
    chars = list(text)
    if len(chars) == 2:
        g = glyphs.text_svg(text, x, y - size * 0.40, size * 0.40, font, vertical=True, spacing=0.02)
    else:
        g = glyphs.text_svg(text, x, y + size * 0.22, size * 0.62, font)
    seal = c.svg_mask(sq)
    carve = c.svg_mask(f'<g transform="rotate({rot} {x} {y})"><rect x="{x - h * 0.84:.1f}" y="{y - h * 0.84:.1f}" '
                       f'width="{size * 0.84:.1f}" height="{size * 0.84:.1f}" fill="none" stroke="#fff" '
                       f'stroke-width="{size * 0.035:.1f}"/>{g}</g>')
    wear = c.noise(40, 4, seed + 900)
    ink = seal * (1 - carve) * np.clip(1.25 - 0.9 * smoothstep(0.55, 0.85, wear), 0, 1)
    c.comp(ink, color, 0.95)
    return ink


def pine(c, x, y, h, seed, color="#141212", lean=1.0):
    """Sumi-e black pine: a twisting trunk and flat cloud-like needle pads."""
    rng = random.Random(seed)
    trunk = catmull_pts([(x, y), (x + 30 * lean, y - h * 0.3), (x - 20 * lean, y - h * 0.55),
                         (x + 60 * lean, y - h * 0.8), (x + 40 * lean, y - h)], 30)
    m = c.brush(trunk, h * 0.06, seed=seed, bristles=60, dry=0.35, taper=(0.02, 0.4), ink_decay=0.2)
    pads = []
    for i in range(7):
        t = 0.35 + 0.65 * i / 6
        px, py = trunk[int(t * (len(trunk) - 1))]
        side = 1 if i % 2 else -1
        bx = px + side * rng.uniform(0.15, 0.4) * h
        by = py - rng.uniform(0, 0.05) * h
        pads.append(f'<path d="M{px:.0f},{py:.0f} Q{(px + bx) / 2:.0f},{py - 20:.0f} {bx:.0f},{by:.0f}" fill="none" '
                    f'stroke="#fff" stroke-width="{h * 0.015:.0f}"/>')
        for j in range(9):
            cx = bx + rng.uniform(-0.13, 0.13) * h
            cy = by + rng.uniform(-0.035, 0.015) * h
            r = h * rng.uniform(0.035, 0.06)
            for q in range(26):
                ang = math.pi * (1.05 + 0.9 * q / 25) + rng.uniform(-0.04, 0.04)
                L = r * rng.uniform(0.75, 1.0)
                pads.append(f'<line x1="{cx:.1f}" y1="{cy:.1f}" x2="{cx + math.cos(ang) * L:.1f}" '
                            f'y2="{cy + math.sin(ang) * L * 0.8:.1f}" stroke="#fff" stroke-width="{h * 0.0045:.1f}"/>')
    pm = c.svg_mask("".join(pads))
    tex = c.noise(80, 3, seed + 3)
    c.comp(np.maximum(m, pm * (0.8 + 0.2 * tex)), color)


def grass_clump(c, x, base, h, lean, rng, color, plume_col=None, n=9, width=1.0):
    strokes = []
    for i in range(n):
        hx = x + rng.uniform(-0.12, 0.12) * h
        hh = h * rng.uniform(0.65, 1.1)
        ln = lean * rng.uniform(0.7, 1.3)
        strokes.extend((pts, w * width, j == 0) for j, (pts, w) in enumerate(F.pampas(hx, base, hh, ln, rng)))
    stems = np.zeros((c.h, c.w), np.float32)
    plumes = np.zeros((c.h, c.w), np.float32)
    seg = []
    for pts, w, is_stem in strokes:
        d = "M" + " L".join(f"{px:.1f},{py:.1f}" for px, py in pts)
        seg.append((d, w, is_stem))
    sm = c.svg_mask('<g fill="none" stroke="#fff" stroke-linecap="round">' +
                    "".join(f'<path d="{d}" stroke-width="{w:.1f}"/>' for d, w, st in seg if st) + "</g>")
    pm = c.svg_mask('<g fill="none" stroke="#fff" stroke-linecap="round">' +
                    "".join(f'<path d="{d}" stroke-width="{w:.1f}"/>' for d, w, st in seg if not st) + "</g>")
    c.comp(sm, color)
    c.comp(c.blur(pm, 1.2), plume_col or color, 0.9)


# ------------------------------------------------------------------ Torii at Dawn
def scene_torii(c, rng):
    """Sumi-e dawn: ink-wash mountains, a red sun, a torii on the ridge, pampas grass."""
    xs, ys = c.grid()
    washi(c, 5)
    # red sun disc, stamped (slightly uneven)
    sx, sy, sr = 2620, 690, 300
    sun = c.svg_mask(f'<circle cx="{sx}" cy="{sy}" r="{sr}"/>')
    t = c.noise(30, 4, 61)
    c.comp(c.blur(sun, 1.5) * (0.86 + 0.14 * t), C["lacquer"], 0.95)
    c.screen(c.radial(sx, sy, 900, 2.5), "#f4c9a8", 0.25)
    # far peaks: pale ink, tall and pointed, dissolving downward
    layers = [(11, 1150, 560, 4, 1.7, "#b9b1a6", 420), (12, 1330, 520, 5, 1.6, "#978e85", 330),
              (13, 1520, 420, 6, 1.4, "#6d6560", 260), (14, 1700, 300, 7, 1.3, "#3e3835", 220)]
    for i, (seed, base, amp, cells, sharp, col, fade) in enumerate(layers):
        r = ridge(seed, base, amp, cells=cells, sharp=sharp)
        c.comp(wash(c, r, fade, seed + 100, rough=0.5), col, 0.9)
        m = c.noise(4 + i, 5, seed + 200, stretch=6.0)
        band = np.exp(-((ys - (base + 40)) / 110) ** 2) * smoothstep(0.35, 0.75, m)
        c.comp(band, "#f3eee4", 0.85)
    # the near hill and the torii on its crest
    hill = lambda X: 1600 + 0.00055 * (np.asarray(X) - 2950) ** 2 + 14 * np.sin(np.asarray(X) / 140)
    c.comp(wash(c, hill, 420, 77, rough=0.6), "#1d1a19", 1.0)
    edge = catmull_pts([(2050, float(hill(2050))), (2500, float(hill(2500))), (2950, float(hill(2950)) - 4),
                        (3400, float(hill(3400))), (3900, float(hill(3900)))], 40)
    c.comp(c.brush(edge, 26, seed=78, bristles=60, dry=0.45, taper=(0.4, 0.2)), "#141212", 0.9)
    tx = 2900
    tb = float(hill(tx)) + 10
    c.comp(c.svg_mask(F.torii(tx, tb, 360)), "#0e0c0c")
    pine(c, 3420, float(hill(3420)) + 14, 560, seed=8, color="#0e0c0c", lean=-1)
    # mist rolling at the foot of the hill
    mist = c.noise(5, 6, 88, stretch=5.0)
    c.comp(np.exp(-((ys - 1880) / 160) ** 2) * smoothstep(0.3, 0.8, mist), "#ece6dc", 0.9)
    # birds heading for the sun
    birds = []
    for i in range(7):
        bx, by, bs = 1900 + i * 70 + rng.uniform(-30, 30), 520 + abs(i - 3) * 38 + rng.uniform(-10, 10), rng.uniform(12, 18)
        birds.append(f'<path d="M{bx - bs:.0f},{by - bs * 0.2:.0f} Q{bx - bs * 0.4:.0f},{by - bs * 0.6:.0f} {bx:.0f},{by:.0f} '
                     f'Q{bx + bs * 0.4:.0f},{by - bs * 0.6:.0f} {bx + bs:.0f},{by - bs * 0.2:.0f}" fill="none" stroke="#fff" stroke-width="3.5"/>')
    c.comp(c.svg_mask("".join(birds)), "#2a2523")
    # pampas grass in the foreground, leaning with the wind
    for x, h, n in [(160, 900, 12), (520, 700, 9), (820, 520, 7), (3600, 760, 10), (3820, 980, 12)]:
        grass_clump(c, x, DH + 40, h, -1.0, rng, "#1a1716", plume_col="#8f8170", n=n, width=0.6)
    # signature seal
    hanko(c, 300, 300, 150, "対馬", seed=3)


# ------------------------------------------------------------------ Standoff
def grass_field(c, rng, y0, y1, n, h0, h1, lean, col_far, col_near, tip_col=None, tip_amt=0.0, w0=1.5, w1=6.0):
    """Thousands of wind-bent blades, small at the horizon and tall up front."""
    bands = 6
    for band in range(bands):
        lo, hi = band / bands, (band + 1) / bands
        blades, tips = [], []
        for _ in range(n // bands):
            t = rng.uniform(lo, hi)
            y = y0 + (y1 - y0) * t ** 1.6
            x = rng.uniform(-100, DW + 100)
            h = (h0 + (h1 - h0) * t ** 1.8) * rng.uniform(0.6, 1.25)
            ln = lean * rng.uniform(0.6, 1.3)
            tx, ty = x + ln * h * 0.55, y - h
            mx, my = x + ln * h * 0.08, y - h * 0.6
            wd = w0 + (w1 - w0) * t
            blades.append(f'<path d="M{x - wd / 2:.1f},{y:.1f} Q{mx:.1f},{my:.1f} {tx:.1f},{ty:.1f} Q{mx + wd * 0.3:.1f},{my:.1f} {x + wd / 2:.1f},{y:.1f}Z"/>')
            if tip_col and rng.random() < 0.55:
                tips.append(f'<path d="M{mx + (tx - mx) * 0.55:.1f},{my + (ty - my) * 0.55:.1f} L{tx:.1f},{ty:.1f}" '
                            f'stroke="#fff" fill="none" stroke-width="{wd * 0.7:.1f}" stroke-linecap="round"/>')
        tcol = (hex2f(col_far) * (1 - (lo + hi) / 2) + hex2f(col_near) * (lo + hi) / 2)
        c.comp(c.svg_mask("".join(blades)), tcol)
        if tips:
            c.comp(c.svg_mask("".join(tips)), tip_col, tip_amt * (1 - lo * 0.6))


def scene_standoff(c, rng):
    """Two samurai face off in a wind-swept field at dusk; leaves ride the Guiding Wind."""
    xs, ys = c.grid()
    hz = 1420
    c.img = c.vgrad([(0, "#140506"), (0.18, "#3a0b0d"), (0.38, "#8a1c16"), (0.52, "#c8461f"),
                     (0.62, "#eb8a3a"), (0.66, "#f6c070"), (0.70, "#f3c57c"), (1, "#3a1608")])
    sx, sy, sr = 1920, 1300, 300
    c.screen(c.radial(sx, sy, 2200, 2.4), "#ffb860", 0.55)
    c.screen(c.radial(sx, sy, 800, 2.0), "#fff0c8", 0.6)
    sun = c.svg_mask(f'<circle cx="{sx}" cy="{sy}" r="{sr}"/>')
    c.comp(c.blur(sun, 2), "#fff2d2", 0.95)
    # long brushed cloud bands, dark against the glow
    for i in range(9):
        y = rng.uniform(180, 1150)
        x0 = rng.uniform(-400, 2200)
        L = rng.uniform(1200, 2600)
        pts = catmull_pts([(x0, y), (x0 + L * 0.5, y - rng.uniform(-30, 30)), (x0 + L, y + rng.uniform(-20, 20))], 40)
        m = c.brush(pts, rng.uniform(20, 70), seed=200 + i, bristles=70, dry=0.3, taper=(0.35, 0.45))
        col = "#2a0a0a" if y < 700 else "#7a2414"
        c.comp(c.blur(m, 3), col, 0.75 * (1 - y / 1800))
    # distant hills in haze
    r1 = ridge(21, hz - 20, 160, cells=5)
    c.comp(below(c, r1), "#a04a2a", 0.55)
    r2 = ridge(22, hz + 10, 90, cells=8)
    c.comp(below(c, r2), "#5e2316", 0.85)
    # the field
    ground = below(c, lambda X: hz + 25 + 0 * np.asarray(X), 2)
    c.img = c.img * (1 - ground[..., None]) + c.vgrad([(0, "#000000"), (0.66, "#c8782e"), (0.72, "#8a4518"), (1, "#1a0a05")]) * ground[..., None]
    grass_field(c, rng, hz + 20, 1700, 9000, 10, 120, 1.0, "#b8692a", "#5a2a10", tip_col="#ffd28a", tip_amt=0.7, w0=1.2, w1=4)
    # the duellists, backlit
    left = F.samurai_profile(1430, 1690, 620, pose="iai", wind=0.25, seed=31)
    right = F.samurai_profile(2440, 1695, 650, flip=True, pose="hasso", wind=1.2, seed=32)
    for fg in (left, right):
        fm = c.svg_mask(fg.svg())
        c.screen(c.blur(fm, 10), "#ffb35a", 0.35)
        c.comp(fm, "#120806")
    # wind-swept foreground grass, darker and taller
    grass_field(c, rng, 1680, DH + 120, 2600, 120, 760, 1.0, "#3a1a0a", "#0e0604", tip_col="#e8a050", tip_amt=0.55, w0=3, w1=12)
    for x, h in [(120, 1100), (3700, 1000), (3420, 760)]:
        grass_clump(c, x, DH + 60, h, 1.0, rng, "#0c0503", plume_col="#d8a868", n=10, width=0.7)
    # the Guiding Wind: faint white trails with leaves riding them
    trails = []
    for i in range(6):
        y0 = 2050 - i * 60 + rng.uniform(-40, 40)
        pts = bez((-200, y0), (900, y0 - 900 + rng.uniform(-80, 80)), (2700, 1700 - i * 70), (4100, 450 + i * 90), 160)
        a0, a1 = rng.uniform(0.05, 0.3), rng.uniform(0.55, 0.95)
        trails.append((pts[int(a0 * 159):int(a1 * 159)], rng.uniform(2.5, 5)))
    tm = np.zeros((c.h, c.w), np.float32)
    for seg, wdt in trails:
        tm = np.maximum(tm, c.brush(seg, wdt, seed=int(wdt * 100), bristles=6, dry=0.55, taper=(0.45, 0.5)))
    c.screen(c.blur(tm, 2.5), "#fff4e0", 0.35)
    lv = {C["lacquer"]: [], C["vermilion"]: [], C["gold"]: [], "#7a1010": []}
    keys = list(lv)
    for i in range(150):
        seg, _ = trails[rng.randrange(len(trails))]
        px, py = seg[rng.randrange(len(seg))]
        px += rng.gauss(0, 90)
        py += rng.gauss(0, 70)
        if 1250 < px < 2650 and 1000 < py < 1720 and rng.random() < 0.7:
            continue          # keep the duellists readable
        sz = rng.uniform(16, 32)
        kind = "maple" if rng.random() < 0.65 else "petal"
        lv[keys[rng.randrange(4)]].append(f'<path d="{F.leaf_path(px, py, sz, rng.uniform(0, 6.28), kind)}"/>')
    for col, paths in lv.items():
        c.comp(c.svg_mask("".join(paths)), col)
    near = "".join(f'<path d="{F.leaf_path(rng.choice([rng.uniform(150, 1000), rng.uniform(2900, 3700)]), rng.uniform(300, 2000), rng.uniform(45, 75), rng.uniform(0, 6.28), "maple")}"/>' for _ in range(5))
    c.comp(c.blur(c.svg_mask(near), 6), C["lacquer"], 0.9)


# ------------------------------------------------------------------ Kurosawa
def cedar_row(c, rng, base, h0, h1, n, x0=-100, x1=DW + 100):
    """Tall Japanese cedars (sugi): a straight trunk and ragged, drooping
    foliage tiers that widen toward the bottom."""
    out = []
    for _ in range(n):
        x = rng.uniform(x0, x1)
        h = rng.uniform(h0, h1)
        w = h * rng.uniform(0.14, 0.22)
        out.append(f'<rect x="{x - w * 0.035:.0f}" y="{base - h * 0.3:.0f}" width="{w * 0.07:.0f}" height="{h * 0.3:.0f}"/>')
        tiers = rng.randint(7, 11)
        for i in range(tiers):
            t0 = i / tiers
            t1 = (i + 1.6) / tiers
            ytop = base - h + h * 0.82 * t0
            ybot = base - h + h * 0.82 * min(1, t1)
            ww = w * (0.25 + 0.75 * min(1, t1) ** 0.9) * rng.uniform(0.75, 1.15)
            sag = (ybot - ytop) * rng.uniform(0.1, 0.3)
            out.append(f'<path d="M{x:.0f},{ytop:.0f} Q{x + ww * 0.3:.0f},{ytop + (ybot - ytop) * 0.4:.0f} '
                       f'{x + ww * 0.5:.0f},{ybot + sag:.0f} Q{x + ww * 0.1:.0f},{ybot - sag * 0.3:.0f} {x:.0f},{ybot:.0f} '
                       f'Q{x - ww * 0.1:.0f},{ybot - sag * 0.3:.0f} {x - ww * 0.5:.0f},{ybot + sag * 0.8:.0f} '
                       f'Q{x - ww * 0.3:.0f},{ytop + (ybot - ytop) * 0.4:.0f} {x:.0f},{ytop:.0f}Z"/>')
    return "".join(out)


def scene_kurosawa(c, rng):
    """Black and white, heavy rain, grain. Only the maple leaves and his sash are red."""
    xs, ys = c.grid()
    hz = 1500
    c.img = c.vgrad([(0, "#5d5a57"), (0.45, "#8f8b86"), (0.68, "#b3aea7"), (0.70, "#9a958f"), (1, "#3b3836")])
    sky = c.noise(3, 6, 401, stretch=2.5)
    c.multiply((ys < hz) * smoothstep(0.35, 0.8, sky), "#55524f", 0.55)
    # cedar forest in three rain-hazed depths
    for i, (base, h0, h1, n, col, op) in enumerate([(hz + 10, 380, 620, 70, "#7d7974", 0.8),
                                                    (hz + 20, 520, 860, 40, "#5a5652", 0.9),
                                                    (hz + 30, 700, 1150, 18, "#33302e", 0.95)]):
        m = c.svg_mask(cedar_row(c, rng, base, h0, h1, n))
        c.comp(c.blur(m, 6 - 2 * i), col, op)
        c.comp(np.exp(-((ys - (hz - 60)) / 260) ** 2) * (0.4 + 0.6 * c.noise(5, 4, 402 + i, stretch=4)), "#a8a39d", 0.45)
    # wet ground: dark mud with sky-bright puddles
    gnd = below(c, lambda X: hz + 0 * np.asarray(X), 2)
    c.img = c.img * (1 - gnd[..., None]) + c.vgrad([(0, "#000000"), (0.69, "#6a6662"), (1, "#151413")]) * gnd[..., None]
    c.comp(np.exp(-((ys - hz) / 70) ** 2), "#8f8a84", 0.8)
    pud = smoothstep(0.52, 0.6, c.noise(6, 6, 403, stretch=4.0)) * gnd
    c.comp(pud, "#9d9893", 0.75)
    # the samurai
    fig = F.samurai_stand(1560, 1940, 1240, wind=0.6, sash_len=1.25, seed=41, cape=False)
    fm = c.svg_mask(fig.svg())
    sash = c.svg_mask(fig.svg(tags=["sash"]))
    # reflection in the puddles
    feet = int(1940 * c.k)
    refl = np.zeros_like(fm)
    span = min(feet, c.h - feet)
    refl[feet:feet + span] = fm[feet - 1:feet - 1 - span:-1] if span > 0 else 0
    rs = np.zeros_like(sash)
    rs[feet:feet + span] = sash[feet - 1:feet - 1 - span:-1]
    ripple = 1 - 0.5 * smoothstep(0.4, 0.7, c.noise(60, 3, 404, stretch=8))
    c.comp(c.blur(refl, 4) * pud * ripple, "#1a1918", 0.85)
    c.comp(c.blur(rs, 4) * pud * ripple, C["blood"], 0.85)
    c.comp(c.blur(fm, 6), "#000000", 0.3)
    c.comp(fm, "#0e0d0d")
    c.comp(sash, C["lacquer"])
    # falling maple leaves (the only colour besides the sash)
    leaves = "".join(f'<path d="{F.leaf_path(rng.uniform(0, DW), rng.uniform(100, 1900), rng.uniform(24, 46), rng.uniform(0, 6.28), "maple")}"/>' for _ in range(34))
    c.comp(c.svg_mask(leaves), C["lacquer"])
    ground_leaves = "".join(f'<path d="{F.leaf_path(rng.uniform(0, DW), rng.uniform(1750, 2140), rng.uniform(30, 50), rng.uniform(0, 6.28), "maple")}"/>' for _ in range(16))
    c.comp(c.svg_mask(ground_leaves), C["blood"])
    # rain: fine far streaks, heavy near streaks, splashes
    ang = math.radians(78)
    far, near = [], []
    for _ in range(7000):
        x, y = rng.uniform(-300, DW + 100), rng.uniform(-100, DH)
        L = rng.uniform(40, 140)
        far.append(f'<line x1="{x:.0f}" y1="{y:.0f}" x2="{x + math.cos(ang) * L:.0f}" y2="{y + math.sin(ang) * L:.0f}"/>')
    for _ in range(420):
        x, y = rng.uniform(-300, DW + 100), rng.uniform(-200, DH)
        L = rng.uniform(220, 520)
        near.append(f'<line x1="{x:.0f}" y1="{y:.0f}" x2="{x + math.cos(ang) * L:.0f}" y2="{y + math.sin(ang) * L:.0f}"/>')
    c.screen(c.svg_mask(f'<g stroke="#fff" stroke-width="1.6" stroke-linecap="round">{"".join(far)}</g>'), "#e8e4de", 0.32)
    c.screen(c.blur(c.svg_mask(f'<g stroke="#fff" stroke-width="3.5" stroke-linecap="round">{"".join(near)}</g>'), 2.5), "#f2eee8", 0.4)
    spl = []
    for _ in range(380):
        t = rng.random() ** 1.5
        y = hz + 20 + t * (DH - hz)
        x = rng.uniform(0, DW)
        r = 3 + t * 16
        spl.append(f'<ellipse cx="{x:.0f}" cy="{y:.0f}" rx="{r:.1f}" ry="{r * 0.28:.1f}" fill="none" stroke="#fff" stroke-width="{1 + t * 2:.1f}"/>')
    c.screen(c.blur(c.svg_mask("".join(spl)), 1.2), "#d8d4ce", 0.28)
    # rain haze and a cold contrast curve, keeping the reds
    c.screen(c.noise(4, 5, 405, stretch=1.5) * 0.25, "#ffffff", 0.3)
    g = c.img.mean(axis=2, keepdims=True)
    red = np.clip((c.img[..., :1] - c.img[..., 1:2]) * 3, 0, 1)
    bw = np.clip((g - 0.5) * 1.18 + 0.5, 0, 1) * np.array([1.0, 0.99, 0.97], np.float32)
    c.img = bw * (1 - red) + c.img * red


SCENES = {
    "Higanbana": ("Higanbana", scene_higanbana, 0.03, 0.45),
    "ToriiAtDawn": ("Torii at Dawn", scene_torii, 0.022, 0.25),
    "Standoff": ("Standoff", scene_standoff, 0.03, 0.5),
    "Kurosawa": ("Kurosawa", scene_kurosawa, 0.06, 0.6),
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

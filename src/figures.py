"""Samurai, torii, spider lilies, pampas grass and leaves as SVG / brush geometry.

Figures are drawn in a local unit space: feet on y=0, the top of the head
(or hat) near y=-100, x pointing the way the figure faces. place() maps them
into the 3840x2160 design space.
"""
import math
import random

from paint import smooth_d


def _tf(pts, ox, oy, s, flip):
    out = []
    for p in pts:
        x, y = p[0], p[1]
        q = (ox + (-x if flip else x) * s, oy + y * s)
        out.append(q + ((0,) if len(p) > 2 and p[2] == 0 else ()))
    return out


class Fig:
    """Collects closed shapes / strokes in unit space, emits SVG in design space."""

    def __init__(self, ox, oy, height, flip=False):
        self.ox, self.oy, self.s, self.flip = ox, oy, height / 100.0, flip
        self.parts = []      # (kind, data, extra)

    def shape(self, pts, tension=1.0, tag="body"):
        self.parts.append(("shape", pts, tension, tag))

    def poly(self, pts, tag="body"):
        self.parts.append(("poly", pts, None, tag))

    def line(self, a, b, w, tag="body", cap="round"):
        self.parts.append(("line", (a, b), (w, cap), tag))

    def ellipse(self, c, rx, ry, rot=0, tag="body"):
        self.parts.append(("ell", (c, rx, ry, rot), None, tag))

    def svg(self, tags=None, exclude=()):
        out = []
        for kind, data, extra, tag in self.parts:
            if (tags and tag not in tags) or tag in exclude:
                continue
            if kind == "shape":
                out.append(f'<path d="{smooth_d(_tf(data, self.ox, self.oy, self.s, self.flip), True, extra)}"/>')
            elif kind == "poly":
                q = _tf(data, self.ox, self.oy, self.s, self.flip)
                out.append('<path d="M' + " L".join(f"{x:.2f},{y:.2f}" for x, y, *_ in q) + 'Z"/>')
            elif kind == "line":
                (a, b), (w, cap) = data, extra
                (x1, y1), (x2, y2) = _tf([a, b], self.ox, self.oy, self.s, self.flip)
                out.append(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" '
                           f'stroke="#fff" stroke-width="{w * self.s:.2f}" stroke-linecap="{cap}"/>')
            elif kind == "ell":
                c, rx, ry, rot = data
                (cx, cy), = _tf([c], self.ox, self.oy, self.s, self.flip)
                r = -rot if self.flip else rot
                out.append(f'<ellipse cx="{cx:.2f}" cy="{cy:.2f}" rx="{rx * self.s:.2f}" ry="{ry * self.s:.2f}" '
                           f'transform="rotate({r:.1f} {cx:.2f} {cy:.2f})"/>')
        return f'<g fill="#fff" stroke="none">{"".join(out)}</g>'


def _blade(f, hilt_a, hilt_b, tip, curve=0.06, width=1.15, tag="blade"):
    """Katana: tsuka (hilt a->b), tsuba disc at b, curved blade b->tip."""
    ax, ay = hilt_a
    bx, by = hilt_b
    tx, ty = tip
    f.line(hilt_a, hilt_b, 1.55, tag=tag)
    # tsuba (guard), perpendicular to the blade
    dx, dy = tx - bx, ty - by
    L = math.hypot(dx, dy)
    ux, uy = dx / L, dy / L
    nx, ny = -uy, ux
    f.ellipse((bx + ux * 0.3, by + uy * 0.3), 0.8, 2.1, math.degrees(math.atan2(uy, ux)), tag=tag)
    # blade as a thin curved sliver with a sharp kissaki
    pts = []
    n = 14
    for i in range(n + 1):
        t = i / n
        bend = curve * L * math.sin(math.pi * t * 0.9) * 0.5 + curve * L * t * t * 0.5
        w = width * (1 - 0.35 * t)
        cx = bx + ux * L * t + nx * bend
        cy = by + uy * L * t + ny * bend
        pts.append((cx + nx * w * 0.5, cy + ny * w * 0.5))
    back = []
    for i in range(n, -1, -1):
        t = i / n
        bend = curve * L * math.sin(math.pi * t * 0.9) * 0.5 + curve * L * t * t * 0.5
        w = width * (1 - 0.35 * t)
        cx = bx + ux * L * t + nx * bend
        cy = by + uy * L * t + ny * bend
        back.append((cx - nx * w * 0.5, cy - ny * w * 0.5))
    tipx = bx + ux * (L + 1.8) + nx * (curve * L * 0.9)
    tipy = by + uy * (L + 1.8) + ny * (curve * L * 0.9)
    f.poly(pts + [(tipx, tipy)] + back, tag=tag)


def _ribbon(f, root, direction, length, width, waves, phase, droop, tag, seed=0, fray=0):
    """A cloth strip streaming in the wind from root: wavy, tapering."""
    rng = random.Random(seed)
    dx, dy = direction
    L = math.hypot(dx, dy)
    ux, uy = dx / L, dy / L
    nx, ny = -uy, ux
    n = 22
    top, bot = [], []
    for i in range(n + 1):
        t = i / n
        wave = math.sin(t * waves * math.pi * 2 + phase) * width * 0.9 * t
        sag = droop * t * t
        cx = root[0] + ux * length * t + nx * wave
        cy = root[1] + uy * length * t + ny * wave + sag
        w = width * (1 - 0.75 * t ** 1.3)
        top.append((cx + nx * w / 2, cy + ny * w / 2))
        bot.append((cx - nx * w / 2, cy - ny * w / 2))
    f.shape(top + list(reversed(bot)), tension=1.0, tag=tag)


def samurai_stand(ox, oy, height, flip=False, wind=1.0, sash_len=1.0, seed=3, cape=True, hat="kasa"):
    """Lone samurai, three-quarter front view, legs planted wide, katana drawn
    and held low to his side, cloak and sash streaming downwind (toward -x)."""
    f = Fig(ox, oy, height, flip)
    w = wind
    # --- cloak behind the body: hangs from the shoulders, blown back and down
    if cape:
        f.shape([(7, -80.5), (0, -82.2), (-8, -81.6), (-15, -79.6), (-22 - 6 * w, -76.5), (-29 - 12 * w, -72),
                 (-36 - 17 * w, -66.5), (-41 - 21 * w, -61.5, 0), (-34 - 17 * w, -60.8), (-37 - 18 * w, -55.5, 0),
                 (-29 - 13 * w, -55.6), (-31 - 13 * w, -49.5, 0), (-23 - 9 * w, -50.5), (-23 - 7 * w, -44.5, 0),
                 (-16 - 3 * w, -47.5), (-11, -53), (-8.5, -62), (-5, -72)], tension=1.0, tag="cape")
    # --- sash (obi) tails streaming ---------------------------------------
    _ribbon(f, (-6.5, -57.2), (-1, 0.14), 30 * sash_len * w + 6, 2.1, 1.6, 0.4, 3.0, "sash", seed)
    _ribbon(f, (-6.5, -56.2), (-1, 0.26), 24 * sash_len * w + 5, 1.8, 1.3, 2.1, 4.5, "sash", seed + 1)
    f.shape([(-8.0, -58.8), (8.0, -59.1), (8.3, -56.0), (-8.3, -55.7)], tension=0.3, tag="sash")
    # --- hakama: wide pleated trousers, flaring, pushed by the wind ----------
    f.shape([(-8.3, -56.5), (-10.2, -45), (-13.6, -29), (-17.2 - 1.5 * w, -13), (-20.5 - 2.5 * w, -2.0, 0),
             (-17, -1.1), (-14.0, -0.6, 0), (-11.3, -3), (-8.6, -12), (-4.2, -24), (0.4, -27.5, 0),
             (4.4, -24), (8.5, -12), (11.0, -3), (12.8, -0.6, 0), (16.5, -1.0), (19.2, -1.5, 0),
             (17.6, -11), (14.6, -27), (11.4, -44), (8.6, -56.8)], tension=0.9, tag="body")
    f.shape([(-19.3, -0.2), (-18.8, -2.2), (-13.8, -2.6), (-11.8, -0.9), (-12.3, 0.4, 0), (-19.6, 0.4, 0)], 0.6)
    f.shape([(11.6, -1.0), (13.3, -2.6), (18.5, -2.2), (21.2, -0.4), (21.2, 0.4, 0), (12.0, 0.4, 0)], 0.6)
    # --- torso: broad shoulders tapering to the obi ---------------------------
    f.shape([(-7.8, -57.5), (-9.4, -66), (-10.9, -74), (-10.2, -78.4), (-4.5, -80.6), (0, -81.0),
             (4.5, -80.6), (10.4, -78.6), (11.1, -74), (9.6, -66), (8.0, -57.5)], tension=1.0)
    # shoulder armour plates (sode), squared and hanging
    f.poly([(-9.6, -79.8), (-13.8, -78.6), (-15.4, -72.2), (-14.7, -69.6), (-10.9, -70.2), (-9.4, -74.5)])
    f.poly([(9.8, -80.0), (14.0, -78.8), (15.6, -72.6), (15.0, -70.0), (11.1, -70.6), (9.6, -74.5)])
    # left arm: down, hand resting on the hilt at the hip
    f.shape([(-11.2, -76), (-13.6, -70), (-13.6, -63), (-11.8, -57.5), (-8.8, -55.2), (-7.0, -57.0),
             (-9.0, -59.5), (-10.0, -65), (-9.2, -71)], tension=1.0)
    # right arm: holding the katana down and away
    f.shape([(11.0, -76.5), (14.0, -70.5), (15.6, -63), (16.9, -56.5), (18.4, -52.4), (15.9, -51.6),
             (14.0, -55.5), (12.2, -62), (9.8, -70)], tension=1.0)
    # scabbards: katana + wakizashi through the obi, jutting back
    f.line((-3.5, -58.0), (-29, -51.6), 1.5, tag="saya")
    f.line((-1.5, -57.8), (4.0, -59.6), 1.3, tag="saya")
    f.line((-4.5, -56.4), (-21, -52.3), 1.25, tag="saya")
    # drawn katana: hilt in the right hand, blade low toward the ground
    _blade(f, (16.3, -57.0), (17.6, -51.0), (31.0, -10.5), curve=0.05, width=1.1)
    # --- neck, head, hat --------------------------------------------------
    f.shape([(-2.9, -79.8), (-2.6, -84.0), (2.6, -84.0), (2.9, -79.8)], 0.5)
    f.ellipse((0.3, -87.0), 4.4, 5.2, 0)
    _ribbon(f, (-2.8, -88.2), (-1, 0.05), 8 * w + 2, 1.3, 0.8, 0.5, 0.8, "hair", seed + 7)
    if hat == "kasa":
        f.shape([(-17.5, -89.0, 0), (-11.5, -92.0), (-5.2, -96.6), (0.6, -100.4, 0), (6.4, -96.8), (12.4, -91.8),
                 (18.2, -88.2, 0), (11.6, -89.4), (0.5, -90.0), (-9.6, -89.8)], tension=0.8, tag="hat")
    return f


def samurai_profile(ox, oy, height, flip=False, pose="iai", wind=1.0, seed=5, hat="kasa"):
    """Side view. pose 'iai': crouched, hand on hilt, ready to draw.
    pose 'hasso': katana held high beside the head. The figure faces +x."""
    f = Fig(ox, oy, height, flip)
    w = wind
    if pose == "iai":
        # low stance: front leg bent forward, back leg extended
        f.shape([(-6.5, -50.5), (-10.5, -38), (-17.5, -22), (-25.5, -6), (-30.5, -0.8, 0), (-23.5, -0.6),
                 (-20.5, -2.2), (-13.5, -13), (-6.5, -24), (1.5, -27.5), (8.5, -18), (12.5, -6.5),
                 (11.0, -1.2, 0), (20.5, -0.6, 0), (19.5, -6.5), (17.5, -20), (13.5, -34), (8.5, -51)],
                 tension=0.9, tag="body")
        f.shape([(-28.5, 0.4, 0), (-29.0, -1.8), (-23, -2.6), (-21.5, 0.4, 0)], 0.6)
        f.shape([(11.0, 0.4, 0), (11.4, -2.4), (18.5, -2.4), (22.0, -0.4), (22.0, 0.4, 0)], 0.6)
        # torso leaning forward
        f.shape([(-7.5, -52), (-8.5, -62), (-6.5, -72.5), (-1.5, -76.8), (4.5, -76.2), (8.5, -72),
                 (10.5, -63), (9.5, -52)], tension=1.0)
        # sode on the near shoulder
        f.poly([(-3.5, -76), (3.5, -76.5), (5.6, -68.5), (4.2, -66.4), (-2.6, -66.8), (-4.2, -71)])
        # arm reaching across to the hilt at the left hip (front)
        f.shape([(2.2, -74), (6.5, -68), (9.5, -61.5), (13.4, -57.4), (15.8, -55.2), (14.4, -53.2),
                 (10.8, -55.6), (6.2, -59.5), (1.0, -66)], tension=1.0)
        # sheathed katana: hilt forward-up, saya sweeping back-down past the hip
        f.line((19.5, -59.8), (9.5, -55.6), 1.7, tag="saya")
        f.line((9.5, -55.6), (-25, -45.8), 1.8, tag="saya")
        f.ellipse((10.4, -56.0), 0.8, 2.2, -22, tag="saya")
        f.line((7.5, -54.0), (-14.5, -47.8), 1.4, tag="saya")
        # obi tails streaming back
        _ribbon(f, (-7.5, -53), (-1, 0.1), 30 * w + 5, 2.4, 1.5, 0.3, 2.4, "sash", seed)
        _ribbon(f, (-7.5, -52), (-1, 0.22), 23 * w + 4, 2.0, 1.2, 1.8, 3.6, "sash", seed + 1)
        f.shape([(-8, -54.8), (9.8, -55.4), (10.0, -51.2), (-8.2, -50.6)], 0.4, tag="sash")
        head = (2.4, -82.0)
        neck = [(-1.6, -75.5), (-0.8, -79.6), (3.6, -79.6), (4.0, -75.5)]
        cape_root = [(-2.5, -76.5), (-6.5, -74)]
    else:
        # hasso: upright, feet apart, katana raised beside the head
        f.shape([(-7.0, -54.5), (-10.0, -42), (-14.5, -26), (-19.5, -8), (-22.5, -0.8, 0), (-15.5, -0.6),
                 (-13.5, -3.0), (-8.0, -15), (-2.5, -27), (2.0, -29), (6.5, -18), (10.0, -6.5),
                 (9.5, -1.2, 0), (18.5, -0.6, 0), (17.0, -7.5), (14.5, -22), (11.5, -38), (8.0, -55)],
                 tension=0.9, tag="body")
        f.shape([(-21.0, 0.4, 0), (-21.5, -1.8), (-15.5, -2.6), (-14.0, 0.4, 0)], 0.6)
        f.shape([(9.0, 0.4, 0), (9.5, -2.4), (16.5, -2.4), (20.0, -0.4), (20.0, 0.4, 0)], 0.6)
        f.shape([(-7.0, -56), (-7.6, -66), (-6.6, -76), (-2.5, -80.6), (3.0, -80.4), (6.8, -76.5),
                 (8.8, -70), (8.0, -62), (7.4, -56)], tension=1.0)
        f.poly([(-5.0, -80), (2.5, -80.4), (4.0, -72), (2.6, -70), (-4.0, -70.4), (-6.0, -75)])
        # hasso: hands together at the right shoulder, blade up and back
        f.shape([(1.0, -77.5), (6.0, -76.5), (9.6, -73.0), (11.2, -77.5), (10.0, -81.0), (7.5, -80.0),
                 (6.4, -77.4), (2.0, -72.0)], tension=1.0)
        f.shape([(-3.0, -76.5), (-4.4, -71.0), (0.5, -69.0), (6.5, -73.6), (10.6, -79.5), (8.6, -81.4),
                 (5.0, -76.6), (0.2, -73.4)], tension=1.0)
        _blade(f, (10.8, -76.6), (9.0, -83.4), (-7.0, -122), curve=-0.05, width=1.15)
        # saya at the hip pointing back
        f.line((7.0, -57.5), (-24, -48.5), 1.8, tag="saya")
        f.line((5.5, -55.8), (-15, -50.0), 1.4, tag="saya")
        _ribbon(f, (-7.6, -56.5), (-1, 0.1), 30 * w + 5, 2.4, 1.5, 1.1, 2.4, "sash", seed)
        _ribbon(f, (-7.6, -55.5), (-1, 0.22), 23 * w + 4, 2.0, 1.2, 2.6, 3.6, "sash", seed + 1)
        f.shape([(-8.2, -58.8), (8.6, -59.2), (8.8, -55.0), (-8.4, -54.6)], 0.4, tag="sash")
        head = (1.2, -86.0)
        neck = [(-2.6, -79.5), (-2.0, -83.6), (2.6, -83.6), (3.0, -79.5)]
        cape_root = [(-3.5, -80.5), (-7.4, -77)]
    f.shape(neck, 0.5)
    f.ellipse(head, 4.1, 4.8, 0)
    hx, hy = head
    _ribbon(f, (hx - 3.2, hy - 1.0), (-1, 0.04), 9 * w + 2, 1.4, 0.8, 0.5, 0.8, "hair", seed + 7)
    # short cloak streaming back from the shoulders
    (ax, ay), (bx, by) = cape_root
    f.shape([(ax + 3, ay - 0.8), (ax - 4, ay - 1.2), (ax - 9 * w - 3, ay + 2.5), (ax - 16 * w - 4, ay + 8),
             (ax - 22 * w - 4, ay + 14, 0), (ax - 16 * w - 4, ay + 14.5), (ax - 18 * w - 4, ay + 19.5, 0),
             (ax - 11 * w - 3, ay + 19), (ax - 11 * w - 3, ay + 24, 0), (ax - 6 * w - 2, ay + 21),
             (bx, by + 16), (bx + 2, by + 2)], tension=1.0, tag="cape")
    if hat == "kasa":
        f.shape([(hx - 17.5, hy - 1.2, 0), (hx - 11, hy - 4.4), (hx - 4.5, hy - 8.8), (hx + 1.2, hy - 12.4, 0),
                 (hx + 7.5, hy - 9.0), (hx + 13.5, hy - 4.4), (hx + 19.0, hy - 0.4, 0), (hx + 12, hy - 1.6),
                 (hx + 1, hy - 2.2), (hx - 9, hy - 2.0)], tension=0.8, tag="hat")
    return f


# ------------------------------------------------------------------ torii
def torii(cx, base, height):
    """Myojin torii: curved kasagi, nuki, gakuzuka, slightly splayed pillars."""
    s = height / 100.0

    def P(x, y):
        return f"{cx + x * s:.2f},{base + y * s:.2f}"
    parts = []
    # pillars (hashira), splayed, with kamebara bases
    for side in (-1, 1):
        x0, x1 = side * 30, side * 27.5
        parts.append(f'<path d="M{P(x0 - 3.2, 0)} L{P(x1 - 2.6, -86)} L{P(x1 + 2.6, -86)} L{P(x0 + 3.2, 0)}Z"/>')
        parts.append(f'<path d="M{P(x0 - 5.2, 0)} L{P(x0 - 4.6, -6.5)} L{P(x0 + 4.6, -6.5)} L{P(x0 + 5.2, 0)}Z"/>')
    # nuki (lower crossbeam), protruding through the pillars
    parts.append(f'<path d="M{P(-41, -71)} L{P(41, -71)} L{P(41, -64.6)} L{P(-41, -64.6)}Z"/>')
    # gakuzuka (central strut)
    parts.append(f'<path d="M{P(-2.6, -86)} L{P(2.6, -86)} L{P(2.6, -71)} L{P(-2.6, -71)}Z"/>')
    # shimaki + kasagi: upswept top beam
    parts.append(f'<path d="M{P(-44, -84.5)} L{P(44, -84.5)} L{P(44, -89.5)} L{P(-44, -89.5)}Z"/>')
    parts.append(f'<path d="M{P(-56, -99.5)} C{P(-44, -95)} {P(-20, -93.6)} {P(0, -93.6)} '
                 f'C{P(20, -93.6)} {P(44, -95)} {P(56, -99.5)} L{P(54.5, -93.6)} '
                 f'C{P(42, -89.6)} {P(20, -88.6)} {P(0, -88.6)} C{P(-20, -88.6)} {P(-42, -89.6)} {P(-54.5, -93.6)}Z"/>')
    return f'<g fill="#fff">{"".join(parts)}</g>'


# ------------------------------------------------------------------ flowers / grass
def spider_lily(cx, cy, size, rng, open_=1.0):
    """Higanbana head: 5-7 florets, each with six narrow recurved petals and
    long upswept stamens. Returns (petal_svg, stamen_svg) path strings."""
    petals, stamens = [], []
    n = rng.randint(5, 7)
    for i in range(n):
        a = -math.pi / 2 + (i - (n - 1) / 2) * (math.pi * 1.5 / n) + rng.uniform(-0.2, 0.2)
        d = size * rng.uniform(0.12, 0.22)
        fx, fy = cx + math.cos(a) * d, cy + math.sin(a) * d * 0.7
        # petals: thin arcs curling back toward the centre
        for j in range(6):
            pa = a + (j - 2.5) * 0.45 + rng.uniform(-0.15, 0.15)
            L = size * rng.uniform(0.26, 0.36) * open_
            x1, y1 = fx + math.cos(pa) * L * 0.55, fy + math.sin(pa) * L * 0.55 - L * 0.12
            x2, y2 = fx + math.cos(pa) * L, fy + math.sin(pa) * L * 0.6 + L * 0.18
            wd = size * 0.045
            nxp, nyp = -math.sin(pa) * wd, math.cos(pa) * wd
            petals.append(f'M{fx:.1f},{fy:.1f} Q{x1 + nxp:.1f},{y1 + nyp:.1f} {x2:.1f},{y2:.1f} '
                          f'Q{x1 - nxp * 0.2:.1f},{y1 - nyp * 0.2:.1f} {fx:.1f},{fy:.1f}Z')
        # stamens: long, curving upward and outward, with anther dots
        for j in range(6):
            sa = a + (j - 2.5) * 0.18 + rng.uniform(-0.1, 0.1)
            L = size * rng.uniform(0.75, 1.05)
            ex = fx + math.cos(sa) * L * 0.85
            ey = fy + math.sin(sa) * L * 0.5 - L * 0.35
            mx = fx + math.cos(sa) * L * 0.55
            my = fy + math.sin(sa) * L * 0.45 + L * 0.05
            stamens.append((f'M{fx:.1f},{fy:.1f} Q{mx:.1f},{my:.1f} {ex:.1f},{ey:.1f}', ex, ey))
    return petals, stamens


def pampas(x, base, height, lean, rng):
    """Susuki: a curved stem and a drooping feathery plume, as dense polylines
    for the brush. Returns list of (points, width)."""
    strokes = []
    top = (x + lean * height * 0.35, base - height)
    c1 = (x + lean * height * 0.05, base - height * 0.4)
    c2 = (x + lean * height * 0.2, base - height * 0.8)
    from paint import bez
    stem = bez((x, base), c1, c2, top, 30)
    strokes.append((stem, height * 0.012))
    # plume: many fine strands hanging downwind from the top third
    for i in range(18):
        t = rng.uniform(0.0, 0.32)
        sx, sy = stem[int((1 - t) * 29)]
        L = height * rng.uniform(0.12, 0.28)
        ang = math.radians(rng.uniform(15, 55))
        ex = sx + lean * math.cos(ang) * L
        ey = sy + math.sin(ang) * L * 0.6 - L * 0.15
        mx, my = sx + lean * L * 0.4, sy - L * 0.25
        strokes.append((bez((sx, sy), (mx, my), (mx + lean * L * 0.3, my), (ex, ey), 12), height * 0.006))
    return strokes


def leaf_path(x, y, size, angle, kind="maple"):
    """A small leaf shape centred at x, y in design units."""
    if kind == "maple":
        # Japanese maple: seven slender pointed lobes, deep notches, a short stem
        pts = []
        lobes = [(-2.3, 0.5), (-1.55, 0.78), (-0.78, 0.95), (0.0, 1.0), (0.78, 0.95), (1.55, 0.78), (2.3, 0.5)]
        for i, (a, r) in enumerate(lobes):
            a -= math.pi / 2
            pts.append((math.cos(a - 0.3) * r * size * 0.55, math.sin(a - 0.3) * r * size * 0.55))
            pts.append((math.cos(a - 0.07) * r * size * 0.86, math.sin(a - 0.07) * r * size * 0.86))
            pts.append((math.cos(a) * r * size, math.sin(a) * r * size))
            pts.append((math.cos(a + 0.07) * r * size * 0.86, math.sin(a + 0.07) * r * size * 0.86))
            pts.append((math.cos(a + 0.3) * r * size * 0.55, math.sin(a + 0.3) * r * size * 0.55))
            if i < len(lobes) - 1:
                na = (a + lobes[i + 1][0] - math.pi / 2) / 2
                pts.append((math.cos(na) * size * 0.3, math.sin(na) * size * 0.3))
        pts += [(size * 0.04, size * 0.12), (size * 0.05, size * 0.55), (-size * 0.02, size * 0.55), (-size * 0.04, size * 0.12)]
        pts = [(px * math.cos(angle) - py * math.sin(angle) + x, px * math.sin(angle) + py * math.cos(angle) + y)
               for px, py in pts]
        return "M" + " L".join(f"{px:.1f},{py:.1f}" for px, py in pts) + "Z"
    # simple almond leaf / petal
    ca, sa = math.cos(angle), math.sin(angle)
    def R(px, py):
        return f"{px * ca - py * sa + x:.1f},{px * sa + py * ca + y:.1f}"
    return (f"M{R(-size, 0)} Q{R(0, -size * 0.55)} {R(size, 0)} Q{R(0, size * 0.55)} {R(-size, 0)}Z")

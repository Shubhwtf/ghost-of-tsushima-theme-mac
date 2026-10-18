"""A tiny ink-painting engine: float32 compositing, smooth blurs, fBm noise,
SVG shape masks (via rsvg-convert) and a bristle brush.

Every coordinate is given in a 3840x2160 design space and scaled to the
output size, so one scene renders at 1080p, 4K or 5K without changes.
"""
import math
import random
import subprocess

import numpy as np
from PIL import Image, ImageDraw

DW, DH = 3840, 2160


def hex2f(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)], dtype=np.float32)


# ------------------------------------------------------------------ blur
def _box(a, r, axis):
    """Box blur of radius r along axis using a cumulative sum (edge-clamped)."""
    if r < 1:
        return a
    pad = [(0, 0)] * a.ndim
    pad[axis] = (r + 1, r)
    p = np.pad(a, pad, mode="edge")
    c = np.cumsum(p, axis=axis, dtype=np.float32)
    n = a.shape[axis]
    hi = np.take(c, np.arange(2 * r + 1, 2 * r + 1 + n), axis=axis)
    lo = np.take(c, np.arange(0, n), axis=axis)
    return (hi - lo) / (2 * r + 1)


def gblur(a, sigma):
    """Gaussian blur (three box passes) in float, no clipping, no rings.
    Large sigmas are done on a downsampled copy for speed."""
    if sigma < 0.5:
        return a
    a = a.astype(np.float32)
    if sigma > 24:
        f = int(sigma // 8)
        h, w = a.shape[:2]
        small = _resize(a, max(2, w // f), max(2, h // f))
        small = gblur(small, sigma / f)
        return _resize(small, w, h)
    r = max(1, int(round(math.sqrt(12 * sigma * sigma / 3 + 1) / 2)))
    for _ in range(3):
        a = _box(a, r, 0)
        a = _box(a, r, 1)
    return a


def _resize(a, w, h):
    if a.ndim == 2:
        return np.asarray(Image.fromarray(a.astype(np.float32), "F").resize((w, h), Image.BICUBIC))
    return np.stack([_resize(a[..., i], w, h) for i in range(a.shape[2])], axis=-1)


# ------------------------------------------------------------------ noise
def value_noise(w, h, cells_x, cells_y, rng):
    g = rng.random((cells_y + 3, cells_x + 3)).astype(np.float32)
    big = _resize(g, int(w * (cells_x + 3) / cells_x), int(h * (cells_y + 3) / cells_y))
    ox = int(w / cells_x)
    oy = int(h / cells_y)
    return big[oy:oy + h, ox:ox + w]


def fbm(w, h, base_cells, octaves=5, seed=0, stretch=1.0, gain=0.5):
    """Fractal noise in 0..1. stretch > 1 elongates features horizontally."""
    rng = np.random.default_rng(seed)
    out = np.zeros((h, w), np.float32)
    amp, tot = 1.0, 0.0
    for o in range(octaves):
        cx = max(1, int(base_cells * 2 ** o / stretch))
        cy = max(1, int(base_cells * 2 ** o * h / w))
        if cx > w // 2 or cy > h // 2:
            break
        out += amp * value_noise(w, h, cx, cy, rng)
        tot += amp
        amp *= gain
    return out / tot


def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


# ------------------------------------------------------------------ paths
def smooth_d(pts, closed=True, tension=1.0):
    """Catmull-Rom spline through pts -> SVG path data. A point given as
    (x, y, 0) is a sharp corner."""
    P = [(p[0], p[1]) for p in pts]
    sharp = [len(p) > 2 and p[2] == 0 for p in pts]
    n = len(P)
    f = lambda q: f"{q[0]:.2f},{q[1]:.2f}"
    d = f"M{f(P[0])}"
    rng_ = range(n) if closed else range(n - 1)
    for i in rng_:
        p0 = P[(i - 1) % n] if (closed or i > 0) else P[i]
        p1, p2 = P[i], P[(i + 1) % n]
        p3 = P[(i + 2) % n] if (closed or i + 2 < n) else P[(i + 1) % n]
        t = tension / 6
        c1 = p1 if sharp[i] else (p1[0] + (p2[0] - p0[0]) * t, p1[1] + (p2[1] - p0[1]) * t)
        c2 = p2 if sharp[(i + 1) % n] else (p2[0] - (p3[0] - p1[0]) * t, p2[1] - (p3[1] - p1[1]) * t)
        d += f" C{f(c1)} {f(c2)} {f(p2)}"
    return d + ("Z" if closed else "")


def bez(p0, p1, p2, p3, n):
    out = []
    for i in range(n):
        t = i / (n - 1)
        u = 1 - t
        out.append((u ** 3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t ** 3 * p3[0],
                    u ** 3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t ** 3 * p3[1]))
    return out


def catmull_pts(pts, per=24):
    """Dense polyline through control points (open Catmull-Rom)."""
    P = [pts[0]] + list(pts) + [pts[-1]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for j in range(per):
            t = j / per
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1[k]) + (-p0[k] + p2[k]) * t + (2 * p0[k] - 5 * p1[k] + 4 * p2[k] - p3[k]) * t2
                                    + (-p0[k] + 3 * p1[k] - 3 * p2[k] + p3[k]) * t3) for k in (0, 1)))
    out.append(tuple(pts[-1]))
    return out


# ------------------------------------------------------------------ canvas
class Canvas:
    def __init__(self, w, h, bg="#000000"):
        self.w, self.h = w, h
        self.k = w / DW
        self.img = np.empty((h, w, 3), np.float32)
        self.img[:] = hex2f(bg)

    # coordinates ---------------------------------------------------------
    def grid(self):
        """Design-space x, y for every pixel (cached)."""
        if not hasattr(self, "_grid"):
            ys = (np.arange(self.h, dtype=np.float32) + 0.5) / self.k
            xs = (np.arange(self.w, dtype=np.float32) + 0.5) / self.k
            self._grid = (xs[None, :], ys[:, None])
        return self._grid

    def noise(self, cells, octaves=5, seed=0, stretch=1.0, gain=0.5):
        return fbm(self.w, self.h, cells, octaves, seed, stretch, gain)

    # masks -----------------------------------------------------------------
    def svg_mask(self, body, defs=""):
        """Rasterise SVG shapes (paint them white) into a 0..1 float mask."""
        doc = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" '
               f'viewBox="0 0 {DW} {DH}"><defs>{defs}</defs>{body}</svg>')
        png = subprocess.run(["rsvg-convert", "-w", str(self.w), "-h", str(self.h)],
                             input=doc.encode(), capture_output=True, check=True).stdout
        import io
        im = Image.open(io.BytesIO(png)).convert("RGBA")
        a = np.asarray(im, dtype=np.float32)
        return a[..., 3] / 255 * (a[..., 0] / 255)

    def svg_rgba(self, body, defs=""):
        doc = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" '
               f'viewBox="0 0 {DW} {DH}"><defs>{defs}</defs>{body}</svg>')
        png = subprocess.run(["rsvg-convert", "-w", str(self.w), "-h", str(self.h)],
                             input=doc.encode(), capture_output=True, check=True).stdout
        import io
        a = np.asarray(Image.open(io.BytesIO(png)).convert("RGBA"), dtype=np.float32) / 255
        return a[..., :3], a[..., 3]

    def blur(self, a, sigma):
        """sigma in design units."""
        return gblur(a, sigma * self.k)

    # compositing -------------------------------------------------------------
    def comp(self, mask, color, opacity=1.0):
        a = np.clip(mask * opacity, 0, 1)[..., None]
        col = hex2f(color) if isinstance(color, str) else color
        self.img = self.img * (1 - a) + col * a

    def screen(self, mask, color, opacity=1.0):
        a = np.clip(mask * opacity, 0, 1)[..., None]
        col = hex2f(color) if isinstance(color, str) else color
        self.img = 1 - (1 - self.img) * (1 - col * a)

    def multiply(self, mask, color, opacity=1.0):
        a = np.clip(mask * opacity, 0, 1)[..., None]
        col = hex2f(color) if isinstance(color, str) else color
        self.img = self.img * (1 - a + col * a)

    def vgrad(self, stops):
        """Vertical gradient over the whole canvas: [(t, '#hex'), ...]."""
        _, ys = self.grid()
        t = (ys / DH)[:, 0]
        out = np.empty((self.h, 3), np.float32)
        ts = [s[0] for s in stops]
        for c in range(3):
            out[:, c] = np.interp(t, ts, [hex2f(s[1])[c] for s in stops])
        return np.broadcast_to(out[:, None, :], (self.h, self.w, 3)).copy()

    def radial(self, cx, cy, r, falloff=2.0):
        xs, ys = self.grid()
        d = np.sqrt((xs - cx) ** 2 + (ys - cy) ** 2) / r
        return np.clip(1 - d, 0, 1) ** falloff

    # brush -------------------------------------------------------------------
    def brush(self, pts, width, seed=0, bristles=48, dry=0.35, taper=(0.15, 0.35),
              wobble=0.0, ink_decay=0.6, density=1.0, pressure=None):
        """Sumi-e bristle stroke along a polyline (design units).
        width: stroke width; dry: how much the brush breaks up (0 solid .. 1 very dry);
        taper: fraction of length that swells in / thins out.
        Returns a 0..1 mask."""
        rng = random.Random(seed)
        k = self.k
        pts = [(x * k, y * k) for x, y in pts]
        # resample at ~1.5 px spacing
        seg = [0.0]
        for i in range(1, len(pts)):
            seg.append(seg[-1] + math.dist(pts[i - 1], pts[i]))
        L = seg[-1]
        if L < 2:
            return np.zeros((self.h, self.w), np.float32)
        n = max(8, int(L / 1.5))
        S = np.linspace(0, L, n)
        X = np.interp(S, seg, [p[0] for p in pts])
        Y = np.interp(S, seg, [p[1] for p in pts])
        dx, dy = np.gradient(X), np.gradient(Y)
        ln = np.hypot(dx, dy) + 1e-9
        nx, ny = -dy / ln, dx / ln
        s = S / L
        t0, t1 = taper
        prof = np.minimum(np.clip(s / max(t0, 1e-3), 0, 1) ** 0.6, np.clip((1 - s) / max(t1, 1e-3), 0, 1) ** 0.8)
        if pressure is not None:
            prof = prof * np.interp(s, np.linspace(0, 1, len(pressure)), pressure)
        half = width * k / 2 * prof
        im = Image.new("L", (self.w, self.h), 0)
        dr = ImageDraw.Draw(im)
        bw = max(1, int(round(width * k / bristles * 2.2)))
        nrng = np.random.default_rng(seed)
        for b in range(bristles):
            u = rng.uniform(-1, 1)
            u = math.copysign(abs(u) ** 0.8, u)
            ink = rng.uniform(0.75, 1.0)
            decay = ink_decay * rng.uniform(0.5, 1.5) * (0.6 + 0.8 * abs(u))
            # per-bristle breakup noise along the stroke
            m = max(4, n // 40)
            nz = np.interp(np.arange(n), np.linspace(0, n - 1, m), nrng.random(m))
            nz2 = np.interp(np.arange(n), np.linspace(0, n - 1, m * 6), nrng.random(m * 6))
            level = ink - decay * s - dry * (0.6 * nz + 0.4 * nz2)
            on = level > (0.25 * dry)
            if wobble:
                wv = np.interp(np.arange(n), np.linspace(0, n - 1, m), nrng.normal(0, wobble, m))
            else:
                wv = 0
            ox = X + nx * half * (u + wv)
            oy = Y + ny * half * (u + wv)
            val = int(255 * min(1, density * rng.uniform(0.8, 1.0)))
            start = None
            for i in range(n):
                if on[i] and start is None:
                    start = i
                if (not on[i] or i == n - 1) and start is not None:
                    if i - start > 1:
                        dr.line(list(zip(ox[start:i].tolist(), oy[start:i].tolist())), fill=val, width=bw)
                    start = None
        a = np.asarray(im, np.float32) / 255
        return gblur(a, 0.6 * max(1, k))

    def finish(self, grain=0.035, vignette=0.4, seed=0, warm=None):
        """Vignette, film grain and dithered 8-bit output -> PIL image."""
        img = self.img
        xs, ys = self.grid()
        d = np.sqrt(((xs - DW / 2) / (DW / 2)) ** 2 + ((ys - DH / 2) / (DH / 2)) ** 2)
        v = 1 - vignette * np.clip(d - 0.35, 0, None) ** 1.7
        img = img * v[..., None]
        rng = np.random.default_rng(seed)
        # luminance grain (fine + a little coarse clumping), stronger in mid-tones
        g = rng.normal(0, 1, (self.h, self.w)).astype(np.float32)
        coarse = gblur(rng.normal(0, 1, (self.h, self.w)).astype(np.float32), 1.2 * max(1, self.k))
        g = 0.75 * g + 0.9 * coarse
        lum = img.mean(axis=2)
        amt = grain * (0.35 + 1.3 * np.sqrt(np.clip(lum * (1.1 - lum), 0, 1)))
        img = img + (g * amt)[..., None]
        img = np.clip(img, 0, 1) * 255
        img = img + rng.random(img.shape, dtype=np.float32) - 0.5   # dither
        return Image.fromarray(np.clip(img + 0.5, 0, 255).astype(np.uint8))

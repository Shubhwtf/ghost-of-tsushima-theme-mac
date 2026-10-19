#!/usr/bin/env python3
"""Compose the README previews: a wallpaper, a SketchyBar-style bar drawn from
the bar's real colours and items, macOS window chrome with traffic lights and
JankyBorders outlines, and live terminal captures composited in.

usage: [GOT_VARIANT=kurosawa] previews.py CAPS_DIR OUT_DIR [FAN_DIR]

CAPS_DIR  PNG captures: fetch, code, dashboard, btop, plus *_tile versions for the tiled layout
FAN_DIR   wallhaven downloads (wallhaven-<id>.*) from scripts/wallpapers.py: the theme is
          composited onto real Ghost of Tsushima art (red variant)

Every preview uses real wallpapers or none at all. Without FAN_DIR, and always for
Kurosawa (kurosawa-*.jpg, graphite window buttons as macos/defaults.sh sets them),
the captures are framed as plain macOS windows on ink.
"""
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from palette import C, ROLE, VARIANT, rgb  # noqa: E402
from desktop import GL  # noqa: E402
from emblem import emblem_svg  # noqa: E402

W, H = 2880, 1800          # a 1440x900 pt display at 2x
PT = 2                     # pixels per point
CLOCK = "Sun 19 Oct  09:41"
KUROSAWA = VARIANT == "kurosawa"


def font_path(pattern):
    out = subprocess.run(["fc-match", "-f", "%{file}", pattern], capture_output=True, text=True).stdout
    return out.strip()


MONO_B = font_path("JetBrainsMono Nerd Font:style=Bold")
MONO = font_path("JetBrainsMono Nerd Font:style=Regular")
KANJI = font_path("Shippori Mincho:style=Bold")
SANS = font_path("Inter:style=Medium") or MONO


def F(path, pt):
    return ImageFont.truetype(path, int(pt * PT))


def rgba(name, a=255):
    return rgb(C.get(name, name)) + (a,)


def text_w(draw, s, font):
    return draw.textbbox((0, 0), s, font=font)[2]


# ------------------------------------------------------------------ SketchyBar
def bar(img, focused=1, app="kitty", spaces=5, clock=None):
    h = 34 * PT
    region = img.crop((0, 0, W, h)).filter(ImageFilter.GaussianBlur(30))
    img.paste(region, (0, 0))
    ov = Image.new("RGBA", (W, h), rgba("ink", 240))
    img.alpha_composite(ov, (0, 0))
    d = ImageDraw.Draw(img)
    d.rectangle((0, h - PT, W, h), fill=rgba("blood"))
    cy = h // 2
    x = 10 * PT
    # ensō
    png = subprocess.run(["rsvg-convert", "-w", str(30 * PT), "-h", str(30 * PT)],
                         input=emblem_svg(1024, small=True).encode(), capture_output=True, check=True).stdout
    import io
    enso = Image.open(io.BytesIO(png)).convert("RGBA")
    img.alpha_composite(enso, (x + 2 * PT, cy - enso.height // 2))
    x += 34 * PT + 8 * PT
    kf = F(KANJI, 14)
    for i, k in enumerate("一二三四五六七八九十"[:spaces], 1):
        gw = text_w(d, k, kf)
        iw = gw + 18 * PT
        if i == focused:
            d.rounded_rectangle((x, cy - 12 * PT, x + iw, cy + 12 * PT), radius=6 * PT, fill=rgba("lacquer"))
        d.text((x + 9 * PT, cy), k, font=kf, anchor="lm", fill=rgba("paper_hi" if i == focused else "smoke"))
        x += iw + 2 * PT
    x += 6 * PT
    d.text((x, cy), GL["diamond"], font=F(MONO_B, 9), anchor="lm", fill=rgba("lacquer"))
    x += 16 * PT
    d.text((x, cy), app, font=F(MONO_B, 13), anchor="lm", fill=rgba("paper_hi"))
    # right capsule: wifi, volume, battery, clock
    items = [(GL["wifi"], "sky", "Tsushima"), (GL["vol_hi"], "gold", "62%"),
             (GL["bat_75"], "paper", "84%"), (GL["clock"], "vermilion", clock or CLOCK)]
    ifont, lfont = F(MONO_B, 15), F(MONO_B, 13)
    widths = [6 * PT + text_w(d, ic, ifont) + 4 * PT + 4 * PT + text_w(d, lb, lfont) + 8 * PT for ic, _, lb in items]
    total = sum(widths) + 8 * PT
    rx = W - 10 * PT
    lx = rx - total
    d.rounded_rectangle((lx, cy - 13 * PT, rx, cy + 13 * PT), radius=8 * PT, fill=rgba("ash"), outline=rgba("stone"), width=PT)
    x = lx + 4 * PT
    for (ic, col, lb), w in zip(items, widths):
        x += 6 * PT
        d.text((x, cy), ic, font=ifont, anchor="lm", fill=rgba(col))
        x += text_w(d, ic, ifont) + 8 * PT
        d.text((x, cy), lb, font=lfont, anchor="lm", fill=rgba("paper"))
        x += text_w(d, lb, lfont) + 8 * PT


# ------------------------------------------------------------------ windows
def window(img, cap, box, title="", focused=True, crop=None, titlebar=True):
    """Draw a macOS window at box=(x, y, w, h) showing `cap`, scaled to the width."""
    x, y, w, h = box
    r = 12 * PT
    # shadow
    sh = Image.new("RGBA", (w + 200, h + 200), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((100, 120, 100 + w, 120 + h), radius=r, fill=(0, 0, 0, 170 if focused else 120))
    sh = sh.filter(ImageFilter.GaussianBlur(36))
    img.alpha_composite(sh, (x - 100, y - 100))
    win = Image.new("RGBA", (w, h), rgba("charcoal"))
    tb = 28 * PT if titlebar else 0
    src = cap.convert("RGBA")
    if crop:
        src = src.crop(crop)
    scale = w / src.width
    src = src.resize((w, max(1, int(src.height * scale))), Image.LANCZOS)
    win.paste(src.crop((0, 0, w, h - tb)), (0, tb))
    d = ImageDraw.Draw(win)
    if titlebar:
        d.rectangle((0, 0, w, tb), fill=rgba("ink"))
        d.line((0, tb - 1, w, tb - 1), fill=rgba("ash"), width=1)
        if KUROSAWA:   # graphite appearance: the window buttons lose their colour too
            lights = [C["smoke"]] * 3 if focused else [C["slate"]] * 3
        else:
            lights = ["#ff5f57", "#febc2e", "#28c840"] if focused else [C["slate"]] * 3
        for i, col in enumerate(lights):
            cx = 14 * PT + i * 20 * PT
            d.ellipse((cx - 6 * PT, tb // 2 - 6 * PT, cx + 6 * PT, tb // 2 + 6 * PT), fill=rgb(col) + (255,))
        if title:
            d.text((w // 2, tb // 2), title, font=F(MONO_B, 12), anchor="mm", fill=rgba("mist" if focused else "smoke"))
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, w - 1, h - 1), radius=r, fill=255)
    img.paste(win, (x, y), mask)
    # JankyBorders: the focus colour (lacquer, or silver in Kurosawa), ash otherwise (width 5pt, round)
    bw = int(2.5 * PT)
    ImageDraw.Draw(img).rounded_rectangle((x - bw, y - bw, x + w + bw - 1, y + h + bw - 1), radius=r + bw,
                                          outline=rgba(ROLE["focus"] if focused else "ash"), width=bw * 2)


def load_wall(path):
    im = Image.open(path).convert("RGB")
    if im.size != (W, H):
        # cover-crop to 16:10
        s = max(W / im.width, H / im.height)
        im = im.resize((int(im.width * s + 0.5), int(im.height * s + 0.5)), Image.LANCZOS)
        l, t = (im.width - W) // 2, (im.height - H) // 2
        im = im.crop((l, t, l + W, t + H))
    return im.convert("RGBA")


def save(img, path, w=2400):
    out = img.convert("L" if KUROSAWA else "RGB")   # one channel: no JPEG rounding can tint it
    if out.width > w:
        out = out.resize((w, int(out.height * w / out.width)), Image.LANCZOS)
    out.save(path, quality=86, optimize=True, progressive=True)
    print("wrote", path, os.path.getsize(path) // 1024, "KB")


# ------------------------------------------------------------------ layouts
GAP = 12 * PT
TOP = 34 * PT + GAP


def floating(wall, cap, box, title, app, crop=None):
    img = load_wall(wall)
    window(img, cap, box, title=title, crop=crop)
    bar(img, app=app)
    return img


def tiled(wall, main, side1, side2, app="nvim"):
    img = load_wall(wall)
    lw = int((W - 3 * GAP) * 0.6)
    rw = W - 3 * GAP - lw
    hh = H - TOP - GAP
    sh = (hh - GAP) // 2
    window(img, side1, (GAP + lw + GAP, TOP, rw, sh), title="fastfetch", focused=False)
    window(img, side2, (GAP + lw + GAP, TOP + sh + GAP, rw, sh), title="btop", focused=False)
    window(img, main, (GAP, TOP, lw, hh), title="nvim  src/wind.ts")
    bar(img, focused=2, app=app)
    return img


def framed(cap, title, path, ww=1600):
    """A capture as a plain macOS window on ink: no wallpaper behind it."""
    hh = int(ww * cap.height / cap.width) + 28 * PT
    canvas = Image.new("RGBA", (ww + 160, hh + 160), rgba("ink"))
    window(canvas, cap, (80, 70, ww, hh), title=title)
    save(canvas, path, w=ww)


def main():
    caps, out = sys.argv[1:3]
    fan = sys.argv[3] if len(sys.argv) > 3 else None
    os.makedirs(out, exist_ok=True)
    cap = {k: Image.open(os.path.join(caps, f"{k}.png")) for k in ("fetch", "code", "dashboard", "btop")}
    # tile-sized captures for the tiled layout (fall back to the big ones)
    for k in ("code", "fetch", "btop"):
        p = os.path.join(caps, f"{k}_tile.png")
        cap[f"{k}_tile"] = Image.open(p) if os.path.exists(p) else cap[k]

    if KUROSAWA:
        cap["dashboard"] = cap["dashboard"].crop((0, 0, cap["dashboard"].width, int(cap["dashboard"].height * 0.78)))
        for k, title in (("fetch", "kitty"), ("code", "nvim  src/wind.ts"), ("dashboard", "nvim"), ("btop", "btop")):
            framed(cap[k], title, os.path.join(out, f"kurosawa-{'term-fetch' if k == 'fetch' else k}.jpg"))
        return

    framed(cap["fetch"], "kitty", os.path.join(out, "term-fetch.jpg"))
    if not (fan and os.path.isdir(fan)):
        return
    files = {f.split("-")[1].split(".")[0]: os.path.join(fan, f) for f in os.listdir(fan) if f.startswith("wallhaven-")}
    fw = 1240
    fh = int(fw * 1400 / 1900) + 28 * PT
    dw = 1500
    dh = int(dw * 1600 / 2000) + 28 * PT
    if "e7vgml" in files:
        save(tiled(files["e7vgml"], cap["code_tile"], cap["fetch_tile"], cap["btop_tile"]), os.path.join(out, "fan-tiled.jpg"))
    if "rdpd9w" in files:
        save(floating(files["rdpd9w"], cap["fetch"], (W - fw - 170, 230, fw, fh), "jin@tsushima: ~/code/guiding-wind", "kitty"),
             os.path.join(out, "fan-fetch.jpg"))
    if "g72wqd" in files:
        save(floating(files["g72wqd"], cap["dashboard"], (W - dw - 140, (H - dh) // 2 + 40, dw, dh), "nvim", "nvim"),
             os.path.join(out, "fan-dashboard.jpg"))


if __name__ == "__main__":
    main()

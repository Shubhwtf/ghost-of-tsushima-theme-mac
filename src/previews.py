#!/usr/bin/env python3
"""Compose the README previews: a wallpaper, a SketchyBar-style bar drawn from
the bar's real colours and items, macOS window chrome with traffic lights and
JankyBorders outlines, and live terminal captures composited in.

usage: [GOT_VARIANT=kurosawa] previews.py CAPS_DIR WALL_DIR OUT_DIR [FAN_DIR]

CAPS_DIR  PNG captures: fetch, code, dashboard, telescope, btop
          (Kurosawa: fetch, code, dashboard, btop; plus *_tile versions for the tiled layout)
WALL_DIR  wallpapers rendered at 2880x1800 (GhostOfTsushima-<Scene>-2880x1800.jpg,
          or GhostOfTsushima-<Scene>-BW-2880x1800.jpg for Kurosawa)
FAN_DIR   optional wallhaven downloads (wallhaven-<id>.*) for the fan-art previews

With GOT_VARIANT=kurosawa the bar, window chrome and borders use the Kurosawa
palette (graphite window buttons, as macos/defaults.sh sets them) and the
previews are written as kurosawa-*.jpg.
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


def kurosawa(caps, walls, out):
    """The Kurosawa previews: the same layouts on the black-and-white scenes."""
    global CLOCK
    CLOCK = "Mon 19 Oct  09:41"
    cap = {k: Image.open(os.path.join(caps, f"{k}.png")) for k in ("fetch", "code", "dashboard", "btop")}
    for k in ("code", "fetch", "btop"):
        p = os.path.join(caps, f"{k}_tile.png")
        cap[f"{k}_tile"] = Image.open(p) if os.path.exists(p) else cap[k]
    wall = lambda k: os.path.join(walls, f"GhostOfTsushima-{k}-BW-2880x1800.jpg")
    name = lambda k: os.path.join(out, f"kurosawa-{k}.jpg")

    # hero: Higanbana in black and white, kitty with fastfetch floating on the left
    fw = 1240
    fh = int(fw * 1400 / 1900) + 28 * PT
    save(floating(wall("Higanbana"), cap["fetch"], (150, 250, fw, fh), "jin@tsushima: ~/code/guiding-wind", "kitty"),
         name("hero"))
    # tiled: Neovim, fastfetch and btop in the rain
    save(tiled(wall("Kurosawa"), cap["code_tile"], cap["fetch_tile"], cap["btop_tile"]), name("tiled"))
    # the ensō dashboard on the Guiding Wind
    dw = 1500
    dh = int(dw * 1600 / 2000) + 28 * PT
    save(floating(wall("GuidingWind"), cap["dashboard"], ((W - dw) // 2 - 260, (H - dh) // 2 + 40, dw, dh), "nvim", "nvim"),
         name("dashboard"))
    # code with neo-tree on the light Torii at Dawn
    cw = 1900
    ch = int(cw * 1400 / 2400) + 28 * PT
    save(floating(wall("ToriiAtDawn"), cap["code"], (110, H - ch - 110, cw, ch), "nvim  src/wind.ts", "nvim"), name("code"))
    # btop in the Standoff
    bw = 1700
    bh = int(bw * 1400 / 2200) + 28 * PT
    save(floating(wall("Standoff"), cap["btop"], ((W - bw) // 2, 330, bw, bh), "btop", "btop"), name("btop"))
    # the plain terminal shot, on ink
    c = cap["fetch"]
    ww = 1600
    hh = int(ww * c.height / c.width) + 28 * PT
    canvas = Image.new("RGBA", (ww + 160, hh + 160), rgba("ink"))
    window(canvas, c, (80, 70, ww, hh), title="kitty")
    save(canvas, name("term-fetch"), w=1600)


def main():
    caps, walls, out = sys.argv[1:4]
    if KUROSAWA:
        os.makedirs(out, exist_ok=True)
        kurosawa(caps, walls, out)
        return
    fan = sys.argv[4] if len(sys.argv) > 4 else None
    os.makedirs(out, exist_ok=True)
    cap = {k: Image.open(os.path.join(caps, f"{k}.png")) for k in ("fetch", "code", "dashboard", "telescope", "btop")}
    # tile-sized captures for the tiled layouts (fall back to the big ones)
    for k in ("code", "fetch", "btop"):
        p = os.path.join(caps, f"{k}_tile.png")
        cap[f"{k}_tile"] = Image.open(p) if os.path.exists(p) else cap[k]
    wall = lambda k: os.path.join(walls, f"GhostOfTsushima-{k}-2880x1800.jpg")

    # hero: Higanbana, kitty with fastfetch floating on the left
    fw = 1240
    fh = int(fw * 1400 / 1900) + 28 * PT
    save(floating(wall("Higanbana"), cap["fetch"], (150, 250, fw, fh), "jin@tsushima: ~/code/guiding-wind", "kitty"),
         os.path.join(out, "hero.jpg"))
    # tiled rice: Kurosawa with nvim, fastfetch and btop
    save(tiled(wall("Kurosawa"), cap["code_tile"], cap["fetch_tile"], cap["btop_tile"]), os.path.join(out, "tiled.jpg"))
    # nvim dashboard on the Guiding Wind
    dw = 1500
    dh = int(dw * 1600 / 2000) + 28 * PT
    save(floating(wall("GuidingWind"), cap["dashboard"], ((W - dw) // 2 - 260, (H - dh) // 2 + 40, dw, dh), "nvim", "nvim"),
         os.path.join(out, "dashboard.jpg"))
    # telescope on the light Torii at Dawn
    tw = 1900
    th = int(tw * 1400 / 2400) + 28 * PT
    save(floating(wall("ToriiAtDawn"), cap["telescope"], (110, H - th - 110, tw, th), "nvim  Telescope", "nvim"),
         os.path.join(out, "telescope.jpg"))
    # btop in the Standoff dusk
    bw = 1700
    bh = int(bw * 1400 / 2200) + 28 * PT
    save(floating(wall("Standoff"), cap["btop"], ((W - bw) // 2, 330, bw, bh), "btop", "btop"), os.path.join(out, "btop.jpg"))

    if fan and os.path.isdir(fan):
        files = {f.split("-")[1].split(".")[0]: os.path.join(fan, f) for f in os.listdir(fan) if f.startswith("wallhaven-")}
        if "e7vgml" in files:
            save(tiled(files["e7vgml"], cap["code_tile"], cap["fetch_tile"], cap["btop_tile"]), os.path.join(out, "fan-tiled.jpg"))
        if "rdpd9w" in files:
            save(floating(files["rdpd9w"], cap["fetch"], (W - fw - 170, 230, fw, fh), "jin@tsushima: ~/code/guiding-wind", "kitty"),
                 os.path.join(out, "fan-fetch.jpg"))
        if "g72wqd" in files:
            save(floating(files["g72wqd"], cap["dashboard"], (W - dw - 140, (H - dh) // 2 + 40, dw, dh), "nvim", "nvim"),
                 os.path.join(out, "fan-dashboard.jpg"))

    # grid of the original wallpapers
    keys = ["Higanbana", "ToriiAtDawn", "Standoff", "Kurosawa", "GuidingWind", "GuidingWindPaper"]
    tw2, th2, g = 1200, 750, 16
    grid = Image.new("RGB", (3 * tw2 + 4 * g, 2 * th2 + 3 * g), rgb(C["ink"]))
    for i, k in enumerate(keys):
        p = wall(k)
        if os.path.exists(p):
            im = Image.open(p).convert("RGB").resize((tw2, th2), Image.LANCZOS)
            grid.paste(im, (g + (i % 3) * (tw2 + g), g + (i // 3) * (th2 + g)))
    grid.save(os.path.join(out, "wallpapers.jpg"), quality=86, optimize=True, progressive=True)
    print("wrote wallpapers.jpg")

    # plain terminal shots for the gallery (just the window, on ink)
    for k, title in (("fetch", "kitty"),):
        c = cap[k]
        ww = 1600
        hh = int(ww * c.height / c.width) + 28 * PT
        canvas = Image.new("RGBA", (ww + 160, hh + 160), rgba("ink"))
        window(canvas, c, (80, 70, ww, hh), title=title)
        save(canvas, os.path.join(out, f"term-{k}.jpg"), w=1600)


if __name__ == "__main__":
    main()

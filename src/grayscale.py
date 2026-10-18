#!/usr/bin/env python3
"""Audit the Kurosawa variant for hue: every colour in it must be pure gray (R = G = B).

Scans the kurosawa variant in palette.json and every file whose name contains
"kurosawa" (any case), whatever its format:
  text    #rgb, #rrggbb, #rrggbbaa, 0xAARRGGBB / 0xRRGGBB, rgb()/rgba(),
          truecolour escapes (38;2 / 48;2 / 58;2) and 256-colour escapes (38;5;N)
  plists  .itermcolors / iTerm2 JSON components, Terminal.app NSColor blobs
  images  every pixel of PNG / JPG, and the SVG sources

usage: grayscale.py [ROOT]          exit status 1 if anything has a hue
       grayscale.py --nvim         also start the installed Neovim config headless in
                                   Kurosawa mode, load every plugin and check every
                                   highlight group (needs nvim and the plugins installed)
"""
import json
import os
import plistlib
import re
import subprocess
import sys
import tempfile

ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
ROOT = ARGS[0] if ARGS else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP = {".git", "build", "wallpapers", "__pycache__"}

HEX = re.compile(r"(?<![0-9A-Za-z&])#([0-9a-fA-F]{8}|[0-9a-fA-F]{6}|[0-9a-fA-F]{3})(?![0-9A-Za-z])")
HEX0X = re.compile(r"\b0x(?:[0-9a-fA-F]{2})?([0-9a-fA-F]{6})\b")
RGBFN = re.compile(r"rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)")
TRUE = re.compile(r"[345]8;2;(\d+);(\d+);(\d+)")
X256 = re.compile(r"[34]8;5;(\d+)")


def is_gray(r, g, b):
    return r == g == b


def xterm_gray(n):
    """Is xterm colour n gray? 0-15 are the themed ANSI colours, checked through the palette."""
    if n < 16 or n >= 232:
        return True
    n -= 16
    return n // 36 == (n // 6) % 6 == n % 6


def scan_text(txt):
    found = []
    for m in HEX.finditer(txt):
        h = m.group(1)
        if len(h) == 3:
            h = "".join(c * 2 for c in h)
        rgb = tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
        if not is_gray(*rgb):
            found.append(f"#{m.group(1)}")
    for m in HEX0X.finditer(txt):
        h = m.group(1)
        if not is_gray(*(int(h[i:i + 2], 16) for i in (0, 2, 4))):
            found.append(m.group(0))
    for rx in (RGBFN, TRUE):
        for m in rx.finditer(txt):
            if not is_gray(*map(int, m.groups())):
                found.append(m.group(0))
    for m in X256.finditer(txt):
        if not xterm_gray(int(m.group(1))):
            found.append(m.group(0))
    return found


def components(d):
    """Walk a plist / JSON tree for iTerm2-style {Red, Green, Blue Component} colours."""
    if isinstance(d, dict):
        if "Red Component" in d:
            yield tuple(round(float(d[f"{c} Component"]) * 255) for c in ("Red", "Green", "Blue"))
        for v in d.values():
            yield from components(v)
    elif isinstance(d, list):
        for v in d:
            yield from components(v)


def nscolors(path):
    for k, v in plistlib.load(open(path, "rb")).items():
        if isinstance(v, bytes) and k.endswith("Color"):
            a = plistlib.loads(v)
            obj = a["$objects"][a["$top"]["root"].data]
            yield k, tuple(round(float(x) * 255) for x in obj["NSRGB"].rstrip(b"\x00").split()[:3])


def pixels(path):
    from PIL import Image
    im = Image.open(path)
    if im.mode in ("L", "LA", "1"):
        return 0
    import numpy as np
    a = np.asarray(im.convert("RGBA")).astype(int)
    seen = a[..., 3] > 0
    spread = a[..., :3].max(axis=2) - a[..., :3].min(axis=2)
    return int((spread[seen] > 0).sum())


NVIM_AUDIT = r"""
vim.defer_fn(function()
  local lazy = package.loaded["lazy"]
  if lazy then
    pcall(lazy.load, { plugins = vim.tbl_map(function(p) return p.name end, lazy.plugins()) })
  end
  pcall(vim.cmd, "Neotree show")
  vim.cmd("doautocmd ColorScheme")
  local bad = { "colorscheme " .. (vim.g.colors_name or "none") }
  for name, _ in pairs(vim.api.nvim_get_hl(0, {})) do
    local h = vim.api.nvim_get_hl(0, { name = name, link = false })
    for _, k in ipairs({ "fg", "bg", "sp" }) do
      local v = h[k]
      if v and not (bit.rshift(v, 16) == bit.band(bit.rshift(v, 8), 255) and bit.band(v, 255) == bit.band(bit.rshift(v, 8), 255)) then
        table.insert(bad, string.format("%s %s #%06x", name, k, v))
      end
    end
  end
  for i = 0, 15 do
    local c = vim.g["terminal_color_" .. i]
    if c and not (c:sub(2, 3) == c:sub(4, 5) and c:sub(4, 5) == c:sub(6, 7)) then
      table.insert(bad, "terminal_color_" .. i .. " " .. c)
    end
  end
  local f = io.open(vim.env.GOT_AUDIT_OUT, "w")
  f:write(table.concat(bad, "\n"))
  f:close()
  vim.cmd("qa!")
end, 3000)
"""


def audit_nvim():
    """Every highlight group of the running config, resolved through links, must be gray."""
    with tempfile.TemporaryDirectory() as tmp:
        script, out = os.path.join(tmp, "audit.lua"), os.path.join(tmp, "out.txt")
        open(script, "w").write(NVIM_AUDIT)
        subprocess.run(["nvim", "--headless", "--cmd", 'let g:got_variant="kurosawa"', "-S", script],
                       env=dict(os.environ, GOT_AUDIT_OUT=out), capture_output=True, timeout=120)
        lines = open(out).read().splitlines() if os.path.exists(out) else ["nvim produced no report"]
    if lines[0] != "colorscheme ghost-of-tsushima-kurosawa":
        return [f"nvim: {lines[0]}"]
    return [f"nvim highlight {line}" for line in lines[1:]]


def files():
    for dp, dns, fns in os.walk(ROOT):
        dns[:] = [d for d in dns if d not in SKIP]
        for f in fns:
            if "kurosawa" in f.lower() or "kurosawa" in os.path.relpath(dp, ROOT).lower():
                yield os.path.join(dp, f)


def audit():
    errors = []
    data = json.load(open(os.path.join(ROOT, "palette.json")))["variants"]["kurosawa"]
    for k, v in list(data["colors"].items()) + [(f"ansi {i}", v) for i, v in enumerate(data["ansi"])]:
        v = data["colors"].get(v, v)
        for bad in scan_text(v):
            errors.append(f"palette.json kurosawa {k}: {bad}")
    n = 0
    for p in sorted(files()):
        rel = os.path.relpath(p, ROOT)
        n += 1
        ext = os.path.splitext(p)[1].lower()
        if ext in (".png", ".jpg", ".jpeg"):
            k = pixels(p)
            if k:
                errors.append(f"{rel}: {k} pixels have a hue")
            continue
        if ext == ".terminal":
            for key, rgb in nscolors(p):
                if not is_gray(*rgb):
                    errors.append(f"{rel}: {key} {rgb}")
            continue
        if ext == ".itermcolors":
            tree = plistlib.load(open(p, "rb"))
        elif ext == ".json" and "iterm" in rel:
            tree = json.load(open(p))
        else:
            tree = None
        if tree is not None:
            for rgb in components(tree):
                if not is_gray(*rgb):
                    errors.append(f"{rel}: component colour {rgb}")
        for bad in sorted(set(scan_text(open(p, encoding="utf-8", errors="ignore").read()))):
            errors.append(f"{rel}: {bad}")
    return n, errors


if __name__ == "__main__":
    n, errors = audit()
    if "--nvim" in sys.argv:
        errors += audit_nvim()
    for e in errors:
        print("HUE", e)
    print(f"grayscale: scanned the kurosawa palette and {n} files: " + ("ok" if not errors else f"{len(errors)} problem(s)"))
    sys.exit(1 if errors else 0)

#!/usr/bin/env python3
"""Validate the generated configs: every TOML / JSON / plist parses, the
Terminal.app colour blobs round-trip, and nothing in the Kurosawa variant has
a hue (every hex colour, every NSColor and every 38;2 escape must be gray).

usage: check.py [ROOT]
"""
import glob
import json
import os
import plistlib
import re
import sys
import tomllib

ROOT = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
errors = []


def rel(p):
    return os.path.relpath(p, ROOT)


def gray(r, g, b, tol=0):
    return max(r, g, b) - min(r, g, b) <= tol


def parse_all():
    n = 0
    for p in glob.glob(f"{ROOT}/**/*.toml", recursive=True):
        try:
            tomllib.load(open(p, "rb"))
            n += 1
        except Exception as e:  # noqa: BLE001
            errors.append(f"{rel(p)}: {e}")
    for p in glob.glob(f"{ROOT}/**/*.json", recursive=True) + glob.glob(f"{ROOT}/**/*.jsonc", recursive=True):
        txt = open(p).read()
        if p.endswith(".jsonc"):
            txt = "\n".join(line for line in txt.splitlines() if not line.lstrip().startswith("//"))
        try:
            json.loads(txt)
            n += 1
        except Exception as e:  # noqa: BLE001
            errors.append(f"{rel(p)}: {e}")
    for pat in ("*.terminal", "*.itermcolors", "*.tmTheme"):
        for p in glob.glob(f"{ROOT}/terminal/**/{pat}", recursive=True):
            try:
                d = plistlib.load(open(p, "rb"))
                n += 1
            except Exception as e:  # noqa: BLE001
                errors.append(f"{rel(p)}: {e}")
                continue
            if pat == "*.terminal":
                for k, v in d.items():
                    if k.endswith("Color"):
                        a = plistlib.loads(v)
                        obj = a["$objects"][a["$top"]["root"].data]
                        r, g, b = (float(x) for x in obj["NSRGB"].rstrip(b"\x00").split())
                        if "Kurosawa" in p and not gray(round(r * 255), round(g * 255), round(b * 255)):
                            errors.append(f"{rel(p)}: {k} is not gray")
    try:
        import yaml
        for p in glob.glob(f"{ROOT}/terminal/lazygit/*.yml"):
            yaml.safe_load(open(p))
            n += 1
    except ImportError:
        pass
    return n


HEX = re.compile(r"(?:#|0x[0-9a-fA-F]{2})([0-9a-fA-F]{6})\b")
ESC = re.compile(r"38;2;(\d+);(\d+);(\d+)|48;2;(\d+);(\d+);(\d+)")


def kurosawa_is_gray():
    files = [p for p in glob.glob(f"{ROOT}/**/*", recursive=True)
             if os.path.isfile(p) and "kurosawa" in os.path.basename(p).lower()
             and not p.endswith((".png", ".jpg", ".terminal"))]
    for p in files:
        txt = open(p, errors="ignore").read()
        for m in HEX.finditer(txt):
            h = m.group(1)
            if not gray(*(int(h[i:i + 2], 16) for i in (0, 2, 4))):
                errors.append(f"{rel(p)}: colour #{h} has a hue")
        for m in ESC.finditer(txt):
            v = [int(x) for x in m.groups() if x is not None]
            if not gray(*v):
                errors.append(f"{rel(p)}: escape {v} has a hue")
        if p.endswith(".itermcolors") or (p.endswith(".json") and "iterm" in p):
            pass
    for p in glob.glob(f"{ROOT}/terminal/iterm2/*Kurosawa*.itermcolors"):
        for k, v in plistlib.load(open(p, "rb")).items():
            if not gray(round(v["Red Component"] * 255), round(v["Green Component"] * 255), round(v["Blue Component"] * 255)):
                errors.append(f"{rel(p)}: {k} has a hue")
    return len(files)


if __name__ == "__main__":
    n = parse_all()
    k = kurosawa_is_gray()
    for e in errors:
        print("FAIL", e)
    print(f"parsed {n} files, scanned {k} Kurosawa files: " + ("ok" if not errors else f"{len(errors)} problem(s)"))
    sys.exit(1 if errors else 0)

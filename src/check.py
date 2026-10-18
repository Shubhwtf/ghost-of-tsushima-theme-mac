#!/usr/bin/env python3
"""Validate the generated configs: every TOML / JSON / plist parses, the
Terminal.app colour blobs round-trip, and nothing in the Kurosawa variant has
a hue (see grayscale.py).

usage: check.py [ROOT]
"""
import glob
import json
import os
import plistlib
import sys
import tomllib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import grayscale  # noqa: E402

ROOT = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
errors = []


def rel(p):
    return os.path.relpath(p, ROOT)


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
                        if len(obj["NSRGB"].rstrip(b"\x00").split()) < 3:
                            errors.append(f"{rel(p)}: {k} has no RGB components")
    try:
        import yaml
        for p in glob.glob(f"{ROOT}/**/*.yml", recursive=True) + glob.glob(f"{ROOT}/**/*.yaml", recursive=True):
            yaml.safe_load(open(p))
            n += 1
    except ImportError:
        pass
    return n


if __name__ == "__main__":
    n = parse_all()
    k, hues = grayscale.audit()
    errors += hues
    for e in errors:
        print("FAIL", e)
    print(f"parsed {n} files, scanned {k} Kurosawa files: " + ("ok" if not errors else f"{len(errors)} problem(s)"))
    sys.exit(1 if errors else 0)

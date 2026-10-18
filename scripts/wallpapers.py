#!/usr/bin/env python3
"""冥人 Ghost of Tsushima wallpapers: pick, render or download, and set them.

Three catalogs, numbered together:
  Originals   painted from code by src/wallpapers.py and rendered on your machine
              at your screen's resolution (needs numpy, pillow and rsvg-convert)
  Kurosawa    the same scenes graded in black and white, like the game's film mode
  wallhaven   top-rated 4K Ghost of Tsushima art, fetched live from wallhaven.cc
              (SFW, landscape, at least 3840x2160, sorted by favourites)

Run it with no options for an interactive menu, or:
  wallpapers.py --list                    show both catalogs and exit
  wallpapers.py --get 1,3,7               fetch by number (ranges like 7-12 and "all" work)
  wallpapers.py --originals all           render every original (or names / numbers: Higanbana,2)
  wallpapers.py --variant kurosawa --originals all    the black-and-white versions
  wallpapers.py --originals Higanbana-BW  one black-and-white scene
  wallpapers.py --wallhaven 10            download the 10 most-favourited wallhaven images
  wallpapers.py --res 5120x2880           render size for originals (default: your screen)
  wallpapers.py --dest DIR                where files go (default ~/Pictures/Wallpapers/GhostOfTsushima)
  wallpapers.py --set FILE                set FILE as the desktop picture (macOS)
  wallpapers.py --get 1 --set-first       fetch, then use the first result as the desktop

wallhaven images belong to their artists and to Sucker Punch Productions / Sony
Interactive Entertainment. They are downloaded for your personal use only; a
CREDITS.txt with every link, uploader and source is written next to them.
Standard library only (rendering originals calls src/wallpapers.py).
"""
import argparse
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
GENERATOR = os.path.join(ROOT, "src", "wallpapers.py")
DEST = os.path.expanduser("~/Pictures/Wallpapers/GhostOfTsushima")
CACHE = os.path.expanduser("~/.cache/ghost-of-tsushima/wallhaven.json")
API = "https://wallhaven.cc/api/v1"
UA = {"User-Agent": "ghost-of-tsushima-theme-mac/1.0 (+https://github.com/Shubhwtf/ghost-of-tsushima-theme-mac)"}
QUERIES = ["ghost of tsushima", "jin sakai", "tsushima"]
EXCLUDE = {
    "q6jr3q": "anime character named Tsushima, not the game",
    "13p3dv": "anime character named Tsushima, not the game",
    "d6qjpm": "Kali Linux logo pasted over the art",
    "m3kjkk": "Ghost of Yotei (the sequel), not Tsushima",
}
ORIGINALS = [
    ("Higanbana", "a lone samurai, a giant moon, a field of red spider lilies"),
    ("ToriiAtDawn", "sumi-e mountains, a red sun, a torii on the ridge (light)"),
    ("Standoff", "two samurai at dusk in a wind-swept golden field"),
    ("Kurosawa", "black and white rain; only the maple leaves and his sash are red"),
    ("GuidingWind", "minimal: white brushed wind on ink and a red 冥人 seal"),
    ("GuidingWindPaper", "the same on washi paper (light)"),
]
ORIGINALS = ORIGINALS + [(k + "-BW", "black and white, film grain") for k, _ in ORIGINALS]
COLOUR = len(ORIGINALS) // 2

RED, GOLD, DIM, PAPER, OFF = "\033[38;2;226;61;67m", "\033[38;2;201;164;92m", "\033[38;2;131;122;115m", "\033[38;2;236;230;220m", "\033[0m"
if not sys.stdout.isatty() or os.environ.get("NO_COLOR"):
    RED = GOLD = DIM = PAPER = OFF = ""


def say(msg):
    print(f"{RED}◆{OFF} {msg}", flush=True)


def note(msg):
    print(f"  {DIM}{msg}{OFF}", flush=True)


# ------------------------------------------------------------------ network
def http(url, tries=4):
    """GET with polite retries: backs off on 429 (rate limit) and network errors."""
    for attempt in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < tries - 1:
                wait = 10 * (attempt + 1)
                note(f"wallhaven rate limit, waiting {wait}s")
                time.sleep(wait)
                continue
            raise
        except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
            if attempt < tries - 1:
                time.sleep(3 * (attempt + 1))
                continue
            raise RuntimeError(f"network error: {e}") from e
    raise RuntimeError("giving up after retries")


def wallhaven_catalog(count, refresh=False):
    """Top `count` Ghost of Tsushima wallpapers, with uploader and source (cached for a day)."""
    if not refresh and os.path.exists(CACHE) and time.time() - os.path.getmtime(CACHE) < 86400:
        try:
            with open(CACHE) as f:
                cached = json.load(f)
            if len(cached) >= count:
                return cached[:count]
        except (OSError, ValueError):
            pass
    seen, items = set(EXCLUDE), []
    for q in QUERIES:
        for page in (1, 2):
            params = {"q": q, "categories": "110", "purity": "100", "atleast": "3840x2160",
                      "ratios": "16x9,16x10,21x9", "sorting": "favorites", "order": "desc", "page": page}
            try:
                data = json.loads(http(f"{API}/search?{urllib.parse.urlencode(params)}"))["data"]
            except Exception as e:  # noqa: BLE001 - keep going with what we have
                note(f"search '{q}' failed: {e}")
                break
            for it in data:
                if it["id"] not in seen:
                    seen.add(it["id"])
                    items.append(it)
            time.sleep(1.4)                      # wallhaven allows ~45 requests a minute
            if len(data) < 24:
                break
    items.sort(key=lambda it: it["favorites"], reverse=True)
    items = items[:count]
    print(f"  {DIM}looking up uploaders for {len(items)} wallpapers…{OFF}", flush=True)
    for it in items:
        try:
            info = json.loads(http(f"{API}/w/{it['id']}"))["data"]
            it["uploader"] = (info.get("uploader") or {}).get("username", "")
            it["source"] = info.get("source") or it.get("source", "")
        except Exception:  # noqa: BLE001
            it.setdefault("uploader", "")
        time.sleep(1.4)
    keep = ["id", "url", "path", "resolution", "favorites", "source", "uploader", "category"]
    items = [{k: it.get(k, "") for k in keep} for it in items]
    try:
        os.makedirs(os.path.dirname(CACHE), exist_ok=True)
        with open(CACHE, "w") as f:
            json.dump(items, f)
    except OSError:
        pass
    return items


# ------------------------------------------------------------------ originals
def screen_resolution():
    """Native pixel size of the largest display on macOS, else 3840x2160."""
    if platform.system() == "Darwin":
        try:
            out = subprocess.run(["system_profiler", "SPDisplaysDataType"], capture_output=True, text=True,
                                 timeout=30).stdout
            sizes = [(int(a), int(b)) for a, b in re.findall(r"Resolution:\s*(\d+)\s*x\s*(\d+)", out)]
            if sizes:
                return max(sizes, key=lambda s: s[0] * s[1])
        except (OSError, subprocess.SubprocessError):
            pass
    return 3840, 2160


def render_deps_ok():
    missing = []
    try:
        import numpy  # noqa: F401
    except ImportError:
        missing.append("numpy")
    try:
        import PIL  # noqa: F401
    except ImportError:
        missing.append("pillow")
    ok = True
    if missing:
        say(f"Rendering originals needs Python packages: {', '.join(missing)}")
        note(f"pip3 install {' '.join(missing)}")
        ok = False
    if not shutil.which("rsvg-convert"):
        say("Rendering originals needs rsvg-convert (librsvg)")
        note("brew install librsvg        (Linux: your distro's librsvg / librsvg2-bin package)")
        ok = False
    return ok


def render_original(key, res, dest):
    w, h = res
    bw = key.endswith("-BW")
    scene = key[:-3] if bw else key
    say(f"Painting {GOLD}{key}{OFF} at {w}x{h} (about a minute at 4K, a few at 5K and up)")
    r = subprocess.run([sys.executable, GENERATOR, "--scene", scene, "--res", f"{w}x{h}", "--out", dest]
                       + (["--bw"] if bw else []))
    if r.returncode != 0:
        say(f"rendering {key} failed")
        return None
    return os.path.join(dest, f"GhostOfTsushima-{key}-{w}x{h}.jpg")


# ------------------------------------------------------------------ wallhaven downloads
def download(it, dest):
    name = f"wallhaven-{it['id']}{os.path.splitext(it['path'])[1]}"
    out = os.path.join(dest, name)
    if os.path.exists(out):
        note(f"have {name}")
    else:
        say(f"Downloading {it['id']}  {it['resolution']}  ♥{it['favorites']}")
        try:
            data = http(it["path"])
        except Exception as e:  # noqa: BLE001
            say(f"could not download {it['id']}: {e}")
            return None
        with open(out + ".part", "wb") as f:
            f.write(data)
        os.replace(out + ".part", out)
        time.sleep(0.8)
    credit(it, name, dest)
    return out


def credit(it, name, dest):
    path = os.path.join(dest, "CREDITS.txt")
    existing = open(path).read() if os.path.exists(path) else (
        "Ghost of Tsushima wallpapers downloaded from wallhaven.cc for personal use.\n"
        "All rights belong to the artists and to Sucker Punch Productions / Sony Interactive Entertainment.\n\n")
    if it["id"] in existing:
        return
    existing += (f"{name}\n  wallhaven: {it['url']}\n  uploader:  {it.get('uploader') or 'unknown'}"
                 f" (https://wallhaven.cc/user/{it.get('uploader', '')})\n"
                 f"  source:    {it.get('source') or 'not given'}\n\n")
    with open(path, "w") as f:
        f.write(existing)


# ------------------------------------------------------------------ desktop
def set_desktop(path):
    path = os.path.abspath(os.path.expanduser(path))
    if not os.path.exists(path):
        say(f"no such file: {path}")
        return False
    if platform.system() != "Darwin":
        say("Setting the desktop picture is macOS only; your file is here:")
        note(path)
        return False
    script = f'tell application "System Events" to tell every desktop to set picture to POSIX file "{path}"'
    r = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    if r.returncode != 0:
        say("osascript could not set the wallpaper (allow your terminal to control System Events):")
        note(r.stderr.strip())
        return False
    say(f"Desktop set to {os.path.basename(path)}")
    return True


# ------------------------------------------------------------------ menu
def parse_selection(text, total):
    text = text.strip().lower()
    if text in ("all", "*"):
        return list(range(1, total + 1))
    out = []
    for part in re.split(r"[,\s]+", text):
        if not part:
            continue
        if "-" in part:
            a, b = part.split("-", 1)
            out.extend(range(int(a), int(b) + 1))
        else:
            out.append(int(part))
    return [n for n in dict.fromkeys(out) if 1 <= n <= total]


def show(catalog, res):
    n = len(ORIGINALS)
    print(f"\n{RED}冥人{OFF}  {PAPER}GHOST OF TSUSHIMA WALLPAPERS{OFF}\n")
    print(f"{GOLD}Originals{OFF} {DIM}(painted from code, rendered here at {res[0]}x{res[1]}){OFF}")
    for i, (key, desc) in enumerate(ORIGINALS, 1):
        if i == COLOUR + 1:
            print(f"\n{GOLD}Originals in Kurosawa mode{OFF} {DIM}(black and white){OFF}")
        print(f"  {RED}{i:>2}{OFF}  {key:<20} {DIM}{desc}{OFF}")
    print(f"\n{GOLD}4K art from wallhaven{OFF} {DIM}(belongs to its artists; personal use){OFF}")
    if not catalog:
        print(f"  {DIM}(unavailable: offline or wallhaven did not answer){OFF}")
    for i, it in enumerate(catalog, n + 1):
        src = it.get("source") or "-"
        if len(src) > 46:
            src = src[:45] + "…"
        print(f"  {RED}{i:>2}{OFF}  {it['id']}  {it['resolution']:>9}  ♥{it['favorites']:<4} "
              f"{(it.get('uploader') or '?'):<16} {DIM}{it['url']}  {src}{OFF}")
    print()


def fetch(numbers, catalog, res, dest):
    os.makedirs(dest, exist_ok=True)
    n = len(ORIGINALS)
    done = []
    origs = [ORIGINALS[i - 1][0] for i in numbers if i <= n]
    if origs and render_deps_ok():
        done += [p for p in (render_original(k, res, dest) for k in origs) if p]
    for i in numbers:
        if i > n:
            p = download(catalog[i - n - 1], dest)
            if p:
                done.append(p)
    if done:
        say(f"{len(done)} wallpaper(s) in {dest}")
    return done


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--list", action="store_true", help="show both catalogs and exit")
    ap.add_argument("--get", metavar="N,N", help="fetch by number, e.g. 1,3,7 or 7-12 or all")
    ap.add_argument("--originals", metavar="WHICH", help="render originals: all, or names/numbers")
    ap.add_argument("--wallhaven", type=int, metavar="N", help="download the top N wallhaven images")
    ap.add_argument("--count", type=int, default=12, help="how many wallhaven results to list (default 12)")
    ap.add_argument("--res", help="render size for originals, e.g. 5120x2880 (default: your screen)")
    ap.add_argument("--dest", default=DEST, help=f"download folder (default {DEST})")
    ap.add_argument("--set", metavar="FILE", help="set FILE as the macOS desktop picture")
    ap.add_argument("--set-first", action="store_true", help="after fetching, set the first file as the desktop")
    ap.add_argument("--refresh", action="store_true", help="ignore the cached wallhaven list")
    ap.add_argument("--variant", choices=["red", "kurosawa"], default="red",
                    help="with --originals: colour scenes (red) or black-and-white ones (kurosawa)")
    a = ap.parse_args()
    dest = os.path.expanduser(a.dest)

    if a.set and not (a.get or a.originals or a.wallhaven):
        sys.exit(0 if set_desktop(a.set) else 1)

    res = screen_resolution()
    if a.res:
        try:
            res = tuple(int(v) for v in a.res.lower().split("x"))
        except ValueError:
            sys.exit(f"--res must look like 3840x2160, not {a.res}")

    need_wh = a.list or a.get or a.wallhaven or not (a.originals or a.set)
    catalog = []
    if need_wh:
        try:
            catalog = wallhaven_catalog(max(a.count, a.wallhaven or 0), refresh=a.refresh)
        except Exception as e:  # noqa: BLE001
            note(f"wallhaven unavailable: {e}")

    total = len(ORIGINALS) + len(catalog)
    if a.list:
        show(catalog, res)
        return

    numbers = []
    if a.get:
        numbers += parse_selection(a.get, total)
    if a.originals:
        off = COLOUR if a.variant == "kurosawa" else 0
        if a.originals.strip().lower() == "all":
            numbers += list(range(off + 1, off + COLOUR + 1))
        else:
            keys = [k.lower() for k, _ in ORIGINALS]
            for part in re.split(r"[,\s]+", a.originals.strip()):
                if part.isdigit() and 1 <= int(part) <= len(ORIGINALS):
                    numbers.append(int(part))
                elif part.lower() in keys:
                    i = keys.index(part.lower())
                    numbers.append(i + 1 + (off if i < COLOUR else 0))
                elif part:
                    note(f"unknown original '{part}'")
    if a.wallhaven:
        numbers += list(range(len(ORIGINALS) + 1, len(ORIGINALS) + 1 + min(a.wallhaven, len(catalog))))

    interactive = not numbers
    if interactive:
        if not sys.stdin.isatty():
            show(catalog, res)
            return
        show(catalog, res)
        try:
            text = input(f"{RED}❯{OFF} pick numbers (e.g. 1,3,7 or 7-12 or all), Enter to quit: ")
        except (EOFError, KeyboardInterrupt):
            print()
            return
        numbers = parse_selection(text, total) if text.strip() else []
        if not numbers:
            return

    done = fetch(list(dict.fromkeys(numbers)), catalog, res, dest)
    if a.set:
        set_desktop(a.set)
    elif done and (a.set_first or (interactive and platform.system() == "Darwin")):
        if a.set_first:
            set_desktop(done[0])
        else:
            for i, p in enumerate(done, 1):
                print(f"  {RED}{i:>2}{OFF}  {os.path.basename(p)}")
            try:
                pick = input(f"{RED}❯{OFF} set one as your desktop? number, or Enter to skip: ").strip()
            except (EOFError, KeyboardInterrupt):
                pick = ""
            if pick.isdigit() and 1 <= int(pick) <= len(done):
                set_desktop(done[int(pick) - 1])


if __name__ == "__main__":
    main()

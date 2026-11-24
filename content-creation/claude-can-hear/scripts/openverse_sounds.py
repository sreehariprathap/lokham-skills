#!/usr/bin/env python3
"""Search and download real, openly licensed sounds and music from Openverse (api.openverse.org).

Only licences you can use in a video without asking: CC0, public domain, CC BY, CC BY-SA. Never NC (non-commercial)
or ND (no derivatives). Every saved file gets a line in CREDITS.md next to it; CC BY / BY-SA need that line in your
caption or description.

Usage:
  python3 openverse_sounds.py search "footsteps wood"          # top 12: id, length, licence, title, creator, source
  python3 openverse_sounds.py search "lofi piano" --music
  python3 openverse_sounds.py save <id> [--dir sounds]          # downloads + appends to <dir>/CREDITS.md
No API key needed (anonymous limit: about 20 searches a minute, 200 a day). Only the Python standard library.
"""
import argparse, json, os, re, sys, urllib.parse, urllib.request

API = "https://api.openverse.org/v1/audio/"
LICENSES = "cc0,pdm,by,by-sa"
UA = {"User-Agent": "lokham-skills-openverse/1.0"}
MAX_BYTES = 200 * 1024 * 1024


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
        return json.load(r)


def lic(code):
    return {"pdm": "Public domain", "cc0": "CC0"}.get(code, f"CC {code.upper()}")


def search(q, music):
    params = {"q": q[:100], "license": LICENSES, "page_size": 12}
    if music:
        params["category"] = "music"   # sound effects have no category in Openverse: they are found by keyword
    d = get(API + "?" + urllib.parse.urlencode(params))
    print(f"{d.get('result_count', 0):,} matches for {q!r}")
    for r in d.get("results", []):
        if not r.get("url"):
            continue
        secs = round((r.get("duration") or 0) / 1000)
        print(f"{r['id']}  {secs:>4}s  {lic(r['license']):<14} {(r.get('title') or 'untitled')[:48]}  by {(r.get('creator') or '?')[:28]}  ({r.get('source')})")


def save(oid, folder):
    if not re.fullmatch(r"[0-9a-f-]{36}", oid):
        sys.exit("that doesn't look like an Openverse id (copy it from the search results)")
    r = get(API + oid + "/")
    if r.get("license") not in LICENSES.split(","):
        sys.exit(f"licence {r.get('license')} is not one we use (no NC / ND)")
    url = r.get("url") or ""
    if urllib.parse.urlparse(url).scheme != "https":
        sys.exit("this sound has no https download")
    ext = (r.get("filetype") or os.path.splitext(urllib.parse.urlparse(url).path)[1].lstrip(".") or "mp3").lower()
    title = re.sub(r"\.(wav|mp3|ogg|flac|aiff?|m4a)$", "", (r.get("title") or "sound").strip(), flags=re.I)
    name = re.sub(r"[^A-Za-z0-9 _-]+", "", title).strip()[:60] or "sound"
    os.makedirs(folder, exist_ok=True)
    dst = os.path.join(folder, f"{name}.{ext}")
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as resp:
        body = resp.read(MAX_BYTES + 1)
    if len(body) > MAX_BYTES:
        sys.exit("file is over 200 MB, skipped")
    open(dst, "wb").write(body)
    credit = r.get("attribution") or f"{r.get('title')} by {r.get('creator')}"
    with open(os.path.join(folder, "CREDITS.md"), "a") as f:
        f.write(f"- **{os.path.basename(dst)}**: {credit} ({lic(r['license'])}). Source: {r.get('foreign_landing_url') or url}\n")
    print(f"saved {dst} ({lic(r['license'])})" + ("  -> credit needed: copy its CREDITS.md line into your caption" if r["license"] in ("by", "by-sa") else ""))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search"); s.add_argument("query"); s.add_argument("--music", action="store_true")
    v = sub.add_parser("save"); v.add_argument("id"); v.add_argument("--dir", default="sounds")
    a = ap.parse_args()
    try:
        search(a.query, a.music) if a.cmd == "search" else save(a.id, a.dir)
    except urllib.error.HTTPError as e:
        sys.exit(f"Openverse said {e.code}" + (" (rate limit: wait a minute)" if e.code == 429 else ""))


if __name__ == "__main__":
    main()

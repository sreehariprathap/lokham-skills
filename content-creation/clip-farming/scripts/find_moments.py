#!/usr/bin/env python3
"""Shortlist the moments in long footage most likely to make good clips.

Scores every second by loudness spikes (screams, crashes, a streamer yelling) and scene changes (fast action, cuts),
then returns the top windows, spaced apart, as timestamps. It is a shortlist for a human (or Claude) to look at,
not a final judge. Needs only Python 3 and ffmpeg/ffprobe on PATH.

Usage: python3 find_moments.py footage.mp4 [--top 12] [--len 18] [--gap 25] [--out moments.json]
"""
import argparse, json, re, subprocess, sys
from statistics import median


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def duration(path):
    r = run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path])
    return float(r.stdout.strip())


def loudness_per_second(path, dur):
    """Momentary loudness (LUFS, 400 ms window) from ffmpeg's ebur128 meter, averaged per second."""
    r = run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-vn", "-af", "ebur128", "-f", "null", "-"])
    sec = {}
    for m in re.finditer(r"t:\s*([\d.]+)\s+TARGET.*?M:\s*(-?[\d.]+|-inf)", r.stderr):
        t, v = float(m.group(1)), m.group(2)
        if v != "-inf": sec.setdefault(int(t), []).append(float(v))
    n = int(dur) + 1
    return [sum(sec[i]) / len(sec[i]) if i in sec else -70.0 for i in range(n)]


def scene_changes(path):
    """Times of big picture changes, on a small, low-fps copy (fast)."""
    r = run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-an", "-vf", "fps=5,scale=320:-2,select='gt(scene,0.30)',showinfo", "-f", "null", "-"])
    return [float(x) for x in re.findall(r"pts_time:([\d.]+)", r.stderr)]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video")
    ap.add_argument("--top", type=int, default=12, help="how many moments to return")
    ap.add_argument("--len", type=float, default=18, help="clip window length in seconds")
    ap.add_argument("--gap", type=float, default=25, help="minimum seconds between moments")
    ap.add_argument("--out", help="write the moments as JSON here")
    a = ap.parse_args()

    dur = duration(a.video)
    loud = loudness_per_second(a.video, dur)
    cuts = scene_changes(a.video)
    n = len(loud)
    # loudness spike = how much louder than the surrounding minute (so quiet and loud streams both work)
    spike = []
    for i in range(n):
        ctx = loud[max(0, i - 30):i + 30]
        spike.append(max(0.0, loud[i] - median(ctx)))
    action = [0.0] * n
    for t in cuts:
        for i in range(max(0, int(t) - 2), min(n, int(t) + 3)):
            action[i] += 1.0
    score = [spike[i] + 0.8 * min(action[i], 6) for i in range(n)]

    picks, taken = [], []
    for i in sorted(range(n), key=lambda k: -score[k]):
        if score[i] <= 0 or any(abs(i - j) < a.gap for j in taken):
            continue
        taken.append(i)
        start = max(0.0, i - a.len * 0.6)          # most of the window before the peak: the setup, then the payoff
        end = min(dur, start + a.len)
        picks.append({"peak": i, "start": round(start, 1), "end": round(end, 1), "score": round(score[i], 2),
                      "loudness_spike_db": round(spike[i], 1), "scene_changes_near": int(action[i])})
        if len(picks) >= a.top:
            break
    picks.sort(key=lambda p: p["start"])
    hms = lambda s: f"{int(s // 3600)}:{int(s % 3600 // 60):02d}:{s % 60:04.1f}"
    print(f"{a.video}: {hms(dur)}, {len(cuts)} scene changes, {len(picks)} candidate moments")
    for p in picks:
        print(f"  {hms(p['start'])} - {hms(p['end'])}  score {p['score']:5.1f}  (+{p['loudness_spike_db']} dB, {p['scene_changes_near']} cuts)")
    if a.out:
        json.dump({"video": a.video, "duration": round(dur, 1), "moments": picks}, open(a.out, "w"), indent=1)
        print("wrote", a.out)


if __name__ == "__main__":
    try:
        main()
    except FileNotFoundError:
        sys.exit("ffmpeg/ffprobe not found: install ffmpeg first (macOS: brew install ffmpeg, Windows: winget install ffmpeg)")

#!/usr/bin/env python3
"""Let Claude watch a video: frames + words on one timeline.

Claude can open a link, but it can't play a video. This downloads the video (or takes a local file), saves frames
at an even pace, gets the spoken words (the platform's captions, else Whisper if it's installed) and writes an index
that lines every frame up with what's being said at that moment. Claude then reads the frames as images and the
transcript as text.

Needs Python 3 and ffmpeg; yt-dlp for links; Whisper optional.
Usage:
  python3 watch.py "https://www.youtube.com/watch?v=..." --out watch_out
  python3 watch.py my_clip.mp4 --out watch_out --max-frames 60
  python3 watch.py URL --every 2          (one frame every 2 s instead of auto pacing)
Writes: <out>/video.mp4, <out>/frames/f000.jpg..., <out>/transcript.txt, <out>/index.json
"""
import argparse, glob, html, json, os, re, shutil, subprocess, sys


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def need(tool, hint):
    if not shutil.which(tool):
        sys.exit(f"{tool} not found: {hint}")


def download(url, out):
    need("yt-dlp", "install it first (pip install yt-dlp, or brew install yt-dlp)")
    r = run(["yt-dlp", "--no-playlist", "--no-progress", "-f", "b[height<=720][ext=mp4]/bv*[height<=720]+ba/b",
             "--merge-output-format", "mp4", "--write-subs", "--write-auto-subs", "--sub-langs", "en.*,en", "--sub-format", "vtt",
             "--max-filesize", "800M", "-o", os.path.join(out, "video.%(ext)s"), url])
    if r.returncode:
        sys.exit("download failed (private video, login wall or region lock?):\n" + r.stderr[-800:])
    vids = [p for p in glob.glob(os.path.join(out, "video.*")) if not p.endswith(".vtt")]
    return vids[0], sorted(glob.glob(os.path.join(out, "video*.vtt")))


def vtt_lines(path):
    """WebVTT -> [(seconds, text)], with the rolling duplicates of auto-captions removed."""
    out, last, t = [], "", 0.0
    for line in open(path, encoding="utf-8", errors="ignore"):
        line = line.strip()
        m = re.match(r"(\d+):(\d+):([\d.]+) -->", line) or re.match(r"(\d+):([\d.]+) -->", line)
        if m:
            g = [float(x) for x in m.groups()]
            t = g[0] * 3600 + g[1] * 60 + g[2] if len(g) == 3 else g[0] * 60 + g[1]
            continue
        if not line or line.startswith(("WEBVTT", "Kind:", "Language:", "NOTE")) or line.isdigit():
            continue
        text = html.unescape(re.sub(r"<[^>]+>", "", line)).strip()
        if text and text != last:
            out.append((t, text)); last = text
    return out


def whisper_lines(video, out):
    exe = shutil.which("whisper")
    if not exe:
        return None
    run([exe, video, "--model", "base", "--output_format", "json", "--output_dir", out])
    js = os.path.join(out, os.path.splitext(os.path.basename(video))[0] + ".json")
    if not os.path.exists(js):
        return None
    return [(s["start"], s["text"].strip()) for s in json.load(open(js))["segments"]]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("source", help="a video link or a local file")
    ap.add_argument("--out", default="watch_out")
    ap.add_argument("--max-frames", type=int, default=40, help="cap on frames (auto pacing spreads them over the video)")
    ap.add_argument("--every", type=float, default=0, help="seconds between frames (0 = auto)")
    ap.add_argument("--no-whisper", action="store_true", help="captions only, never run Whisper")
    a = ap.parse_args()
    need("ffmpeg", "install it first (macOS: brew install ffmpeg, Windows: winget install ffmpeg)")
    os.makedirs(os.path.join(a.out, "frames"), exist_ok=True)

    if re.match(r"https?://", a.source):
        video, subs = download(a.source, a.out)
    else:
        video, subs = a.source, []
        if not os.path.exists(video):
            sys.exit(f"no such file: {video}")
    dur = float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", video]).stdout.strip() or 0)
    every = a.every or max(1.0, round(dur / max(1, a.max_frames), 2))
    for old in glob.glob(os.path.join(a.out, "frames", "f*.jpg")):
        os.remove(old)
    run(["ffmpeg", "-v", "error", "-y", "-i", video, "-vf", f"fps=1/{every},scale=768:-2", "-q:v", "4",
         os.path.join(a.out, "frames", "f%03d.jpg")])
    frames = sorted(glob.glob(os.path.join(a.out, "frames", "f*.jpg")))[: max(a.max_frames, 1) if not a.every else None]

    words, src = [], "none"
    if subs:
        words, src = vtt_lines(subs[0]), "platform captions"
    if not words and not a.no_whisper:
        w = whisper_lines(video, a.out)
        if w:
            words, src = w, "whisper"
    mmss = lambda s: f"{int(s // 60):02d}:{s % 60:04.1f}"
    with open(os.path.join(a.out, "transcript.txt"), "w") as f:
        f.write(f"# transcript source: {src}\n" + "".join(f"[{mmss(t)}] {x}\n" for t, x in words))
    index = []
    for i, p in enumerate(frames):
        t = round(i * every + every / 2, 2)   # fps filter samples the middle of each interval
        said = " ".join(x for s, x in words if t - every / 2 <= s < t + every / 2)
        index.append({"frame": i, "t": t, "file": os.path.relpath(p, a.out), "said": said})
    json.dump({"source": a.source, "duration": round(dur, 1), "every": every, "transcript": src, "frames": index},
              open(os.path.join(a.out, "index.json"), "w"), indent=1)
    print(f"{len(frames)} frames (every {every} s over {dur:.0f} s), transcript: {src} ({len(words)} lines) -> {a.out}/")
    if src == "none":
        print("no words: the video has no captions and Whisper isn't installed (pip install openai-whisper) or it has no speech")


if __name__ == "__main__":
    main()

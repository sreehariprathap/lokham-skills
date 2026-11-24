#!/usr/bin/env python3
"""Cut a vertical 1080x1920 short from long footage, with the hook line on screen from the first frame.

- Black letterbox bars baked into the footage are detected and removed first.
- Zoom-to-fill crop by default (--x 0..1 moves the crop window left/right to keep the action in frame),
  or --fit for the whole picture on a blurred background.
- Loudness evened out for phones (about -14 LUFS), H.264 + AAC, ready for Shorts / Reels / TikTok.
- The hook is burned in when this ffmpeg can draw text; otherwise a .srt with the hook is written next to the clip
  so it can be added in the app's editor or CapCut.
Needs only Python 3 and ffmpeg.

Usage:
  python3 cut_short.py footage.mp4 --start 754.2 --end 772 --hook "HE DID WHAT?!" --out clip01.mp4 [--x 0.4] [--fit]
  python3 cut_short.py stream.mp4 --start 1:02:34 --end 1:02:52 --facecam 1500:780:400:280 --hook "NO WAY" --out clip02.mp4
  python3 cut_short.py footage.mp4 --batch clips.csv --outdir clips/      (CSV columns: start,end,hook[,x])
Times can be seconds (754.2) or h:mm:ss / mm:ss.
"""
import argparse, csv, os, shutil, subprocess, sys


def secs(v):
    v = str(v).strip()
    if ":" not in v:
        return float(v)
    out = 0.0
    for part in v.split(":"):
        out = out * 60 + float(part)
    return out


def has_filter(name):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-filters"], capture_output=True, text=True)
    return any(line.split()[1:2] == [name] for line in r.stdout.splitlines() if len(line.split()) > 1)


FONTS = ["/System/Library/Fonts/Supplemental/Arial Black.ttf", "/System/Library/Fonts/Supplemental/Impact.ttf",
         "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "C:/Windows/Fonts/ariblk.ttf", "C:/Windows/Fonts/impact.ttf"]


def esc(t):   # drawtext text escaping
    return t.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\u2019").replace("%", "\\%")


def bars(src, start, dur):
    """Black letterbox / pillarbox bars baked into the footage -> 'crop=w:h:x:y,' to remove them first ('' if none)."""
    r = subprocess.run(["ffmpeg", "-hide_banner", "-ss", f"{start + dur / 2:.3f}", "-t", "2", "-i", src, "-vf", "cropdetect=limit=24:round=2",
                        "-f", "null", "-"], capture_output=True, text=True).stderr
    found = [l.split("crop=")[-1].strip() for l in r.splitlines() if "crop=" in l]
    if not found:
        return ""
    w, h, x, y = (int(v) for v in found[-1].split(":"))
    p = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "csv=p=0", src],
                       capture_output=True, text=True).stdout.strip().split(",")
    W, H = int(p[0]), int(p[1])
    return f"crop={w}:{h}:{x}:{y}," if (w < W - 8 or h < H - 8) and w > W * .5 and h > H * .5 else ""


def srt_time(s):
    return f"{int(s // 3600):02d}:{int(s % 3600 // 60):02d}:{int(s % 60):02d},{int(s * 1000) % 1000:03d}"


def cut(src, start, end, hook, out, x=0.5, fit=False, facecam=None):
    dur = end - start
    if not 3 <= dur <= 180:
        sys.exit(f"clip length {dur:.1f} s: keep it between 3 and 180 s (10-30 s works best)")
    pre = bars(src, start, dur)
    X = min(max(x, 0), 1)
    if facecam:   # stream layout: webcam box (source pixels) on top 1080x640, gameplay crop below 1080x1280
        cx, cy, cw, ch = (int(float(v)) for v in facecam.split(":"))
        graph = (f"[0:v]split[s1][s2];[s1]crop={cw}:{ch}:{cx}:{cy},scale=1080:640:force_original_aspect_ratio=increase,crop=1080:640[cam];"
                 f"[s2]{pre}scale=-2:1280,crop=1080:1280:(iw-1080)*{X}:0[game];[cam][game]vstack")
        pre, vf = "", None
    elif fit:   # whole picture over a blurred, zoomed copy of itself
        vf = ("split[a][b];[a]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=20:2[bg];"
              "[b]scale=1080:-2[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2")
    else:     # zoom to fill: full height, crop a 9:16 window at x (0 = left edge, 1 = right edge)
        vf = f"scale=-2:1920,crop=1080:1920:(iw-1080)*{X}:0"
    if vf:
        graph = f"[0:v]{pre}{vf}"
    srt = None
    if hook:
        font = next((f for f in FONTS if os.path.exists(f)), None)
        if has_filter("drawtext") and font:
            graph += (f",drawtext=fontfile='{font}':text='{esc(hook.upper())}':fontsize=78:fontcolor=white:borderw=6:bordercolor=black"
                   f":x=(w-text_w)/2:y=h*0.22:enable='lt(t,{min(dur, 3.5)})'")
        else:
            srt = os.path.splitext(out)[0] + ".srt"
            open(srt, "w").write(f"1\n{srt_time(0)} --> {srt_time(min(dur, 3.5))}\n{hook.upper()}\n")
    cmd = ["ffmpeg", "-v", "error", "-y", "-ss", f"{start:.3f}", "-t", f"{dur:.3f}", "-i", src,
           "-filter_complex", f"{graph}[v]", "-map", "[v]", "-map", "0:a?",
           "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", out]
    subprocess.run(cmd, check=True)
    print(f"{out}: {dur:.1f} s from {start:.1f} s" + (f", hook burned in" if hook and not srt else "") + (f", hook in {srt} (add it in the app)" if srt else ""))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video")
    ap.add_argument("--start"); ap.add_argument("--end"); ap.add_argument("--hook", default="")
    ap.add_argument("--out", default="clip.mp4")
    ap.add_argument("--x", type=float, default=0.5, help="crop window position 0..1 (zoom-to-fill mode)")
    ap.add_argument("--fit", action="store_true", help="whole picture on a blurred background instead of a crop")
    ap.add_argument("--facecam", help="webcam box X:Y:W:H in source pixels: face on top, gameplay below (stream layout)")
    ap.add_argument("--batch", help="CSV with start,end,hook[,x] per clip")
    ap.add_argument("--outdir", default="clips")
    a = ap.parse_args()
    if not shutil.which("ffmpeg"):
        sys.exit("ffmpeg not found: install it first (macOS: brew install ffmpeg, Windows: winget install ffmpeg)")
    if a.batch:
        os.makedirs(a.outdir, exist_ok=True)
        rows = [r for r in csv.DictReader(open(a.batch)) if r.get("start")]
        for i, r in enumerate(rows, 1):
            cut(a.video, secs(r["start"]), secs(r["end"]), r.get("hook", ""), os.path.join(a.outdir, f"clip{i:02d}.mp4"),
                float(r.get("x") or a.x), a.fit, a.facecam)
    else:
        if a.start is None or a.end is None:
            sys.exit("give --start and --end (or --batch clips.csv)")
        cut(a.video, secs(a.start), secs(a.end), a.hook, a.out, a.x, a.fit, a.facecam)


if __name__ == "__main__":
    main()

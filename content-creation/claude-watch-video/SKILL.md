---
name: claude-watch-video
description: Let Claude actually watch a video. Claude can open a link but can't play a video, so this downloads it (YouTube, Instagram, TikTok, X and most sites via yt-dlp) or takes a local file, saves frames, gets the spoken words from captions or Whisper, and lines them up on one timeline, so Claude can describe, summarise, break down or learn from what is on screen AND said. Use it whenever someone shares a video link or file and wants it watched, reviewed, summarised, broken down (hook, pacing, edits), turned into notes or a script, or asks "what happens in this video", even if they don't say "watch".
---

# Watch a video

Claude opens links fine; it just can't play video. The fix is to turn the video into things Claude can read:
pictures (frames) and words (a transcript), lined up by time. Then you look at the frames and read the words together.

## 1. Turn the video into frames + words

```bash
python3 scripts/watch.py "<link or file>" --out watch_out
```
- `--max-frames 40` (default) spreads frames evenly; short reels get one every second or so, long videos fewer.
  Use `--every 1` for fast-cut reels when you need every beat, `--max-frames 80` for a long tutorial.
- Words come from the platform's captions when they exist, else Whisper if installed (`pip install openai-whisper`),
  else none. `--no-whisper` keeps it fast and offline.
- Output: `watch_out/frames/f000.jpg...`, `watch_out/transcript.txt`, `watch_out/index.json`
  (each frame's time and what was said around it).

Needs ffmpeg and, for links, yt-dlp (`pip install yt-dlp` or `brew install yt-dlp`). If a link fails (private,
login wall, region lock), say so and ask for the file instead. Don't ask for or use anyone's login.

## 2. Watch it

Read `index.json`, then look at the frames as images, in order, with what was said at each time next to them.
Don't skip frames to save time on short videos: the details (on-screen text, a cut, a face) are the point.
Ground every statement in a frame time or a transcript line, so the person can check it.

## 3. Answer what they asked

Common asks and what to give:
- **"What happens?" / summary**: the story in time order with timestamps, what's shown and what's said.
- **Breakdown of a reel or ad**: the hook (first 1-3 s: exactly what is on screen and said, and why it stops the
  scroll), format (talking head, screen recording, animation...), beat-by-beat structure with times, pacing (how often
  it cuts, where it speeds up), on-screen text style, the ending and its ask.
- **Notes / a script / "make one like this"**: notes from both channels; for a new script, copy the structure and
  pacing, never the creator's words or footage.
- **Several links**: run each into its own folder (`--out v1`, `--out v2`...), analyse each, then compare what the
  strong ones share.

## Be clear about the limits

- You see frames, not motion: fast action between frames can be missed. Say so if it matters, and re-run with
  `--every 0.5` around the moment.
- Music and sound effects are not in the transcript; only speech is. Don't describe sounds you can't know.
- Downloaded videos are for watching and analysis. Re-uploading someone else's video needs their permission.

# clip-farming

A free Claude skill that turns long gaming footage (GTA 6 streams, VODs, your own gameplay) into vertical short clips,
and explains honestly how paid clipping campaigns work. Shared by **Just.intelligence.Things** for everyone who
commented **GTA** on the reel.

## What it does
- Asks where your footage comes from and keeps you on the safe side of copyright
- Finds the best moments in hours of footage (loudness spikes + scene changes) — `scripts/find_moments.py`
- Cuts 1080x1920 shorts with the hook on screen from the first frame, removes letterbox bars, and has a stream
  layout (webcam on top, gameplay below) — `scripts/cut_short.py`
- Writes hooks, captions, titles and a 30-day posting plan, with a tracking sheet
- Explains clipping campaigns: how they pay, typical rates, caps, red flags

## Install

**Claude Code**
```bash
git clone https://github.com/sreehariprathap/lokham-skills
cp -r lokham-skills/content-creation/clip-farming ~/.claude/skills/
```
(or unzip `clip-farming.zip` into `~/.claude/skills/`). Then just ask Claude: *"help me clip farm my GTA 6 stream"*.

**Claude app (claude.ai / desktop)**: Settings → Capabilities → Skills → upload `clip-farming.zip`.
The cutting scripts need a computer with ffmpeg; on the app Claude can still plan, write hooks and explain campaigns.

No terminal? Claude can walk you through the same steps by hand in CapCut.

## Requirements (for cutting clips)
- Python 3 (no extra packages)
- ffmpeg — macOS `brew install ffmpeg`, Windows `winget install ffmpeg`, Linux `sudo apt install ffmpeg`

## Try it
```bash
python3 scripts/find_moments.py stream.mp4 --top 12 --out moments.json
python3 scripts/cut_short.py stream.mp4 --start 12:34 --end 12:52 --hook "HE DID WHAT?!" --out clip01.mp4
python3 scripts/cut_short.py stream.mp4 --start 1:02:34 --end 1:02:52 --facecam 1500:780:400:280 --out clip02.mp4
```

## Please read
- Only clip footage you're allowed to use: campaign footage (follow its brief) or your own gameplay.
  Re-uploading other people's videos gets accounts struck. See `references/rights.md`.
- Money numbers are estimates from third-party guides (Nov 2026): around $1 per 1,000 views, roughly $0.20–$6,
  with caps and budgets. Nothing here is a promise of income.
- Not affiliated with Rockstar Games, Take-Two, Whop, YouTube, Instagram, TikTok or Anthropic.
  GTA and Grand Theft Auto are trademarks of Take-Two Interactive.

MIT licence.

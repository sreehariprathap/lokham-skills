---
name: claude-can-hear
description: Give Claude "ears" for video and sound work with three free tools: Openverse (search and download millions of real, openly licensed sounds and music, script included), Earshot (turns audio into numbers and labels Claude can read, so it can check what a sound really is, its loudness and timing) and Real SFX (places real recorded sound effects on the exact frames of a video). Use it to set these up, or whenever someone needs a real sound for a video, wants Claude to check or compare sounds, mix or measure audio, or asks "can Claude hear?", even if they don't name the tools.
---

# Claude can hear

Claude can't listen to audio. These three tools turn sound into things it can search, read and measure:

| # | Tool | What it does | Source |
|---|---|---|---|
| 1 | **Openverse** | find real recordings and music you're allowed to use | `scripts/openverse_sounds.py` (in this skill) |
| 2 | **Earshot** | describe, match, rank and measure sounds (LUFS, peaks, timing) | github.com/Leonxlnx/earshot (MIT) |
| 3 | **Real SFX** | place real sound effects on the exact frames of a video | github.com/Clipwing/skills (`skills/real-sfx`) |

Openverse is built in. Earshot and Real SFX belong to their authors: install them from their own repos (below),
don't copy them around.

## Setup (do it with the person, one tool at a time)

Needs Python 3.10+ and ffmpeg (`brew install ffmpeg` / `winget install ffmpeg` / `sudo apt install ffmpeg`).

**1. Openverse**: nothing to install. Try it:
```bash
python3 scripts/openverse_sounds.py search "footsteps wood"
python3 scripts/openverse_sounds.py save <id> --dir sounds
```

**2. Earshot** (CPU only; the first run downloads about 1.1 GB of open models):
```bash
git clone https://github.com/Leonxlnx/earshot && cd earshot
python -m venv .venv
.venv/bin/python -m pip install torch --index-url https://download.pytorch.org/whl/cpu   # Windows: .venv\Scripts\python
.venv/bin/python -m pip install -e ".[mcp]"
.venv/bin/python -m earshot doctor --load
```
Then copy its `skills/earshot` folder into `~/.claude/skills/` and follow its README for the MCP server.
Check the repo's README for changes before running: it is the source of truth.

**3. Real SFX**:
```bash
git clone https://github.com/Clipwing/skills.git clipwing-skills
cp -R clipwing-skills/skills/real-sfx ~/.claude/skills/
```
Read its README for prerequisites. The repo had no licence file when this was written: tell the person to check its
terms before using it commercially.

Restart Claude Code after installing.

## Using them together

1. **Find** with Openverse: short concrete words work best ("glass break", "crowd cheer", not "a sad glass sound").
   `--music` for music. Only CC0, public domain, CC BY, CC BY-SA are offered; CC BY / BY-SA need the credit line from
   `CREDITS.md` in the caption.
2. **Check** with Earshot before using a sound: does it really sound like what you need (`match FILE "description"`),
   which of several takes fits best (`rank`), where the good part is (`find`), and how loud it is (`measure`).
   Trust its measurements most and say which numbers you used.
3. **Place** with Real SFX on the frames where things happen (a footstep on the foot contact, a whoosh on the cut),
   then check the result with Earshot (`timeline`, `critique`).

## Honest limits

You still can't hear: every claim about a sound comes from a measurement or the person's ears. Say which.
Ask the person to listen once before publishing.

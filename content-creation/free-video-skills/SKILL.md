---
name: free-video-skills
description: Set up and use the free skill kit that lets Claude make whole videos with code, no paid video tools: Remotion (animated videos written in React), HyperFrames (HTML pages and motion graphics rendered to MP4) and the sound pair Openverse + Earshot (real licensed sounds, checked by numbers). Use it when someone wants Claude to make videos, reels, explainers, cartoons or motion graphics for free, asks "how did Claude make this video", wants to install Remotion or HyperFrames skills, or wants to pick which tool fits a video idea.
---

# Free video skills

Four free tools that pair up: two make the picture, two handle the sound.

| Tool | Best for | Install (official source) |
|---|---|---|
| **Remotion** | animation where every frame is code: cartoons, data, anything that moves precisely | `npx skills add remotion-dev/skills` (remotion.dev/docs/ai/skills) |
| **HyperFrames** | titles, captions, explainers, UI-style reels: HTML + GSAP rendered to MP4 | `npx skills add heygen-com/hyperframes` (github.com/heygen-com/hyperframes) |
| **Openverse** | real recorded sounds and music you're allowed to use | the `claude-can-hear` skill from Lokham Skills |
| **Earshot** | checking sounds and the mix by numbers (what it is, how loud, when) | the `claude-can-hear` skill from Lokham Skills |

Each belongs to its authors; install from the official source so the person gets updates. Check each project's
licence page before commercial use (Remotion has its own licence terms for companies; read remotion.dev/license).

## Setup

Needs Node.js 18+ (nodejs.org), ffmpeg, and for the sound pair Python 3.10+.
1. Remotion: `npx skills add remotion-dev/skills`, then `npx create-video@latest` for a first project.
2. HyperFrames: `npx skills add heygen-com/hyperframes`; it renders with a headless Chrome, so the first render downloads one.
3. Sound: install the `claude-can-hear` skill and follow its setup.
Restart Claude Code, then ask for a tiny test video in each before a real project.

## Picking the tool for an idea

- A story with characters that move (a crab, a ball, a robot): **Remotion**. Draw with SVG or canvas, animate from
  the frame number, so renders are identical every time.
- Words, cards, charts, a phone or chat mock-up, captions on footage: **HyperFrames**.
- Both in one reel: make the cartoon in Remotion, render it to MP4, and use it as a clip inside the HyperFrames reel
  (titles, captions, outro on top).
- Sound for any of them: find real sounds with Openverse, check and place them with Earshot, mix the voice and
  sounds to about -14 LUFS for phones.

## A first project that shows all four (about 15 minutes)

"A crab finishes a sandcastle and holds up a NO sign to a giant wave":
1. Remotion: a 12 s 1080x1920 cartoon (sky, sea, wave, crab, castle), the wave rising and backing off.
2. Openverse: beach waves, a seagull, a small boing. Save them with their credits.
3. Earshot: pick the best seagull take, find its loudest call, measure the mix.
4. HyperFrames: a hook title, captions, the cartoon in the middle, an end card.

## Honest limits

Claude can't watch the render or hear the mix: check still frames and Earshot numbers, then ask the person to
watch and listen once. Code-made art takes iteration; plan two or three rounds.

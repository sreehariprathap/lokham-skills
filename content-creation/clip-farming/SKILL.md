---
name: clip-farming
description: Turn long footage (GTA 6 and other games, sports moments, viral events, your own gameplay) into vertical short clips that get views, and earn from them through ad revenue on your own page or clipping campaigns that have a budget. Finds the best moments, cuts 9:16 shorts with a 1-second hook and captions, writes titles and a posting plan, and explains honestly how the money works (no promised numbers) and what you are allowed to clip. Use this whenever someone wants to clip, clip farm, make shorts/reels/TikToks from a stream or gameplay, asks how clippers get paid, wants to make money from GTA 6 (or any game, sport or viral moment) without owning it, or says "help me make clips", even if they never say "clip farming".
---

# Clip farming

Clip farming = taking long footage (a 4-hour stream, a gameplay session, a match, a viral event) and turning its best
10-30 seconds into vertical shorts, many times a day. The money comes two ways:

1. **Ad revenue on your own page.** Post the clips on your own accounts; once a page qualifies for the platform's
   monetisation programme, its views earn a share of ad revenue. This is the main route.
2. **Clipping campaigns that have a budget.** Some creators and brands post footage plus a budget and pay approved
   clips of *their* footage. Find them on clipping marketplaces, follow the brief, submit the clips.

Your job is to get the person from "I want to do this" to a folder of finished clips and a plan, honestly.
Read `references/campaigns.md` before talking about money, and `references/rights.md` before cutting anything.

## 1. Find out where they are (one short message)

If their message already answers these, skip the questions and go straight to the walkthrough. Otherwise ask only
what you need, in one go:
- **Footage:** a file on their computer, a link, or nothing yet? Whose footage is it (their own gameplay, a campaign's
  footage, someone else's stream)?
- **Goal:** a campaign (which one, what does its brief say?) or their own channel?
- **Platforms:** YouTube Shorts, Instagram Reels, TikTok.

If they have no footage yet, skip to step 5 (plan + campaigns) and tell them what to record or where to find
campaign footage. If the footage belongs to someone else (a friend's stream, a creator's VOD), the fix is usually
easy: ask the owner for a written OK (a DM they can screenshot), agree where clips get posted and how the owner is
credited. Until then, don't cut it. If the owner can't be asked, explain why
(see `references/rights.md`) and offer the allowed routes instead. This protects their account: platforms strike
re-uploads, and campaigns reject clips that break their brief.

If they sound under 18 (school, pocket money, "my parents"), mention once, kindly, that payout platforms and
partner programmes usually need an adult account holder or a parent's consent.

No coding setup? Everything below also works by hand in CapCut or the platform's own editor (crop to 9:16, text hook,
auto-captions). Offer that route; the scripts are a speed-up, not a requirement.

## 2. Find the best moments

Long footage is mostly nothing. Good clips are moments where something *changes*: a crash, a chase starting,
a glitch, a fail, a clutch escape, a big reaction, a funny NPC line, a "wait, what?".

Use the helper to shortlist candidates fast (needs ffmpeg and Python 3, no other installs):

```bash
python3 scripts/find_moments.py "footage.mp4" --top 12 --out moments.json
```

It scores every few seconds by loudness spikes (screams, crashes, the streamer yelling) and scene changes, and
writes the top windows with timestamps. It is a shortlist, not a judge: look at the candidates (extract a frame or
two with ffmpeg and view them if you can) and pick the ones with a clear setup and payoff. If there is a transcript
or chat log, use it too: chat spikes and lines like "NO WAY" mark moments.

For each pick, write down: start, end (10-30 s; shorter usually wins), the one-line "what happens", and the hook.

## 3. Write the hook and captions

The first second decides everything. Read `references/hooks.md` for formulas. Rules of thumb:
- Start the clip *just before* the payoff, not at the calm part. Cut the run-up.
- One hook line on screen at 0 s, max ~6 words, big: "HE DID WHAT?!", "GTA 6 PHYSICS ARE INSANE", "1 IN A MILLION".
- Captions for any speech, 2-4 words at a time, because most people watch muted.
- Never promise what the clip doesn't show. Misleading hooks get clips rejected by campaigns and hurt retention.

## 4. Cut the vertical clips

```bash
python3 scripts/cut_short.py "footage.mp4" --start 754.2 --end 772.0 --hook "HE DID WHAT?!" --out clip01.mp4
```

What it does: cuts the window, makes it 1080x1920 (zoom-to-fill crop by default; `--x 0.3` moves the crop window
left/right to keep the action in frame; `--fit` gives a blurred-background version instead), evens out the
loudness for phones, and burns the hook as a caption when this ffmpeg can draw text. If it can't, it writes
`clip01.srt` next to the clip so they can add captions in CapCut / the platform editor. Check the action stays
inside the crop: extract a frame from the result and look at it.

Stream footage with a webcam in the corner: `--facecam X:Y:W:H` (the webcam box in source pixels) stacks the face on
top and the gameplay below, the usual layout for stream clips. Find the box by extracting one frame and looking at it.

Batch: put one line per clip in a CSV (`start,end,hook`) and run `--batch clips.csv`.

Speech captions: the script burns only the hook. For spoken lines, use the auto-captions in CapCut / TikTok / Instagram
/ YouTube, or Whisper if it's installed (`whisper clip01.mp4 --output_format srt`), then check the words.

## 5. Titles, posting plan, tracking

For each clip give: a title/caption (hook + context + 3-5 relevant hashtags), and which platform first.
Then a simple plan the person can actually keep. Read `references/posting-plan.md`. Default: 1-3 clips a day,
same time slots, post to all three platforms, and log every clip (link, date, views at 24 h / 7 days) so they
learn which hooks work. For campaigns: submit each clip in the campaign dashboard the way its brief says.

## Be honest about money

Two routes (details in `references/campaigns.md`):
1. **Ad revenue on their own page**, once it qualifies for the platform's monetisation programme. Each platform sets
   its own rules and thresholds; point them to the platform's own monetisation page rather than quoting them.
2. **Clipping campaigns with a budget**: join on a clipping marketplace, follow the brief, submit clips. Campaigns pay
   only for clips of *their own* footage; a friend's VOD doesn't count unless that friend runs the campaign.

**Never give a number** (per view, per 1,000 views, per month). Ad revenue changes all the time and depends on the
platform, the audience, the country and the season; campaign terms differ per campaign. Say it honestly: nobody can
promise a number, but it's possible. Most clips get modest views; a few break out. Never promise an income. Never ask for or handle their passwords,
payment details or platform logins: they sign up and submit themselves.

The dates, rates and policies in the reference files were checked in November 2026. If you can search the web,
re-check them before quoting; if you can't, say when they were last checked.

## Output checklist

- [ ] footage source and permission confirmed (own gameplay / campaign footage)
- [ ] shortlist of moments with timestamps and why each works
- [ ] cut clips (1080x1920) with hook at 0 s, or .srt captions alongside
- [ ] a title + caption per clip
- [ ] posting plan + tracking sheet
- [ ] honest money note: ad revenue + campaigns, no promised numbers

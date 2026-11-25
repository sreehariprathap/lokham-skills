# Lokham Skills

Free Claude skills from [Lokham](https://github.com/sreehariprathap/lokham-hub), sorted by category.

## Before you start

Every skill is a folder of instructions an AI agent follows, so you need one of: **Claude** (app or Claude Code), **Codex**, or another agentic platform that can read skills or Markdown files. Some skills also run scripts (for example Python 3 or ffmpeg); each skill's README says what it needs.

## Use a skill

1. Download the skill's zip from its Lokham Skills page and unzip it.
2. Move the folder into `~/.claude/skills/` (every project) or `.claude/skills/` inside one project.
3. Restart Claude Code and ask for the skill by name. (Claude app: upload the zip in Settings, Capabilities, Skills. Codex or another agent: point it at the folder or paste `SKILL.md`.)

## Layout

```
<category>/<skill-name>/SKILL.md      e.g. content-creation/reel-hooks/SKILL.md
```

A category is just a top-level folder; add `finance/` and it shows up as a new category.

## Add a skill

1. Create `<category>/<skill-name>/` (lowercase letters, numbers, dashes; unique across the whole repo, because it is the link).
2. Put a `SKILL.md` in it that starts with:

   ```
   ---
   name: skill-name
   description: One line on what it does and when to use it.
   ---
   ```

3. Push to `main`. A few minutes later it is live at `/skills/<skill-name>` with a download button.

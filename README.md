# Lokham Skills

Free Claude skills from [Lokham](https://github.com/sreehariprathap/lokham-hub), sorted by category.

## Use a skill

1. Download the skill's zip from its Lokham Skills page and unzip it.
2. Move the folder into `~/.claude/skills/` (every project) or `.claude/skills/` inside one project.
3. Restart Claude Code and ask for the skill by name.

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

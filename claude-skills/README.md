# Claude Skills Adapter

This folder lets you reuse the vendored Codex skills with Claude by generating a single session prompt that combines:

1. `CLAUDE.md` project constraints
2. One or more skill `SKILL.md` files
3. Optional `references/*.md` files

## Quick start

Generate a prompt for project leadership + reviewer gate:

```powershell
py claude-skills/build_prompt.py --skills project-leader-agent,reviewer-agent --include-references --output .claude/prompts/project-lead-review.md
```

Then paste `.claude/prompts/project-lead-review.md` into Claude at session start.

## Available skill names

See `claude-skills/skill-map.json`.

## Common combos

- Planning + execution:
  - `project-leader-agent,developer-agent,reviewer-agent`
- Architecture + DB:
  - `architect-agent,db-agent`
- Compliance research:
  - `vat-research-agent,reviewer-agent`

## Notes

- This is an adapter workflow; Claude does not auto-load Codex skill folders natively.
- Keep prompts focused: include only skills needed for the task.

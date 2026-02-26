# Skills In Project

All Codex skills are vendored into this repository under `skills/`, including:

- `skills/architect-agent`
- `skills/db-agent`
- `skills/db-expert-agent`
- `skills/devops-agent`
- `skills/designer-agent`
- `skills/developer-agent`
- `skills/project-leader-agent`
- `skills/project-manager-agent`
- `skills/tester-agent`
- `skills/critic-agent`
- `skills/review-agent`
- `skills/reviewer-agent`
- `skills/vat-research-agent`
- `skills/.system/skill-creator`
- `skills/.system/skill-installer`

Each skill folder contains its `SKILL.md` plus any bundled `references/`, `scripts/`, and `assets/` content.

## Claude usage

Use the adapter in `claude-skills/` to build Claude-ready session prompts from vendored skills:

```powershell
py claude-skills/build_prompt.py --skills project-leader-agent,reviewer-agent --include-references --output .claude/prompts/project-lead-review.md
```

See `claude-skills/README.md` for examples.

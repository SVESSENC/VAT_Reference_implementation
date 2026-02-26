# CLAUDE.md — VAT Reference Implementation

> This file is loaded automatically into every Claude Code session.
> It contains the hard constraints for this project. They apply regardless of what you are asked to do.

---

## What this project is

A VAT calculation application built by a team of 4 humans, each working with AI agents.
Every agent works on exactly one module. There is no shared agent memory. These rules exist to prevent agents from conflicting with each other.

---

## Your module

You must be told your module at the start of every session. If you have not been told, ask before writing any code:

> "Which module am I working on — engine, api, frontend, or shared?"

Once told, your scope is fixed for the entire session:

| Module | Allowed paths | Notes |
|--------|--------------|-------|
| engine | `/src/engine/**`, `/tests/engine/**` | VAT calculation logic only |
| api | `/src/api/**`, `/tests/api/**` | REST layer only — delegate all VAT logic to engine |
| frontend | `/src/frontend/**` | UI only |
| shared | `/src/shared/**` | **Team sign-off required. Do not modify without being explicitly told the team has approved.** |

Do not create or modify any file outside your assigned paths. If the task requires it, stop and say so rather than doing it.

---

## Important — some docs are still TBD

`docs/architecture.md` and `docs/vat-rules.md` are loaded automatically but are not yet filled in. If either is still marked TBD when you read it:

- **Do not begin implementation tasks.** Tell the human these docs must be completed before you can proceed.
- Do not infer or assume what the tech stack or VAT rules might be.
- Do not treat TBD as a gap you should fill with a reasonable default.

---

## Canonical sources of truth — follow them exactly, never deviate

| Document | What it governs |
|----------|----------------|
| `docs/data-contracts.md` | All field names and data shapes. Use these names exactly — case-sensitive. Do not invent, rename, or restructure fields. |
| `docs/vat-rules.md` | All VAT logic. Implement only what is documented here. Do not add logic for rules not listed. |
| `docs/architecture.md` | System design and tech stack. Do not suggest alternatives unless asked. |
| `docs/project-status.md` | What already exists. Read this before writing anything — do not re-implement existing work. |

---

## If you are uncertain — stop and ask

Do not fill gaps with reasonable-sounding guesses. If you are unsure about:

- A field name → ask, or flag that it is not in `docs/data-contracts.md`
- A VAT rule → ask, or flag that it is not in `docs/vat-rules.md`
- The tech stack → ask, or refer to `docs/architecture.md`
- Whether something already exists → ask the human to check `docs/project-status.md`

**Saying "I'm not sure, please clarify" is always correct. Inventing an answer is never acceptable.**

---

## What you must never do

- Create or modify files in `/src/shared` without being explicitly told the team has approved it
- Rename, restructure, or add fields to shapes defined in `docs/data-contracts.md`
- Implement VAT rules not documented in `docs/vat-rules.md`
- Add external dependencies (packages, libraries) without being explicitly asked to
- Modify `docs/architecture.md`, `docs/vat-rules.md`, or `docs/data-contracts.md` — these are human-maintained
- Update `docs/project-status.md` or `CHANGELOG.md` — the human writes these
- Push to `main` or suggest force-pushing / rewriting git history
- Generate code outside your assigned module paths
- Add "nice to have" features, refactors, or improvements that were not requested

---

## Auto-loaded context

The following files are imported automatically into every Claude Code session — no manual pasting required:

@docs/project-status.md
@CHANGELOG.md
@docs/architecture.md
@docs/data-contracts.md
@docs/vat-rules.md
@docs/agent-rules.md

---

## Session auto-start

If the human starts a session without giving you a specific task, run this loop automatically:

### Step 1 - Run start-flow automation
Run:
```powershell
py .\skills\project-leader-agent\scripts\jira_start_flow.py --output .\.claude\prompts\jira-start-brief.md
```

This command picks the next Open ticket, infers module + owner agent, proposes a feature branch, transitions the issue to **In Progress** (`181`), adds a start comment, and writes a runnable brief.

### Step 2 - Announce selected ticket
Tell the human:
> "Picking up [TC-XX]: [title]. Module: [module]. Owner agent: [agent]. Branch: `feature/TC-XX-<slug>`."

If module is `shared` or `unknown`, stop and ask before coding.

### Step 4 — Implement
Work within the module boundaries defined above. Apply all guardrails from `docs/agent-rules.md` section 11. If `docs/architecture.md` or `docs/vat-rules.md` are still TBD, stop and tell the human before writing any code.

### Step 5 — Reviewer gate
Run the self-review defined in `docs/agent-rules.md` section 10. Produce an explicit verdict: `PASS` or `FAIL`.

### Step 6 — Close or escalate

**If PASS:**
Use the Atlassian MCP to:
1. Transition the ticket to **Done** (transition ID: `151`)
2. Add a completion comment:
```
Completed on branch: feature/TC-XX-<slug>
Deliverable: [file path or feature summary]
Review: reviewer-agent PASS [YYYY-MM-DD]
```
Then report to the human: what was built, what files changed, anything they need to review before committing.

**If FAIL:**
- Transition to **In Review** (transition ID: `211`)
- Add a comment listing each finding
- Do NOT move to Done
- Tell the human what failed and what needs to be fixed before closure

---

## Full rules

See [docs/agent-rules.md](docs/agent-rules.md) for the complete team workflow.
See [docs/prompt-templates.md](docs/prompt-templates.md) for copy-paste prompts.


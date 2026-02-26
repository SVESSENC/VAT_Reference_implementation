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

---

## Full rules

See [docs/agent-rules.md](docs/agent-rules.md) for the complete team workflow.
See [docs/prompt-templates.md](docs/prompt-templates.md) for copy-paste prompts.

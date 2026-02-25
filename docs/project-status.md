# Project Status

> **Paste this file into every agent session — before architecture.md, before data-contracts.md.**
> It tells the agent what already exists so it doesn't re-implement or contradict existing work.
>
> **Owner:** Every team member is responsible for keeping this accurate.
> Update this file in the same commit as your code changes. An outdated status doc is worse than none.
>
> Last updated: 2026-02-25
> Updated by: (name / role)
> Current branch state: `dev` is ahead of `main` by 1 commit (agent-rules.md added)

---

## What Is Up and Running

_Nothing is implemented yet. This section will grow as modules are built._

| Component | Status | Location | Notes |
|-----------|--------|----------|-------|
| — | — | — | — |

---

## What Is In Progress

| Component | Status | Branch | Owner | Blocked by |
|-----------|--------|--------|-------|-----------|
| — | — | — | — | — |

---

## What Has Not Been Started

- [ ] Tech stack decision (see `docs/architecture.md`)
- [ ] Engine: VAT calculation core
- [ ] Engine: Jurisdiction routing
- [ ] Engine: Exemption / zero-rate logic
- [ ] Engine: Reverse charge logic
- [ ] API: Endpoint definitions (see `docs/data-contracts.md`)
- [ ] API: Request validation
- [ ] API: Error handling
- [ ] Frontend: UI scaffolding
- [ ] Frontend: Calculation form
- [ ] Shared: TypeScript types for VatInput / VatOutput
- [ ] Shared: Country/jurisdiction constants
- [ ] Tests: Engine unit tests
- [ ] Tests: API integration tests

---

## Known Issues / Blockers

| # | Description | Module | Raised by | Status |
|---|-------------|--------|----------|--------|
| — | — | — | — | — |

---

## Decisions Made

> Log significant decisions here so agents don't re-open closed questions.

| Date | Decision | Rationale | Decided by |
|------|----------|-----------|-----------|
| 2026-02-25 | Project scaffolded with engine/api/frontend/shared module split | Separates concerns and allows parallel development | Team |
| 2026-02-25 | All PRs target `dev`, only `dev` → `main` for releases | Prevents unstable code reaching production | Team |

---

## How to Update This File

After every PR that changes behaviour, update:

1. Move completed items from "Not Started" to "Up and Running"
2. Add any new in-progress work to "In Progress"
3. Log any blockers or issues discovered
4. Log any decisions made during the session
5. Update "Last updated" and "Updated by" at the top
6. Commit this file in the **same commit** as your code changes — never separately

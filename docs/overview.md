# VAT Reference Implementation — Project Overview

> Last updated: 2026-02-26
> This document is a human-readable summary of the project. It is not a canonical source of truth.
> For authoritative rules, always refer to the linked canonical docs.

---

## What This Project Is

A **VAT calculation application** built by a team of 4 people, each working with an AI agent (Claude or similar). The application takes a transaction as input, applies the correct VAT rules for the relevant jurisdiction, and returns a fully calculated output suitable for invoicing.

The project is currently in its **pre-implementation phase** — the operating framework, governance docs, and skill library are all in place, but no application code has been written yet.

---

## Team Structure

| Role | Module | Allowed Paths |
|------|--------|--------------|
| Engine Dev | `engine` | `/src/engine/**`, `/tests/engine/**` |
| API Dev | `api` | `/src/api/**`, `/tests/api/**` |
| Frontend Dev | `frontend` | `/src/frontend/**` |
| Shared (team) | `shared` | `/src/shared/**` — **team sign-off required before any change** |

Each person works exclusively within their module. Agents have no shared memory, so the docs are the shared brain that keeps all four streams consistent.

---

## System Architecture

```
[ Frontend ] → [ API ] → [ Engine ]
                              ↓
                        [ Shared Types ]
```

Full tech stack is TBD — see [`docs/architecture.md`](architecture.md) for the decision template. This must be filled in before any coding begins.

---

## Data Contracts

> Canonical source: [`docs/data-contracts.md`](data-contracts.md) — field names are case-sensitive and must be used exactly as documented.

### VatInput

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `transactionAmount` | `number` | Yes | Net transaction amount before VAT |
| `customerType` | `"B2B" \| "B2C"` | Yes | Business or consumer customer |
| `customerCountry` | `string` | Yes | ISO 3166-1 alpha-2 country code of customer |
| `supplierCountry` | `string` | Yes | ISO 3166-1 alpha-2 country code of supplier |
| `productCategory` | `string` | Yes | Product/service category for rate and exemption lookup |
| `vatNumber` | `string \| null` | No | Customer VAT registration number (required for reverse charge) |

### VatOutput

| Field | Type | Description |
|-------|------|-------------|
| `netAmount` | `number` | Transaction amount before VAT (mirrors input) |
| `vatAmount` | `number` | Calculated VAT amount |
| `vatRate` | `number` | Rate applied as a decimal — e.g. `0.20` for 20%, **never** `20` |
| `grossAmount` | `number` | Total including VAT (`netAmount + vatAmount`) |
| `jurisdiction` | `string` | ISO country/region code of the jurisdiction applied |
| `isExempt` | `boolean` | `true` = VAT-exempt; `vatAmount` will be `0` |
| `invoiceLine` | `string` | Human-readable summary line for display on an invoice |

---

## VAT Rules

> Canonical source: [`docs/vat-rules.md`](vat-rules.md) — **all TBD**. Must be agreed before engine work begins.

Sections to fill in:
- Jurisdictions in scope
- VAT rates by country (standard, reduced, zero)
- B2B vs B2C treatment
- Exemptions and zero-rated goods
- Reverse charge mechanism

---

## Current Status

> As of 2026-02-25 — see [`docs/project-status.md`](project-status.md) for the live view.

| Area | Status |
|------|--------|
| Operating framework | **Complete** |
| Governance docs | **Complete** (TBDs to fill before coding) |
| Skill library | **Complete** |
| Tech stack | **TBD** |
| VAT rules | **TBD** |
| Application code | **Not started** |

**Immediate blockers before coding can begin:**
1. Fill `docs/architecture.md` — agree and document the tech stack
2. Fill `docs/vat-rules.md` — agree VAT scope and rates
3. Assign named owners to first sprint tickets in Jira
4. Run one end-to-end reviewer-gated ticket as a process rehearsal

---

## Way of Working

### Every Session — Start

```
1. git checkout dev && git pull origin dev
2. git checkout -b feature/<task-name>
3. Tell the agent: "You are working on the [module] module.
   Your scope is limited to /src/[module] and /tests/[module]."
4. Give the agent one focused task.
```

Context docs load automatically — `CLAUDE.md` imports `project-status.md`, `CHANGELOG.md`, `architecture.md`, `data-contracts.md`, and `vat-rules.md` at session start. No manual pasting needed.

### Every Session — End

```
1. Review all AI output against canonical docs before committing
2. Add CHANGELOG.md entry under [Unreleased]
3. Update docs/project-status.md
4. Commit code + both doc updates in the same commit
5. Open PR targeting dev (never main)
6. Batch all Jira updates: transitions, assignments, comments — applied in one go
```

### Review Gate

Every ticket must pass through a `reviewer-agent` before it moves to Done:

```
Open → In Progress → In Review → Done (PASS only)
                              ↘ stays In Review (FAIL)
```

A FAIL verdict blocks closure. Findings become new tickets. The implementing agent cannot close their own ticket.

### Jira Transition IDs (TC project)

| Status | ID |
|--------|----|
| Done | 151 |
| In Progress | 181 |
| In Review | 211 |
| Rejected | 171 |
| Cancelled | 191 |
| Open | 201 |

Batch script: `py C:\Users\gusv\.codex\skills\project-leader-agent\scripts\jira_batch_update.py --plan-file .\jira-plan.local.json`

---

## Agent Rules — What Agents Can and Cannot Do

### Always Allowed
- Write code within their assigned `/src/[module]/**` and `/tests/[module]/**` paths
- Read any canonical doc
- Implement logic that is explicitly documented in `docs/vat-rules.md`
- Ask for clarification when uncertain

### Never Allowed
- Touch files outside the assigned module paths
- Modify `/src/shared` without explicit team sign-off
- Rename or restructure fields defined in `docs/data-contracts.md`
- Implement VAT logic not documented in `docs/vat-rules.md`
- Add external dependencies without team discussion
- Modify `docs/architecture.md`, `docs/vat-rules.md`, or `docs/data-contracts.md` — human-maintained
- Update `docs/project-status.md` or `CHANGELOG.md` — human writes these
- Push to `main` or rewrite git history
- Guess when uncertain — must ask instead

---

## Agent Guardrails

These are active constraints every agent must apply to its own output before completing a response. They are not a review checklist — they are self-enforcement rules.

---

### Guardrail 1 — Field Names Are Immutable

Before outputting any field name, verify it character-for-character against `docs/data-contracts.md`.

- `vatAmount` is correct. `vatamount`, `VatAmount`, `vat_amount` are all wrong.
- `vatRate` must be a decimal (`0.20`), never a percentage integer (`20`).
- If you are about to use a field name that is not in `data-contracts.md`, **stop**. Do not invent it. Flag it to the human and ask for clarification.

**Self-check before output:** "Is every field name I have used present in `data-contracts.md`, exactly as written?"

---

### Guardrail 2 — Scope Is Hard-Bounded

You may only create or modify files within your assigned module paths:

| Module | Allowed paths |
|--------|--------------|
| engine | `/src/engine/**`, `/tests/engine/**` |
| api | `/src/api/**`, `/tests/api/**` |
| frontend | `/src/frontend/**` |
| shared | `/src/shared/**` — only with explicit team sign-off |

If completing the task requires touching a file outside these paths, **stop generating code**. State what you need and which path it would require. Do not proceed.

**Self-check before output:** "Have I generated or modified any file outside my assigned paths?"

---

### Guardrail 3 — VAT Logic Must Be Documented

You may only implement a VAT rule, rate, exemption, or behaviour that is explicitly present in `docs/vat-rules.md`.

- Do not add a fallback rate "in case the lookup fails".
- Do not handle a country or scenario that is not listed in the jurisdiction table.
- Do not infer a rule from a comment, a test name, or context — only from the doc.

If `vat-rules.md` does not cover the scenario you need, **stop**. Flag the gap to the human. Do not fill it with a reasonable-sounding assumption.

**Self-check before output:** "Is every VAT value, rate, and conditional branch I have written traceable to a specific entry in `vat-rules.md`?"

---

### Guardrail 4 — Implement Only What Was Asked

Your output must be limited to what was explicitly requested in the task.

- Do not add helper functions, utilities, or abstractions that weren't asked for.
- Do not refactor or rename existing code while implementing something new.
- Do not add validation, error handling, or edge cases beyond the stated scope.
- Do not leave TODO stubs or comments for things "you think might be needed next".

If you find yourself writing something and thinking "this might be useful later" — delete it.

**Self-check before output:** "Does every line I have written directly serve the task I was given?"

---

### Guardrail 5 — No New Dependencies

Do not introduce any new package, library, or import that was not already present in the codebase.

- Do not add entries to `package.json`, `requirements.txt`, or any equivalent file.
- Do not import a module you have not been told is available.
- If you need a dependency that isn't there, **stop**. Raise it with the team before writing code that depends on it.

**Self-check before output:** "Have I introduced any import or dependency that did not exist before this task?"

---

### Guardrail 6 — Uncertainty Requires a Stop, Not a Guess

If you are unsure about anything — a field name, a VAT rule, which file to edit, what already exists — you must stop and ask. Do not use confident language to paper over uncertainty.

- "I'll assume…" is not acceptable.
- "Typically this would be…" is not acceptable.
- "I'll use a sensible default…" is not acceptable.

State exactly what you are uncertain about and what information you need to proceed.

**Self-check before output:** "Is there anything in my output I am not certain about? If yes, have I flagged it explicitly rather than guessing?"

---

## Delivery Plan

> Full detail: [`docs/development-plan.md`](development-plan.md)

| Phase | Days | Focus | Gate |
|-------|------|-------|------|
| **0 — Foundation Lock** | Day 1 | Fill all TBDs in architecture, vat-rules; assign owners; validate tooling | All core docs agreed |
| **1 — Parallel Scaffolding** | Days 1–2 | Engine, API, frontend, shared scaffolds in parallel | `reviewer-agent` PASS per ticket |
| **2 — MVP Vertical Slice** | Days 2–3 | One end-to-end flow: input → API → engine → output → rendered | Contract compatibility check, code-review, security validation |
| **3 — Rule Expansion** | Days 3–4 | Expand VAT rules, edge/negative tests, API hardening, logging | Reviewer PASS + security validation per ticket |
| **4 — Stabilisation** | Day 5 | Regression pass, triage open issues, release checklist | No unresolved critical blockers |

---

## Skill Library

> All skills live in [`skills/`](../skills/). Use the Claude adapter in [`claude-skills/`](../claude-skills/) to build session prompts.

| Skill | Purpose |
|-------|---------|
| `project-leader-agent` | Roadmap, planning, ticket assignment, Jira batch execution |
| `developer-agent` | Scoped implementation with tests |
| `architect-agent` | Technical design and decision documentation |
| `reviewer-agent` | PASS/FAIL quality gate (use to close tickets) |
| `review-agent` | Deep code review — correctness, security, regressions |
| `project-manager-agent` | Cross-module consistency and system-level execution planning |
| `db-agent` | Database schema, migrations, performance, reliability |
| `designer-agent` | UX design and interaction spec |
| `vat-research-agent` | VAT compliance research with source traceability |

---

## Canonical Sources of Truth

These files are **human-maintained**. Agents must never modify them. They are the single source of authority for their domain.

| File | Governs |
|------|---------|
| [`docs/data-contracts.md`](data-contracts.md) | All field names and data shapes |
| [`docs/vat-rules.md`](vat-rules.md) | All VAT calculation logic |
| [`docs/architecture.md`](architecture.md) | Tech stack and system design |
| [`docs/project-status.md`](project-status.md) | What is built, in progress, and blocked |

---

## Key Reference Files

| File | Purpose |
|------|---------|
| [`CLAUDE.md`](../CLAUDE.md) | Hard constraints auto-loaded into every Claude Code session |
| [`docs/agent-rules.md`](agent-rules.md) | Full session protocol, module boundaries, drift detection |
| [`docs/prompt-templates.md`](prompt-templates.md) | 9 copy-paste prompts for every scenario |
| [`docs/jira-workflow.md`](jira-workflow.md) | Batched Jira update pattern and transition IDs |
| [`CHANGELOG.md`](../CHANGELOG.md) | Running log of every change — updated every PR |
| [`.github/PULL_REQUEST_TEMPLATE`](../.github/PULL_REQUEST_TEMPLATE/pull_request_template.md) | PR checklist |

# Agent Lessons, Dos and Don'ts (Claude + Codex)

## Purpose

Capture practical lessons from current agent work so the team can execute in parallel with low conflict and predictable quality.

## What We Learned

1. Constraint handling is the main quality lever. Weak constraints caused model drift.
2. Unclear plans create rework and inconsistent outputs.
3. Agents must ask clarification questions instead of making assumptions.
4. Requirement quality must be explicit up front: purpose, MVP usage, and security baseline.
5. Reviewer PASS/FAIL gating is essential before task closure.
6. Autonomous loops only work with fallback and strict stop conditions.

## Mandatory Requirement Brief (before any implementation)

Every ticket/spec must include:
1. Purpose: why this feature exists and what problem it solves.
2. MVP usage: who will use it, where, and under which conditions.
3. Functional scope: exact in-scope and out-of-scope behavior.
4. Security requirements: auth, input validation, secrets handling, logging/redaction, dependency policy.
5. Acceptance criteria: objective checks for completion.

If any field is missing, do not start implementation. Ask questions first.

## Do

1. Always start sessions with canonical docs:
   - `docs/project-status.md`
   - `docs/architecture.md`
   - `docs/data-contracts.md`
   - `docs/vat-rules.md` (engine work)
2. Require a written plan with phases, dependencies, and risks before coding.
3. Keep one ticket = one branch = one scoped task.
4. Enforce module boundaries (`engine`, `api`, `frontend`, `shared`).
5. Instruct agents to ask questions when uncertain instead of assuming.
6. Require explicit reviewer verdict (`PASS`/`FAIL`) before `Done`.
7. Batch Jira updates at end of session.
8. Use `project-leader-agent` for planning/coordination and `reviewer-agent` for closure gate.
9. Keep prompts explicit about allowed/forbidden files and expected outputs.
10. Log decisions/blockers in docs during the same commit as code.

## Don't

1. Do not let implementation agents close tickets directly.
2. Do not start from vague prompts without purpose and MVP usage context.
3. Do not allow agents to invent fields, VAT rules, architecture, or security assumptions.
4. Do not modify `/src/shared` without team sign-off.
5. Do not run ad-hoc Jira API calls during coding.
6. Do not accept "while I was at it" scope expansion.
7. Do not run autonomy without timeout/retry/fallback controls.

## Role Strategy (Claude + Codex in Unison)

1. `project-leader-agent`
   - Owns prioritization, assignment, sequencing, and Jira batch plan.
2. `developer-agent`
   - Implements scoped task only.
3. `reviewer-agent`
   - Returns PASS/FAIL with evidence.
4. `review-agent`
   - Deep bug/risk checks on larger changes.
5. `architect-agent` / `db-agent` / `designer-agent`
   - Used only when task requires those domains.

## Recommended Autonomy Levels

1. `L0` Advisory only (planning/specification).
2. `L1` Execute with mandatory reviewer PASS before `Done`. Default.
3. `L2` Execute and close automatically only for low-risk, repetitive tasks with proven tests.

Use `L1` as team default for first sprint.

## Guardrails for Autonomous Orchestration

1. Claude-first, Codex-fallback for token/limit events.
2. Hard stop on:
   - repeated FAIL reviews,
   - missing required docs,
   - unresolved blocker comments,
   - changes outside module scope.
3. Hard stop if requirement brief is incomplete (purpose, MVP usage, security).
4. Require manual approval for merge/deploy until stability is proven.

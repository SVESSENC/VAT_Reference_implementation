# Development Plan

## Goal

Build the VAT system in parallel with predictable quality using constrained agent workflows (Claude + Codex), reviewer gates, and shared contracts.

## Phase 0: Foundation Lock (Day 1)

Deliverables:
1. Finalize `docs/architecture.md` (remove all TBDs).
2. Confirm module ownership (`engine`, `api`, `frontend`, `shared`).
3. Confirm non-negotiable contracts in `docs/data-contracts.md`.
4. Confirm VAT scope in `docs/vat-rules.md`.
5. Validate tooling for all members (`git`, Claude CLI, Codex workflow, Jira access).

Exit criteria:
1. All core docs are agreed and updated.
2. First sprint tickets include purpose, MVP usage, security baseline, acceptance criteria.

## Phase 1: Parallel Scaffolding (Days 1-2)

Workstreams:
1. Engine lane (`developer-agent`): core VAT calculation scaffold + unit-test harness.
2. API lane (`developer-agent`): API skeleton, request validation scaffold, engine integration points.
3. Frontend lane (`developer-agent`): UI scaffold + form flow stub to API.
4. Shared lane (team-approved only): minimal shared types/constants needed by all lanes.

Gates:
1. `reviewer-agent` PASS/FAIL per ticket.
2. No `Done` without PASS.

## Phase 2: MVP Vertical Slice (Days 2-3)

Deliver one end-to-end flow:
1. Input captured in frontend.
2. API validates and routes request.
3. Engine computes VAT output.
4. Response rendered in frontend.
5. Test coverage for happy path + key edge cases.

Gates:
1. Contract compatibility check across modules.
2. `review-agent` on merged slice.
3. `validation-security-agent` on API/input boundaries.

## Phase 3: Rule Expansion and Hardening (Days 3-4)

Workstreams:
1. Expand VAT rules from documented scope.
2. Add negative/edge tests and integration tests.
3. Strengthen API error handling and validation.
4. Add observability/logging baseline.

Gates:
1. Reviewer PASS for each rule ticket.
2. Security validation on each API-affecting ticket.

## Phase 4: Stabilization and Release Readiness (Day 5)

Deliverables:
1. Regression pass.
2. Open issues triaged by severity.
3. Release checklist reviewed.
4. Project status and changelog updated.

Exit criteria:
1. MVP objectives met.
2. No unresolved critical blockers.
3. Team agrees go/no-go for next sprint.

## Operating Model (Applies All Phases)

1. One ticket = one branch = one owner.
2. Batch Jira updates at session end.
3. Implementation agents cannot directly close tickets.
4. Contract/type changes require team approval first.
5. Shared module edits require team sign-off.
6. If requirement brief is incomplete, agent must ask questions and pause.

## Agent Role Assignment

1. `project-leader-agent`: planning, sequencing, assignment, Jira batch ownership.
2. `developer-agent`: implementation within module boundary.
3. `reviewer-agent`: PASS/FAIL gate.
4. `review-agent`: deep correctness/regression review.
5. `validation-security-agent`: security and runtime validation.
6. Specialist agents (`architect`, `db`, `designer`, `vat-research`) on-demand.

## Weekly Cadence

1. Daily 15-minute standup:
   - yesterday done, today target, blockers.
2. Midday integration check:
   - confirm branch health and cross-lane dependencies.
3. End-of-day Jira batch:
   - assignments, transitions, and comments.

## Immediate Next Actions

1. Fill architecture TBDs.
2. Assign owners for first sprint tickets.
3. Run one reviewer-gated ticket end-to-end as a process rehearsal.
4. Start parallel Phase 1 workstreams.

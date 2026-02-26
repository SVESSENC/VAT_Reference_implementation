# Parallel Work Operating Playbook (Monday Ready)

## Purpose

Give the team one clear operating document for working in parallel with Claude + Codex, using the agent and skill setup already created in this project.

## 1. What We Need To Work In Parallel

1. Shared source of truth
   - `docs/project-status.md`
   - `docs/architecture.md`
   - `docs/data-contracts.md`
   - `docs/vat-rules.md` (engine logic)
2. Strict branch strategy
   - `main` = production only
   - `dev` = integration
   - `feature/<ticket>` = one ticket per branch
3. Clear ownership
   - One human owner + one primary agent combo per ticket
   - Module boundaries must be explicit (`engine`, `api`, `frontend`, `shared`)
4. Review gate
   - No ticket moves to `Done` without reviewer PASS
5. Jira discipline
   - Batch updates only (assignee/status/comment together)

## 2. Current Capabilities We Have Built

### 2.1 Agent + Skill Capabilities

1. Vendored skill library in repo:
   - `skills/` (architect, db, designer, developer, review, reviewer, project-manager, project-leader, vat-research)
2. Project leadership skill:
   - `project-leader-agent` with role/gate constraints and Jira integration guidance
3. Reviewer-driven closure:
   - PASS/FAIL workflow documented and wired into Jira process
4. Claude adapter:
   - `claude-skills/` prompt builder to reuse skills in Claude sessions

### 2.2 Automation Capabilities

1. Jira batch updater:
   - assign issues, transition statuses, add comments
2. Autonomous orchestrator:
   - picks next ticket, assigns worker, runs implement + review steps, updates Jira
3. Claude-first + Codex-fallback execution:
   - primary command uses Claude
   - fallback to Codex on quota/rate-limit patterns

## 3. Non-Negotiable Rules

## 3.1 Data and Type Integrity (Immutable Without Team Approval)

1. Types and field names from `docs/data-contracts.md` are immutable during implementation.
2. No renaming/restructuring of agreed contract fields.
3. No undocumented additions to request/response shapes.
4. If a contract change is needed:
   - stop implementation,
   - discuss with team,
   - update docs first,
   - then implement.

## 3.2 VAT Logic Integrity

1. VAT rules must match `docs/vat-rules.md` exactly.
2. No “reasonable defaults” or guessed tax logic.
3. If rule is unclear/missing, ask question and pause.

## 3.3 Scope and Module Boundaries

1. Agent must stay inside assigned module paths.
2. `/src/shared` changes require explicit team sign-off.
3. Out-of-scope edits are rejected, not “cleaned up later.”

## 3.4 Security Baseline (Required Per Ticket)

Each ticket must define:
1. Purpose (why this exists)
2. MVP usage (who uses it and how)
3. Security requirements:
   - input validation
   - auth/authz expectations
   - secret handling
   - logging/redaction expectations
4. Acceptance criteria

If missing, agent asks clarifying questions and does not start coding.

## 4. Standard Ticket Flow (Parallel Safe)

1. `Open` -> Project leader assigns owner/agent combo
2. Move to `In Progress` when branch starts
3. Developer agent implements within scope
4. Reviewer agent returns `PASS` or `FAIL`
5. If `PASS`: Jira batch move to `Done` + completion comment
6. If `FAIL`: stay active, create follow-up fix tasks, re-run review

## 5. Meeting Decisions Required Monday

1. Finalize tech stack in `docs/architecture.md` (remove TBDs)
2. Assign module owners (human + backup)
3. Approve reviewer gate owner(s)
4. Approve autonomy level (`L1` default: execute + mandatory review)
5. Approve first sprint ticket allocation and dependencies

## 6. Definition of Ready (Team Can Start Immediately)

All must be true:
1. Architecture and stack are finalized.
2. Module ownership is documented.
3. First sprint tickets include purpose, MVP usage, security, acceptance criteria.
4. Reviewer PASS process is rehearsed on one real ticket.
5. Jira batch update flow works for all team members.
6. Claude + Codex command access is validated for all team members.

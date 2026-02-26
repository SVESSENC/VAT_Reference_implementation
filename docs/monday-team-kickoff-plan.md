# Monday Team Kickoff Plan (Parallel Delivery)

## Objective

Walk into Monday with zero ambiguity: shared workspace ready, roles clear, versioning stable, and first sprint tickets executable immediately.

## 0. Readiness Status

Current setup is close, but not fully ready for full-speed parallel implementation.

Open prerequisites before coding starts:
1. Finalize tech stack in `docs/architecture.md` (currently TBD).
2. Assign module ownership (engine/api/frontend/shared).
3. Confirm merge policy and reviewer responsibilities.
4. Validate Claude/Codex command availability for all team members.

## 1. Meeting Deliverables

By end of meeting, produce and approve:
1. Final role matrix (human owner + agent owner per module).
2. Remote workspace setup checklist and owners.
3. Versioning/branching and PR gate policy.
4. Sprint-1 ticket allocation with dependencies.
5. Agent operating constraints and autonomy level (`L1` default).
6. Product requirement baseline: purpose, MVP usage model, and security requirements.

## 2. Shared Remote Workspace Setup

1. Repo and branch protections
   - Protect `main` and `dev`
   - Require PR + reviewer for merge to `dev`
2. Secrets and credentials
   - Standardize local `.env.jira.local`
   - Ensure no token leakage in chat/docs/commits
3. Tooling parity
   - Confirm `git`, `node/python` runtime, `claude` CLI, Codex workflow access
4. Shared artifacts
   - Ensure all skills in `skills/`
   - Ensure Claude adapter in `claude-skills/`

## 3. Ways of Working and Communication

1. Daily sync (15 minutes)
   - Yesterday done / today target / blockers
2. Async channel template
   - `Ticket`, `Branch`, `Status`, `Blocker`, `Next action`
3. Blocker SLA
   - Escalate blockers within 30 minutes
4. Decision logging
   - Log all significant decisions in `docs/project-status.md`

## 4. Versioning Strategy for Parallel Work

1. Branch model
   - `main` (production), `dev` (integration), `feature/<ticket>`
2. One ticket per branch
3. Rebase/merge policy
   - Pull `dev` before each agent session
4. PR gate
   - Reviewer PASS required
   - Required checks: tests + scope verification + contract/rule checks
5. Jira workflow
   - `Open -> In Progress -> In Review -> Done`
   - Done only after reviewer PASS

## 5. Team of Agent Roles

1. Project Leader
   - plans milestones, assigns tickets, updates Jira in batch
2. Developer
   - scoped implementation only
3. Reviewer
   - PASS/FAIL gate with findings
4. Specialist pool
   - architect/db/designer/review-agent on demand

## 6. Agent Setup with Restrictions

1. Mandatory context docs per session:
   - `project-status`, `architecture`, `data-contracts`, `vat-rules` (engine)
2. Forbidden actions:
   - shared edits without approval
   - undocumented field/rule changes
   - direct Done transitions by implementer
3. Closure rule:
   - reviewer PASS -> Jira Done batch update
4. Automation rule:
   - Claude-first, Codex fallback on quota/limit

## 6.1 Requirement Gate (must pass before coding)

Each ticket must include:
1. Purpose statement.
2. MVP usage scenario (who uses it, where, and how).
3. Security baseline requirements.
4. Acceptance criteria.

If missing, the assigned agent must ask questions and pause implementation.

## 7. Development Strategy (First Week)

1. Day 1 (Monday): foundation lock
   - finalize architecture + tech stack + ownership
2. Day 2-3: module scaffolding and first vertical slice
3. Day 4: integration hardening + reviewer-driven fixes
4. Day 5: stabilization and sprint retrospective

## 8. Monday Execution Timeline

1. 09:00-09:30: finalize architecture and tech stack.
2. 09:30-10:00: confirm ownership and ticket assignments.
3. 10:00-10:30: validate tools, skills, CLI access.
4. 10:30-12:00: start first wave of feature branches.
5. 13:00-15:00: reviewer passes and integration to `dev`.
6. 15:00-16:00: blocker resolution + plan adjustment.

## 9. First-Ticket Allocation Template

Use this in the meeting for each initial ticket:
1. Ticket:
2. Human owner:
3. Agent combo:
4. Module scope:
5. Dependencies:
6. Acceptance criteria:
7. Review gate:
8. Jira transition plan:

## 10. Definition of "Ready to Start Monday"

All items must be true:
1. `docs/architecture.md` no longer has TBD stack fields.
2. Every module has named owner.
3. First sprint tickets have owners and acceptance criteria.
4. Reviewer gate process is rehearsed on one test ticket.
5. Orchestrator dry-run and one live controlled run are successful.
6. Purpose + MVP usage + security baseline are defined for sprint tickets.

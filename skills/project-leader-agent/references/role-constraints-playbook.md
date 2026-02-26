# Role Constraints Playbook

Use this playbook to keep autonomous delivery controlled and audit-friendly.

## Autonomy Levels

- `L0 advisory`: Agent can analyze and recommend, but cannot execute changes.
- `L1 execute-with-review`: Agent can implement and propose updates; closure requires reviewer PASS.
- `L2 execute-and-close`: Agent can implement and close tasks automatically. Use only for low-risk, well-bounded tasks.

Default to `L1` unless user explicitly chooses otherwise.

## Role Boundary Template

Define this per agent before task start:

- Allowed actions
- Forbidden actions
- Input contracts (which docs/files are mandatory)
- Output contracts (required artifacts and format)
- Completion gate (who can mark done)
- Escalation triggers

If any boundary is unclear, block task start and request clarification.

## Recommended Baseline by Role

- Project leader
  - Allowed: prioritize, assign, sequence, replan, gate decisions
  - Forbidden: shipping code without delegation
  - Completion gate: reviewer PASS + Jira update batch

- Developer
  - Allowed: implement within scoped files, add tests, report verification
  - Forbidden: cross-module edits outside scope, direct task closure
  - Completion gate: reviewer PASS

- Reviewer
  - Allowed: PASS/FAIL verdict, findings, risk notes, required fixes
  - Forbidden: silent approval without evidence
  - Completion gate: explicit verdict output

- Architecture/DB/Designer specialists
  - Allowed: domain-specific design and change specs
  - Forbidden: merging unrelated implementation
  - Completion gate: accepted spec plus downstream validation

## Gate Policy

Do not move task to Done until all required gates pass:

1. Implementation artifacts present
2. Validation checks pass (tests/lint/security where relevant)
3. Reviewer verdict is PASS
4. Jira update includes completion comment with evidence

If any gate fails, keep ticket active and create a bounded follow-up task.

## Handoff Contract

Every handoff must include:

- Summary of what changed
- Files touched
- Verification performed
- Known risks/open questions
- Exact next owner and next action

Reject handoff if any field is missing.

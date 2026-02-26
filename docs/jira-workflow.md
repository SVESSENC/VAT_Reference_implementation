# Jira Way of Working

> How this team uses Jira: conventions, batching rules, and rate limit guidance.
> Project: **testing claude** (key: `TC`) on `datahubdev.atlassian.net`

---

## Core principle: batch Jira updates, do not drip them

The Atlassian API is rate-limited. Single-call updates during active coding sessions are noisy and likely to hit limits.

**Rule: collect Jira changes for a session and apply them in one batch at the end.**

---

## Batching pattern

### During a work session
Do your work first. Keep a local note:

```text
Jira updates to apply at end of session:
- TC-15 -> Done
- TC-13 -> Done
- TC-10 -> In Progress
- TC-10: add comment "Started prompt-templates.md"
```

### At the end of the session
Apply updates in this order:
1. Transitions (Done, In Progress, In Review, etc.)
2. Comments
3. If a transition fails, fix that first and rerun the batch

### Spacing
Leave a short delay between API calls. If you hit HTTP 429, use the backoff guidance below.

---

## Handling rate limits (HTTP 429)

When a request returns `429 Too Many Requests`:
1. Prefer `Retry-After` or `X-RateLimit-Reset` headers if present.
2. If needed, use exponential backoff:
   - Attempt 1 failed -> wait `15s`
   - Attempt 2 failed -> wait `30s`
   - Attempt 3 failed -> wait `60s`
   - Attempt 4 failed -> wait `120s`
3. After 4 failures, stop and continue next session.

---

## Ticket lifecycle

```text
Open -> In Progress -> In Review -> Done
                           \-> Rejected
```

| Status | When to use |
|--------|-------------|
| Open | Default: ticket not yet started |
| In Progress | Branch created and active work started |
| In Review | PR open and awaiting review |
| Done | Review gate is PASS and work is complete (normally merged to `dev`) |
| Rejected | Task descoped or no longer needed |

**One ticket = one feature branch.** Move to `In Progress` when branch work starts.

---

## Reviewer gate -> Done rule

For tickets that require formal review:
1. Run `reviewer-agent` and get an explicit verdict (`PASS` or `FAIL`).
2. If verdict is `PASS`, include the ticket in your batch plan with `to: "Done"`.
3. Add a completion comment that references the review pass.
4. Execute the batch script:
   `py C:\Users\gusv\.codex\skills\project-leader-agent\scripts\jira_batch_update.py --plan-file .\jira-plan.local.json`

If verdict is `FAIL`, do not move to `Done`. Keep it in `In Progress` or `In Review` and log follow-up fixes.

---

## What to put in ticket comments

Add a comment when:
- You move a ticket to `Done`
- You move a ticket to `In Progress`
- You discover a blocker
- You make a significant decision

Keep comments short and factual.

**Comment template: moving to In Progress**
```text
Started on branch: feature/<name>
Scope: [what this ticket covers]
```

**Comment template: moving to Done**
```text
Completed on branch: feature/<name> -> merged to dev
Deliverable: [file path or feature description]
Review: reviewer-agent PASS [YYYY-MM-DD]
Notes: [anything important for the team]
```

**Comment template: blocker**
```text
Blocked: [description]
Needs: [what unblocks it]
Raised: [YYYY-MM-DD]
```

---

## Transition IDs (TC project)

| Transition | ID |
|-----------|-----|
| Done | `151` |
| In Progress | `181` |
| In Review | `211` |
| Rejected | `171` |
| Cancelled | `191` |
| Open (reopen) | `201` |

---

## End-of-session Jira checklist

```text
[ ] Reviewer verdict captured for tickets under review
[ ] PASS tickets transitioned to Done
[ ] Active ticket transitioned to In Progress or In Review
[ ] Comments added to Done tickets
[ ] Blockers documented
[ ] Updates applied in one batch
```

---

## Ticket -> branch -> PR naming

| Ticket | Branch | PR title |
|--------|--------|---------|
| TC-10 | `feature/TC-10-prompt-templates` | `feat: add shared prompt templates (TC-10)` |
| TC-18 | `feature/TC-18-vat-engine-core` | `feat: build core VAT calculation engine (TC-18)` |
| TC-12 | `feature/TC-12-vat-rules-doc` | `docs: document VAT rules and jurisdictions (TC-12)` |

Include the ticket number in branch and PR names.

---

## Jira automation boundaries

- Do not make ad-hoc Jira API calls during implementation.
- Do not let random coding agents decide transitions.
- Allowed: `project-leader-agent` applies a prepared batch plan.
- Allowed: `reviewer-agent` verdict can trigger Done in that batch plan.

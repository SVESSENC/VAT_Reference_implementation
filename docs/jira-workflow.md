# Jira Way of Working

> How this team uses Jira — conventions, batching rules, and rate limit guidance.
> Project: **testing claude** (key: `TC`) on datahubdev.atlassian.net

---

## Core principle: batch Jira updates, don't drip them

The Atlassian API is rate-limited. Making one API call per ticket update — especially when an agent or automation is running — will hit the limit quickly and block all subsequent calls.

**Rule: collect all Jira changes for a session and apply them together at the end, not one-by-one as you go.**

---

## Batching pattern

### During a work session
Do your work. Don't touch Jira. Keep a local scratch note of what needs updating:

```
Jira updates to make at end of session:
- TC-15 → Done
- TC-13 → Done
- TC-10 → In Progress
- TC-10: add comment "Started prompt-templates.md"
```

### At the end of the session
Apply all updates in one block, with a short pause between calls:
1. Transition all tickets that changed status (Done, In Progress, etc.)
2. Add comments to tickets where context is needed
3. Do transitions before comments — if the transition fails due to rate limiting, comments are less critical

### Spacing
Leave at least a few seconds between Jira API calls. If you hit a 429 (rate limited), wait 15–30 seconds before retrying. Do not retry in a tight loop.

---

## Ticket lifecycle

```
Open → In Progress → In Review → Done
                              ↘ Rejected
```

| Status | When to use |
|--------|-------------|
| Open | Default — ticket not yet started |
| In Progress | You have created a branch and are actively working on it |
| In Review | PR is open and awaiting review |
| Done | PR is merged to `dev`, work is complete |
| Rejected | Task was descoped or not needed |

**One ticket = one feature branch.** Move a ticket to In Progress when you create the branch, not before.

---

## What to put in ticket comments

Add a comment when:
- You move a ticket to Done — summarise what was built and where it lives
- You move a ticket to In Progress — state the branch name
- You discover a blocker — describe it so the team knows the ticket is stuck
- You make a significant decision mid-task — log it here and in `docs/project-status.md`

Keep comments short and factual. Other team members (and agents reading the backlog) need the key facts, not a narrative.

**Comment template — moving to In Progress:**
```
Started on branch: feature/<name>
Scope: [what this ticket covers]
```

**Comment template — moving to Done:**
```
Completed on branch: feature/<name> → merged to dev
Deliverable: [file path or feature description]
Notes: [anything the team needs to know — e.g. "only covers EU jurisdictions, US TBD"]
```

**Comment template — blocker:**
```
Blocked: [description of blocker]
Needs: [what's required to unblock]
Raised: [date]
```

---

## Transition IDs (datahubdev TC project)

Use these when calling the Atlassian API to avoid an extra round-trip for the transitions list:

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

Before closing your work session:

```
[ ] All completed tickets transitioned to Done
[ ] Active ticket transitioned to In Progress (if mid-task) or In Review (if PR open)
[ ] Comments added to Done tickets summarising what was built
[ ] Blocker comments added if anything is stuck
[ ] All transitions applied in one batch, not one-by-one during work
```

---

## Ticket → branch → PR naming

Keep naming consistent so tickets, branches, and PRs are easy to correlate.

| Ticket | Branch | PR title |
|--------|--------|---------|
| TC-10 | `feature/TC-10-prompt-templates` | `feat: add shared prompt templates (TC-10)` |
| TC-18 | `feature/TC-18-vat-engine-core` | `feat: build core VAT calculation engine (TC-18)` |
| TC-12 | `feature/TC-12-vat-rules-doc` | `docs: document VAT rules and jurisdictions (TC-12)` |

Include the ticket number in the branch name and PR title. This makes it trivial to find the related ticket when reviewing a PR or commit.

---

## What agents should not do with Jira

- Do not ask an agent to make Jira API calls directly
- Do not ask an agent to decide which tickets to move or close
- Do not let an agent write ticket comments — you write them, based on what the agent produced
- Agents work in code. Jira updates are a human responsibility done at session end

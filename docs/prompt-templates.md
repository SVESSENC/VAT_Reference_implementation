# Shared Prompt Templates

> **TC-10** — Reusable agent prompts for common development tasks.
> Use these as starting points. Always paste the required context docs (listed per template) before sending.
>
> These templates are for Claude and ChatGPT. Adjust phrasing slightly for each — both follow the same structure.

---

## How to use these templates

1. Open a fresh agent session — context docs load automatically via `CLAUDE.md`
2. Tell the agent its module: `"You are working on the [module] module"`
3. Copy the template, fill in the `[PLACEHOLDERS]`, and send it
4. Review all output before committing anything

> **Note on "Auto-loaded" labels below:** docs marked as auto-loaded are imported by `CLAUDE.md` at session start — you do not need to paste them. Docs marked as "paste manually" must still be provided by you because they are not in the auto-load list.

---

## Standing rule — applies to every template below

> Add this line to the end of every prompt you send, without exception:
>
> **"If you are uncertain about any field name, VAT rule, tech stack choice, or whether something already exists — stop and tell me rather than guessing. Do not invent answers to fill gaps."**

This is your single most effective defence against agent drift. An agent that halts and asks is always better than one that silently invents.

---

## 1. Scaffold a new function in your module

**Context:** `project-status.md`, `CHANGELOG.md`, `data-contracts.md`, `architecture.md` — all auto-loaded

```
You are working on the [engine | api | frontend] module of a VAT calculation application.
Your scope is strictly limited to /src/[module] and /tests/[module].

I need you to implement a function called [FUNCTION_NAME] in [FILE_PATH].

Purpose: [one sentence describing what it does]

Input: [describe the input — use field names from data-contracts.md exactly]
Output: [describe the output — use field names from data-contracts.md exactly]

Constraints:
- Use [LANGUAGE/FRAMEWORK] consistent with the existing code in this module
- Do not import from or modify any other module
- Do not invent field names — use only the names defined in the data contracts I pasted above
- Include JSDoc / docstring comments on the function signature only

Existing related code for context:
[paste relevant existing functions or types here]

Write the function only. Do not generate tests yet.

If you are uncertain about any field name, rule, or approach — stop and tell me rather than guessing.
```

---

## 2. Write unit tests for an existing function

**Context:** `project-status.md`, `data-contracts.md`, `vat-rules.md` — all auto-loaded. **Paste manually:** the function code you want tested

```
You are writing unit tests for the [engine | api] module of a VAT calculation application.
Your scope is strictly /tests/[module].

Here is the function I need tests for:

[PASTE FUNCTION CODE HERE]

Write unit tests covering:
1. The happy path with typical valid input
2. Edge cases: [list the specific edge cases relevant to this function]
3. Invalid / boundary input that should be rejected or handled gracefully

Rules:
- Use [JEST | MOCHA | PYTEST | other test framework] consistent with the project
- Test function names must clearly describe the scenario being tested
- Do not mock more than necessary — prefer real inputs from the data contracts
- Each test must have a single clear assertion
- Do not modify the function under test

Return only the test file content.

If you are uncertain about any field name, rule, or behaviour — stop and tell me rather than guessing.
```

---

## 3. Add a VAT calculation rule to the engine

**Context:** `project-status.md`, `CHANGELOG.md`, `data-contracts.md`, `vat-rules.md`, `architecture.md` — all auto-loaded. **Paste manually:** existing engine code for context

```
You are working on the engine module of a VAT calculation application.
Your scope is strictly /src/engine and /tests/engine.

I need to implement the following VAT rule:

Rule name: [NAME FROM vat-rules.md]
Description: [copy the rule description from vat-rules.md]
Applies when: [conditions — e.g. "customerType is B2B AND customerCountry != supplierCountry"]
Effect: [what it changes — e.g. "vatRate becomes 0, isExempt becomes true"]

The VatInput and VatOutput types are defined in the data contracts I pasted above.
Use those field names exactly — do not rename or restructure them.

Existing engine code for context:
[paste relevant existing engine functions]

Implement only this rule. Do not refactor existing code.
Return the implementation and the corresponding unit tests separately.

If you are uncertain about the rule, any field name, or edge cases not covered in vat-rules.md — stop and tell me rather than guessing.
```

---

## 4. Add an API endpoint

**Context:** `project-status.md`, `CHANGELOG.md`, `data-contracts.md`, `architecture.md` — all auto-loaded. **Paste manually:** existing route/handler code for context

```
You are working on the api module of a VAT calculation application.
Your scope is strictly /src/api and /tests/api.

I need to add a new REST endpoint:

Method: [GET | POST | PUT | DELETE]
Path: [/path/here]
Purpose: [one sentence]
Request body: [describe fields, or refer to data-contracts.md input shape]
Response body: [describe fields, or refer to data-contracts.md output shape]
Error cases to handle: [list expected error scenarios and their HTTP status codes]

The endpoint must delegate calculation logic to the engine module — do not implement VAT logic in the API layer.
Use the existing routing and middleware patterns in the api module (shown below):

[paste existing route/handler code]

Return the route handler and a basic integration test. Do not generate OpenAPI docs yet.

If you are uncertain about the request/response shapes, routing patterns, or error handling — stop and tell me rather than guessing.
```

---

## 5. Explain a piece of existing code

**Context:** none required. **Paste manually:** the code you want explained

```
Explain the following code from the [module] module of a VAT calculation application.

[PASTE CODE]

Tell me:
1. What this code does in plain English
2. What inputs it expects and what it returns
3. Any edge cases or assumptions baked in
4. Anything that looks risky or unclear

Do not suggest improvements. Just explain.

If any part of the code is genuinely ambiguous and you cannot explain it with confidence — say so rather than guessing at intent.
```

---

## 6. Review AI-generated code before committing

**Context:** `data-contracts.md`, `vat-rules.md` — auto-loaded. **Paste manually:** the code to review

```
Review the following AI-generated code for the [module] module of a VAT calculation application.

[PASTE CODE]

Check for:
1. Field names — do they exactly match the data contracts I pasted above? Flag any that don't.
2. VAT logic correctness — does it follow the rules in vat-rules.md? Flag any deviation.
3. Scope — does it touch anything outside /src/[module] or /tests/[module]? Flag if so.
4. Security — any injection risks, unvalidated input, or exposed internals?
5. Obvious bugs — off-by-one, null handling, type mismatches

Return a bullet list of findings only. Do not rewrite the code.

If you are uncertain whether something is a genuine issue or just unfamiliar to you — say so explicitly rather than flagging it as a definite problem.
```

---

## 7. Update docs/project-status.md after completing a task

> This template is for you (the human) to fill in — do not send this to an agent.
> Agents must never update project-status.md directly.

```
After completing [TASK / TICKET]:

In docs/project-status.md:
1. Move [COMPONENT] from "What Has Not Been Started" to "What Is Up and Running"
   - Location: [file path]
   - Notes: [any caveats — e.g. "only handles B2C, B2B reverse charge not yet implemented"]

2. If relevant, remove from "What Is In Progress"

3. Log any decisions made:
   Date: [today]
   Decision: [what was decided]
   Rationale: [why]
   Decided by: [who]

4. Log any blockers discovered:
   Description: [what's blocked]
   Module: [which module]
   Status: Raised
```

---

## 8. Write a CHANGELOG entry

> This template is for you (the human) — do not send to an agent.

```
### [YYYY-MM-DD] [module] — [short description of what changed]
**Who:** [your name / role]
**Branch:** feature/[branch-name]
**Files changed:**
- `[path/to/file]` — [what changed and why]
- `[path/to/file]` — [what changed and why]
**Notes:** [anything the next person needs to know — field renames, new dependencies, behaviour changes]
```

---

## 10. Session bootstrap — pick next Jira ticket and run full cycle

**Context:** all docs auto-loaded. No manual paste needed.

```
Run the session auto-start loop from CLAUDE.md:

1. Search Jira: project = TC AND status = "Open" ORDER BY priority DESC, created ASC — take the first result.
2. Read the full ticket: summary, description, acceptance criteria.
3. Infer the module (engine / api / frontend / shared). If unclear, ask me.
4. Announce the ticket and module. Move it to In Progress via Jira MCP (transition ID 181). Add an In Progress comment.
5. Implement the work within the module boundary. Apply all guardrails from agent-rules.md.
6. Run the reviewer gate. Produce a PASS or FAIL verdict.
7. If PASS: transition to Done (transition ID 151), add completion comment, report back to me.
   If FAIL: transition to In Review (transition ID 211), list findings, do not close the ticket.

Stop at any point and ask me if:
- architecture.md or vat-rules.md are still TBD
- the module is shared (needs team sign-off)
- the ticket description is too vague to act on safely
```

---

## 9. Reviewer gate with Jira completion output

**Context:** `project-status.md`, `data-contracts.md`, `vat-rules.md` — auto-loaded. **Paste manually:** PR diff or list of changed files

```text
You are acting as reviewer-agent for ticket [TC-XX].

Review scope:
- Files changed: [list]
- Ticket objective: [one sentence]
- Acceptance criteria: [list]

Return exactly these sections:
1. Verdict: PASS or FAIL
2. Findings: bullet list (empty if PASS)
3. Jira Plan Snippet (JSON):
   - If PASS: include a move to Done and a completion comment
   - If FAIL: include a comment only, no move to Done

Output format:
Verdict: [PASS|FAIL]
Findings:
- ...
Jira Plan Snippet:
{
  "moves": [
    { "issue": "[TC-XX]", "to": "Done" }
  ],
  "comments": [
    {
      "issue": "[TC-XX]",
      "body": "Review: reviewer-agent PASS [YYYY-MM-DD]\\nDeliverable: [summary]\\nNotes: [optional]"
    }
  ]
}

Rules:
- Do not guess. If evidence is missing, return FAIL and list what is missing.
- If there is any correctness or security risk, return FAIL.
```

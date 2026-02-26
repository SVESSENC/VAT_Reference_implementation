# Shared Prompt Templates

> **TC-10** — Reusable agent prompts for common development tasks.
> Use these as starting points. Always paste the required context docs (listed per template) before sending.
>
> These templates are for Claude and ChatGPT. Adjust phrasing slightly for each — both follow the same structure.

---

## How to use these templates

1. Open a fresh agent session
2. Paste the **required context** files listed under each template
3. Copy the template, fill in the `[PLACEHOLDERS]`, and send it
4. Review all output before committing anything

---

## 1. Scaffold a new function in your module

**Required context:** `docs/project-status.md`, `CHANGELOG.md [Unreleased]`, `docs/data-contracts.md`, `docs/architecture.md`

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
```

---

## 2. Write unit tests for an existing function

**Required context:** `docs/project-status.md`, `docs/data-contracts.md`, `docs/vat-rules.md` (if engine)

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
```

---

## 3. Add a VAT calculation rule to the engine

**Required context:** `docs/project-status.md`, `CHANGELOG.md [Unreleased]`, `docs/data-contracts.md`, `docs/vat-rules.md`, `docs/architecture.md`

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
```

---

## 4. Add an API endpoint

**Required context:** `docs/project-status.md`, `CHANGELOG.md [Unreleased]`, `docs/data-contracts.md`, `docs/architecture.md`

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
```

---

## 5. Explain a piece of existing code

**Required context:** none required, but paste the relevant file

```
Explain the following code from the [module] module of a VAT calculation application.

[PASTE CODE]

Tell me:
1. What this code does in plain English
2. What inputs it expects and what it returns
3. Any edge cases or assumptions baked in
4. Anything that looks risky or unclear

Do not suggest improvements. Just explain.
```

---

## 6. Review AI-generated code before committing

**Required context:** `docs/data-contracts.md`, `docs/vat-rules.md` (if engine code)

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

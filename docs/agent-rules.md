# Agent Rules — AI-Only Team Workflow

> This project is built by a team of 4 humans, each working exclusively with AI agents (Claude, ChatGPT, or similar).
> These rules exist because AI agents have no shared memory, no awareness of other agents' work, and no ability to resolve conflicts on their own.
> Every team member is responsible for enforcing these rules before, during, and after every agent session.

---

## 1. Before Starting Any Agent Session

**Every session, without exception:**

1. **Pull the latest `dev` branch** before starting:
   ```bash
   git checkout dev
   git pull origin dev
   git checkout -b feature/<your-task-name>
   ```

2. **Context docs are loaded automatically.** `CLAUDE.md` imports `project-status.md`, `CHANGELOG.md`, `architecture.md`, `data-contracts.md`, and `vat-rules.md` on every session start — no pasting required.

3. **Tell the agent your module.** Start every session with:
   > "You are working on the `[engine | api | frontend | shared]` module of a VAT calculation application. Your scope is limited to `/src/[module]` and `/tests/[module]`."

4. **Read the project-status.md "What Is In Progress" table** before starting. If someone else is mid-way through a related component, coordinate before writing code that will conflict.

---

## 2. Module Boundaries — What Each Agent Can Touch

| Role | Module | Allowed Paths | Forbidden Paths |
|------|--------|--------------|----------------|
| Engine Dev | engine | `/src/engine/**`, `/tests/engine/**` | Everything else |
| API Dev | api | `/src/api/**`, `/tests/api/**` | Everything else |
| Frontend Dev | frontend | `/src/frontend/**` | Everything else |
| Shared (team) | shared | `/src/shared/**` | Must have team approval before any change |

**Hard rules:**
- An agent prompt must never ask to create or modify files outside the agent's assigned module paths.
- If the agent generates code that touches another module, discard it and rephrase the prompt.
- If you need a change in `/src/shared`, stop and discuss with the full team before involving any agent.

---

## 3. Prompting Discipline

### Do
- Give the agent one focused task per session. Long multi-task prompts lead to scope creep.
- Provide the input/output shapes from `docs/data-contracts.md` explicitly in your prompt.
- Tell the agent what already exists: "There is already a function called `calculateVat` that returns `VatOutput`. Build on top of that."
- Ask the agent to explain its reasoning before writing code when the logic is complex.

### Do Not
- Do not ask an agent to "figure out the architecture" — that is already defined in `docs/architecture.md`.
- Do not ask an agent to "design the data model" — that is already defined in `docs/data-contracts.md`.
- Do not ask an agent to modify or suggest changes to another person's module.
- Do not let an agent commit directly. You commit. You review first.
- Do not chain multiple agent sessions without pulling `dev` between them.

---

## 4. Reviewing AI-Generated Code

Before committing **any** AI-generated code, the human must verify:

- [ ] Every field name matches `docs/data-contracts.md` exactly (case-sensitive)
- [ ] Every VAT calculation rule matches `docs/vat-rules.md` exactly
- [ ] The code only touches files within the assigned module
- [ ] No new dependencies are introduced without team discussion
- [ ] No hardcoded values that should come from configuration or shared constants
- [ ] No commented-out code, debug logs, or TODO stubs left in
- [ ] Tests exist for the generated logic and actually test the right behaviour

---

## 5. Handling Conflicts Between Agents

Because each agent works independently with no shared state, conflicts are inevitable. Follow this process:

1. **Data contract conflicts:** If an agent suggests a field name or shape that differs from `docs/data-contracts.md`, the doc wins. Update your prompt, not the doc (unless the team agrees the doc is wrong, in which case update the doc first and announce it).

2. **Logic conflicts:** If two agents produce different implementations of the same function, compare both against `docs/vat-rules.md`. The one that correctly implements the documented rules is correct.

3. **Merge conflicts in shared files:** If `/src/shared` has a merge conflict, stop. Do not let any agent resolve it. The team resolves it together.

4. **Naming conflicts:** Use `docs/data-contracts.md` as the canonical naming source. Do not allow agents to rename fields.

---

## 6. Branch and PR Rules for Agent-Assisted Work

- **One feature branch per task.** Do not accumulate multiple features on one branch.
- **Commit frequently** as you work with the agent, so you can roll back easily if a session produces bad output.
- **Write a clear commit message** that describes what the code does, not "AI-generated code".
- **Before opening a PR, update both living docs:**
  1. Add a `CHANGELOG.md` entry under `[Unreleased]` describing every file changed and why.
  2. Update `docs/project-status.md`: move completed items, update in-progress work, log any decisions or blockers.
  3. Commit these updates in the **same commit** as your final code changes.
- **When opening a PR:**
  - Check the "AI-generated code" box in the PR template.
  - Confirm in the PR description which docs were pasted into the agent session.
  - Describe what the agent was asked to do and what you changed after review.
- **Jira updates happen at end of session, in a batch — not during work.** See [docs/jira-workflow.md](jira-workflow.md) for the batching pattern and transition IDs.

---

## 7. Session Start Checklist (copy this into your notes)

```
Before every agent session:
[ ] Pulled latest dev
[ ] Created a feature branch
[ ] Read docs/project-status.md — know what's built and what's in progress
[ ] Told the agent its module and scope
[ ] Have a single, focused task ready

Before opening a PR:
[ ] Added CHANGELOG.md entry under [Unreleased]
[ ] Updated docs/project-status.md
[ ] Both files committed with code changes
```

---

## 8. Recognising Agent Drift — Warning Signs

Drift rarely announces itself. It usually looks like reasonable-seeming code that quietly violates a constraint you didn't notice until review. Know what to look for.

### Field and naming drift

- A field name that differs from `docs/data-contracts.md` — even by one character or casing (`vatamount` vs `vatAmount`)
- A new field in an output object that isn't in the data contract
- A type mismatch — e.g. `vatRate` returned as a percentage integer (`20`) instead of a decimal (`0.20`)

**What to do:** Reject the output. Repaste the exact field definition from `docs/data-contracts.md` and re-prompt.

### Scope drift

- Files created or modified outside `/src/[your-module]` or `/tests/[your-module]`
- An import from another module the agent added "for convenience"
- A change to `/src/shared` you didn't ask for
- Any modification to a file in `docs/` — agents must never touch docs

**What to do:** Discard the out-of-scope output entirely. Do not commit it. Re-prompt with an explicit scope reminder.

### Logic drift

- A VAT rate, exemption, or rule not in `docs/vat-rules.md`
- A conditional branch handling a country or scenario not in scope
- The agent adding a "sensible default" (e.g. a fallback VAT rate) you didn't ask for

**What to do:** Compare every VAT-related value against `docs/vat-rules.md`. If it isn't documented there, it must not be in the code.

### Feature drift

- Helper functions, utilities, or abstractions you didn't request
- Additional validation, error cases, or edge case handling beyond what you described
- Refactored or renamed existing functions the agent decided were "cleaner"
- TODO stubs or comments for features "the agent thought you'd want next"
- The agent saying "I also added…" or "while I was at it…"

**What to do:** Delete the unrequested additions before committing. Accepting unrequested additions once teaches the agent that expanding scope is acceptable.

### Dependency drift

- A new `import` or `require` for a package you didn't ask for
- A new entry in `package.json`, `requirements.txt`, or equivalent

**What to do:** Remove it. If the dependency is genuinely needed, raise it with the team first.

### Signs the agent is guessing (not following the docs)

- The agent uses confident language but the value it produced isn't in any of your docs
- Slightly different field names appear across turns in the same session
- The agent answers a question about an existing function without having seen the code

**What to do:** Test it. Ask the agent directly: "What is the exact type of `vatRate` as defined in the data contracts I pasted?" If it can't repeat it back accurately, repaste the doc and re-prompt from scratch.

---

## 9. What Agents Must Never Do

Regardless of how the prompt is written, never accept or commit agent output that:

- Creates or modifies files in `/src/shared` without team approval
- Renames or restructures fields defined in `docs/data-contracts.md`
- Implements VAT rules not documented in `docs/vat-rules.md`
- Adds external dependencies (npm packages, libraries) without team discussion
- Modifies `docs/architecture.md`, `docs/vat-rules.md`, or `docs/data-contracts.md` directly — these are human-maintained sources of truth and require team discussion before changing
- Updates `docs/project-status.md` or `CHANGELOG.md` autonomously — the human writes these, not the agent
- Pushes to `main` directly
- Suggests force-pushing or rewriting git history

---

## 10. Reviewer Gate Completion Rule

Use this rule to close tickets consistently:

1. Run a `reviewer-agent` check with explicit verdict output: `PASS` or `FAIL`.
2. If verdict is `PASS`, queue the ticket for Jira transition to `Done` in `jira-plan.local.json`.
3. Add a completion comment that includes review pass evidence.
4. Apply updates in one batch using:
   `py C:\Users\gusv\.codex\skills\project-leader-agent\scripts\jira_batch_update.py --plan-file .\jira-plan.local.json`

If verdict is `FAIL`, do not move the ticket to `Done`. Keep it in `In Progress` or `In Review` and create follow-up tasks for findings.

---

## 11. Agent Guardrails — Self-Enforcement Before Every Response

These are active constraints every agent must apply to its own output **before** completing a response. They are not a review checklist for humans — they are rules the agent enforces on itself.

---

### Guardrail 1 — Field Names Are Immutable

Before outputting any field name, verify it character-for-character against `docs/data-contracts.md`.

- `vatAmount` is correct. `vatamount`, `VatAmount`, `vat_amount` are all wrong.
- `vatRate` must be a decimal (`0.20`), never a percentage integer (`20`).
- If you are about to use a field name that is not in `data-contracts.md`, **stop**. Do not invent it. Flag it to the human and ask for clarification.

**Self-check:** "Is every field name I have used present in `data-contracts.md`, exactly as written?"

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

**Self-check:** "Have I generated or modified any file outside my assigned paths?"

---

### Guardrail 3 — VAT Logic Must Be Documented

You may only implement a VAT rule, rate, exemption, or behaviour that is explicitly present in `docs/vat-rules.md`.

- Do not add a fallback rate "in case the lookup fails".
- Do not handle a country or scenario not listed in the jurisdiction table.
- Do not infer a rule from a comment, a test name, or context — only from the doc.

If `vat-rules.md` does not cover the scenario you need, **stop**. Flag the gap to the human. Do not fill it with a reasonable-sounding assumption.

**Self-check:** "Is every VAT value, rate, and conditional branch I have written traceable to a specific entry in `vat-rules.md`?"

---

### Guardrail 4 — Implement Only What Was Asked

Your output must be limited to what was explicitly requested in the task.

- Do not add helper functions, utilities, or abstractions that weren't asked for.
- Do not refactor or rename existing code while implementing something new.
- Do not add validation, error handling, or edge cases beyond the stated scope.
- Do not leave TODO stubs or comments for things "you think might be needed next".

If you find yourself writing something and thinking "this might be useful later" — delete it.

**Self-check:** "Does every line I have written directly serve the task I was given?"

---

### Guardrail 5 — No New Dependencies

Do not introduce any new package, library, or import that was not already present in the codebase.

- Do not add entries to `package.json`, `requirements.txt`, or any equivalent file.
- Do not import a module you have not been told is available.
- If you need a dependency that isn't there, **stop**. Raise it with the team before writing code that depends on it.

**Self-check:** "Have I introduced any import or dependency that did not exist before this task?"

---

### Guardrail 6 — Uncertainty Requires a Stop, Not a Guess

If you are unsure about anything — a field name, a VAT rule, which file to edit, what already exists — you must stop and ask. Do not use confident language to paper over uncertainty.

- "I'll assume…" is not acceptable.
- "Typically this would be…" is not acceptable.
- "I'll use a sensible default…" is not acceptable.

State exactly what you are uncertain about and what information you need to proceed.

**Self-check:** "Is there anything in my output I am not certain about? If yes, have I flagged it explicitly rather than guessing?"

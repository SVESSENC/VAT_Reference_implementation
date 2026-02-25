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

2. **Paste the full content of these files into your agent context — in this order:**
   - `docs/project-status.md` — **first, always** — tells the agent what already exists
   - `CHANGELOG.md` (Unreleased section + last 2–3 entries) — recent changes and conventions
   - `docs/architecture.md` — system design
   - `docs/data-contracts.md` — all input/output shapes
   - `docs/vat-rules.md` — if working on engine/calculation logic

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

---

## 7. Session Start Checklist (copy this into your notes)

```
Before every agent session:
[ ] Pulled latest dev
[ ] Created a feature branch
[ ] Read docs/project-status.md — know what's built and what's in progress
[ ] Pasted docs/project-status.md into agent context
[ ] Pasted CHANGELOG.md [Unreleased] section into agent context
[ ] Pasted docs/architecture.md into agent context
[ ] Pasted docs/data-contracts.md into agent context
[ ] Pasted docs/vat-rules.md (if touching engine)
[ ] Told the agent its module and scope
[ ] Have a single, focused task ready

Before opening a PR:
[ ] Added CHANGELOG.md entry under [Unreleased]
[ ] Updated docs/project-status.md
[ ] Both files committed with code changes
```

---

## 8. What Agents Must Never Do

Regardless of how the prompt is written, never accept or commit agent output that:

- Creates or modifies files in `/src/shared` without team approval
- Renames or restructures fields defined in `docs/data-contracts.md`
- Implements VAT rules not documented in `docs/vat-rules.md`
- Adds external dependencies (npm packages, libraries) without team discussion
- Modifies `docs/architecture.md`, `docs/vat-rules.md`, or `docs/data-contracts.md` directly — these are human-maintained sources of truth and require team discussion before changing
- Updates `docs/project-status.md` or `CHANGELOG.md` autonomously — the human writes these, not the agent
- Pushes to `main` directly
- Suggests force-pushing or rewriting git history

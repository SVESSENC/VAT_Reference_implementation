# Contributing to VAT Reference Implementation

---

## Branch Strategy

| Branch | Purpose | Rules |
|--------|---------|-------|
| `main` | Production only | No direct commits. Only merged from `dev` via PR with team review. |
| `dev` | Integration branch | All feature PRs target this branch. Must always be in a working state. |
| `feature/<name>` | Working branch | Scoped to your module. Branch off `dev`, merge back to `dev` via PR. |

### Creating a feature branch

```bash
# Make sure dev is up to date
git checkout dev
git pull origin dev

# Create your feature branch
git checkout -b feature/<your-feature-name>

# Work on your changes, then push
git push -u origin feature/<your-feature-name>
```

### Merging back via PR

1. Push your branch to the remote.
2. Open a PR targeting `dev` (never `main`).
3. Fill in the [PR template](.github/PULL_REQUEST_TEMPLATE/pull_request_template.md).
4. Request review from at least one team member.
5. Merge only after all checklist items are satisfied.

---

## Module Ownership

Each module has a designated owner. Changes outside your module require explicit approval from the relevant owner.

| Module | Path | Owner | Notes |
|--------|------|-------|-------|
| engine | `/src/engine` | TBD | VAT calculation logic |
| api | `/src/api` | TBD | REST API layer |
| frontend | `/src/frontend` | TBD | UI layer |
| shared | `/src/shared` | TBD | **Team sign-off required for any changes** |

> **Shared module rule:** No changes to `/src/shared` without discussion and approval from all team members. This includes types, constants, and utilities used across modules.

---

## AI Agent Rules

> See [docs/agent-rules.md](docs/agent-rules.md) for the full AI workflow guide. This section is a summary.

When using Claude, ChatGPT, or any AI assistant to generate code, follow these rules:

1. **Scope your prompt to your module only.** Do not ask an agent to generate or modify code in modules you do not own.

2. **Always paste `docs/data-contracts.md` into the agent session** before generating any engine or API code. The agent must understand the agreed data shapes before writing anything.

3. **Always paste `docs/vat-rules.md` into the agent session** when working on calculation logic. VAT rules are the source of truth — the agent must follow them exactly.

4. **Never commit AI-generated code without reviewing it.** Read every line. Verify it matches the data contracts, VAT rules, and existing patterns in the codebase.

5. **Shared types require team discussion before any agent touches them.** Do not prompt an agent to modify `/src/shared` without prior team approval.

6. **Paste `docs/architecture.md` into every agent session** so the agent understands the overall system before generating code.

---

## PR Checklist

Before marking a PR as ready for review, confirm all of the following:

- [ ] Code is scoped to my module only — no unintended changes to other modules
- [ ] All AI-generated code has been read and reviewed line by line
- [ ] All tests pass locally
- [ ] Documentation has been updated if behaviour has changed
- [ ] No changes to `/src/shared` without prior team approval
- [ ] PR targets `dev`, not `main`
- [ ] PR template is fully filled in

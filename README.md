# VAT Reference Implementation

A VAT calculation application built by a 3-person team using AI-assisted development.

> **Before contributing:** Read [CONTRIBUTING.md](CONTRIBUTING.md) and ensure [docs/architecture.md](docs/architecture.md) and [docs/data-contracts.md](docs/data-contracts.md) are pasted into your agent session.

---

## Folder Structure

| Path | Description | Owner |
|------|-------------|-------|
| `/src/engine` | Core VAT calculation logic | TBD |
| `/src/api` | REST API layer | TBD |
| `/src/frontend` | UI layer | TBD |
| `/src/shared` | Shared types, constants, utilities | TBD (team sign-off required) |
| `/tests/engine` | Unit tests for VAT engine | TBD |
| `/tests/api` | API integration tests | TBD |
| `/docs` | Architecture, VAT rules, data contracts | All |
| `/.github/PULL_REQUEST_TEMPLATE` | PR template | All |

---

## Getting Started

1. **Clone the repository**
   ```bash
   git clone <repo-url>
   cd VAT-Reference-Implementation
   ```

2. **Switch to the dev branch**
   ```bash
   git checkout dev
   ```

3. **Install dependencies** _(once tech stack is confirmed)_
   ```bash
   # TBD — see docs/architecture.md
   ```

4. **Read the docs before writing any code**
   - [docs/architecture.md](docs/architecture.md) — system design and tech decisions
   - [docs/vat-rules.md](docs/vat-rules.md) — VAT logic source of truth
   - [docs/data-contracts.md](docs/data-contracts.md) — all data shapes

5. **Create a feature branch off `dev`**
   ```bash
   git checkout dev
   git pull origin dev
   git checkout -b feature/<your-feature-name>
   ```

6. **Open a PR targeting `dev`** when your work is ready.

---

## Tech Stack

> TBD — to be filled in before coding begins. See [docs/architecture.md](docs/architecture.md).

---

## Branch Strategy

| Branch | Purpose |
|--------|---------|
| `main` | Production only. No direct commits. |
| `dev` | Integration branch. All PRs merge here. |
| `feature/<name>` | Working branch scoped to your module. |

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for branch strategy, module ownership, AI agent rules, and PR checklist.

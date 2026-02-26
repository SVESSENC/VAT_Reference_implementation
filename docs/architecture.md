# Architecture

> Starter architecture baseline so agent execution is not blocked.

---

## Tech Stack

| Layer | Technology | Notes |
|-------|-----------|-------|
| Engine | Python 3.12 | Core VAT rules and calculations |
| API | FastAPI | REST wrapper around engine |
| Frontend | Static HTML/CSS/JS | Simple UI mockups for tests |
| Testing | Pytest | Unit tests for engine and API |
| Build/Tooling | GitHub Actions | CI checks on pull requests |

---

## High-Level Architecture

```
[ Frontend ] -> [ API ] -> [ Engine ]
                              v
                        [ Shared Types ]
```

Data flow:
1. Frontend sends request payload.
2. API validates input and calls engine.
3. Engine computes VAT response.
4. API returns result and frontend renders output.

---

## Key Components

### Engine (`/src/engine`)
- Owns VAT logic.
- No UI or HTTP concerns.

### API (`/src/api`)
- Owns request/response handling.
- Delegates VAT math to engine.

### Frontend (`/src/frontend`)
- Owns presentation and user interaction.
- For mockups, static files are acceptable.

### Shared (`/src/shared`)
- Cross-module constants/types.
- Team sign-off required before changes.

---

## External Dependencies

| Dependency | Purpose | Notes |
|-----------|---------|-------|
| Jira Cloud API | Ticket automation | Used by scripts in `skills/project-leader-agent/scripts` |
| OpenAI Codex CLI | Optional autonomous execution | Invoked by `start_dev_cycle.bat` |
| GitHub | Source control and PRs | `dev` is integration branch |

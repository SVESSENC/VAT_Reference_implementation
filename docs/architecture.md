# Architecture

> **ACTION REQUIRED:** This document must be filled in before any coding begins.
> Paste this entire document into every agent session so the AI understands the system before generating code.

---

## Tech Stack

> TBD — agree as a team and document here before writing any code.

| Layer | Technology | Notes |
|-------|-----------|-------|
| Engine | TBD | |
| API | TBD | |
| Frontend | TBD | |
| Testing | TBD | |
| Build/Tooling | TBD | |

---

## High-Level Architecture

> TBD — add a diagram or description of how the components interact.

```
[ Frontend ] → [ API ] → [ Engine ]
                              ↓
                        [ Shared Types ]
```

_Replace with actual architecture once agreed._

---

## Key Components

### Engine (`/src/engine`)
> TBD — describe the core VAT calculation logic and its responsibilities.

### API (`/src/api`)
> TBD — describe the REST API layer, endpoints, and how it delegates to the engine.

### Frontend (`/src/frontend`)
> TBD — describe the UI layer and how it communicates with the API.

### Shared (`/src/shared`)
> TBD — describe shared types, constants, and utilities. Changefs here require team sign-off.

---

## External Dependencies

> TBD — list any third-party services, libraries, or APIs the system depends on.

| Dependency | Purpose | Notes |
|-----------|---------|-------|
| TBD | | |

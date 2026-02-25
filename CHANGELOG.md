# Changelog

> **Every agent session that produces committed code must add an entry here before opening a PR.**
> This file is the shared memory of the team. Paste it into your agent context at the start of every session.
>
> Format rules:
> - Add new entries at the **top**, under `[Unreleased]`
> - One entry per PR / logical unit of work
> - Be specific about what changed and in which files — vague entries are useless to other agents
> - After a release to `main`, move `[Unreleased]` entries under a versioned heading

---

## [Unreleased]

_No changes yet. First entry goes here._

---

## Entry Format

Use this template for every entry:

```
### [YYYY-MM-DD] <module> — <short description>
**Who:** <team member / role>
**Branch:** feature/<name>
**Files changed:**
- `path/to/file.ts` — what changed and why
- `path/to/other.ts` — what changed and why
**Notes:** Any context another agent needs to know (e.g. "VatCalculator now expects vatNumber to be null not undefined", "added new field discountAmount to VatInput — data-contracts.md updated too")
```

---

## How to use this file in an agent session

Paste the **[Unreleased]** section (plus the last 2-3 entries) into your agent context with this instruction:

> "Here is the recent changelog for this project. Read it before writing any code so you understand what has already been implemented and what conventions have been established."

---

## Archive

_Versioned releases will be logged here once the project reaches a deployable state._

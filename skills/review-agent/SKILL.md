---
name: review-agent
description: Perform rigorous code review focused on correctness, security, regressions, and missing tests. Use when a user asks for a review, PR review, audit, risk check, or bug hunt across changed code, configuration, migrations, infrastructure, or tests.
---

# Review Agent

## Overview

Identify high-impact review findings quickly and report them with precise file/line evidence.
Prioritize defects and behavior risks over style preferences.

## Workflow

1. Determine review scope.
- Inspect requested files, diff, or commit range first.
- If scope is unclear, infer from recent changes and state the assumption.

2. Build behavioral understanding before judging details.
- Trace execution paths introduced or modified by the change.
- Check entry points, state transitions, error handling, and cleanup paths.

3. Find and validate defects.
- Reproduce logic mentally or with targeted commands/tests when possible.
- Prefer concrete issues with clear impact over speculative concerns.
- Verify whether existing tests cover the changed behavior.

4. Report findings in severity order.
- Include file path and line number for each finding.
- Explain impact, trigger condition, and why current code is unsafe or incorrect.
- Suggest a minimal fix direction when obvious.

5. Close with risks and gaps.
- State explicitly if no findings are discovered.
- Note residual risks and missing/untested scenarios.

## What To Prioritize

- Functional correctness and regressions
- Security flaws and data exposure
- Concurrency, race conditions, and transaction safety
- Input validation and boundary conditions
- Migration/backward compatibility risks
- Missing tests for critical paths

## Evidence Standard

- Prefer findings that include direct code evidence.
- Avoid style-only comments unless the user asks for style review.
- Do not inflate with low-confidence speculation.
- Mark uncertain findings as assumptions and list what would confirm them.

## Output Format

- Start with `Findings` and list issues by severity (`Critical`, `High`, `Medium`, `Low`).
- For each finding, use:
  - `Severity:`
  - `Location:` absolute or repo-relative path with line number
  - `Issue:`
  - `Impact:`
  - `Recommendation:`
- Add `Open Questions` only when required to confirm risk.
- Add a short `Summary` after findings.
- If no findings exist, write `No actionable findings.` then list testing gaps.

## Reference

For concise severity definitions and confidence guidance, read `references/severity-guide.md`.

---
name: project-manager-agent
description: Build a whole-project execution plan by mapping architecture, reading key folders, finding cross-cutting inconsistencies, and assigning concrete implementation tasks to specialized agents. Use when a user asks for high-level project management, roadmap decomposition, repo-wide quality alignment, or coordination across multiple subsystems beyond a narrow code review.
---

# Project Manager Agent

Deliver a system-level view of the repository and convert that view into executable, agent-specific workstreams.
Focus on coherence across modules, not isolated defects.

## Workflow

1. Define scope and assumptions.
- Confirm root directories and intended product behavior.
- If scope is ambiguous, infer from repo structure and state assumptions.

2. Build a project map before evaluating quality.
- Enumerate major folders, services, and ownership boundaries.
- Identify architecture layers: interfaces, application logic, data, infrastructure, tests, docs.
- Summarize how data and control flow through those layers.

3. Detect cross-cutting inconsistencies.
- Compare naming, error handling, validation, auth/authz, logging, configuration patterns, and test conventions across modules.
- Flag divergence between docs, implementation, and deployment/runtime configuration.
- Spot dead zones: unowned modules, missing tests, stale scripts, duplicated logic.

4. Prioritize by impact and sequencing.
- Rank issues by user impact, security risk, blast radius, and dependency ordering.
- Group related issues into workstreams that can be executed independently.
- Mark blockers and prerequisites explicitly.

5. Produce specialized-agent action plans.
- Assign each workstream to a role-oriented agent (for example: API agent, data agent, frontend agent, infra agent, test agent).
- Provide concrete files/components to touch and exact acceptance criteria.
- Include validation commands and regression checks.

## Required Output

Use this structure:

1. `System Map`
- Repo domains and key folder responsibilities.
- Primary dependency/data flows.

2. `Inconsistencies`
- Each item includes: `Severity`, `Scope`, `Evidence`, `Risk`.
- Prefer file-path evidence over general claims.

3. `Execution Plan`
- Ordered phases with dependencies.
- State what must happen first and what can run in parallel.

4. `Agent Workstreams`
- For each workstream include:
  - `Owner Agent`
  - `Objective`
  - `Files/Areas`
  - `Steps`
  - `Validation`
  - `Definition of Done`

5. `Residual Risks`
- List what remains uncertain and how to de-risk it.

## Constraints

- Do not stop at review findings; always provide an implementation plan.
- Do not provide style-only feedback unless it affects correctness or maintainability.
- Keep recommendations specific enough for another agent to execute without reinterpretation.
- Identify parallelizable work to accelerate delivery.

## Reference

For the consistency checklist and prioritization rubric, read `references/consistency-rubric.md`.

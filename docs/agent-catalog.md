# Agent Catalog

## Core Coordination

- `project-leader-agent`: Owns roadmap, milestone planning, task assignment, dependency management, and Jira execution gating.
- `project-manager-agent`: Maps the full repository, detects cross-cutting inconsistencies, and outputs prioritized workstreams.

## Delivery Agents

- `developer-agent`: Implements scoped backend/frontend changes with tests and production-safe handoff notes.
- `architect-agent`: Defines architecture decisions, component boundaries, integration strategy, and long-term technical direction.
- `db-agent`: Handles schema design, migrations, indexing, performance tuning, and database operational reliability.
- `designer-agent`: Produces UX flows, interaction behavior, and implementation-ready design guidance.

## Quality and Review

- `reviewer-agent`: Provides PASS/FAIL quality gate with explicit findings and closure recommendation.
- `code-review-agent`: Performs deep code review focused on correctness, regressions, maintainability, and missing tests.
- `validation-security-agent`: Validates runtime safety and security requirements (input validation, auth/authz, secrets handling, dependency risk, and abuse paths).

## Domain Specialist

- `vat-research-agent`: Validates Danish/EU VAT treatment with source-backed compliance reasoning.

## Recommended Additional Agents

- `qa-test-agent`: Owns test strategy and regression coverage across unit, integration, and edge-case scenarios.
- `security-agent`: Performs threat modeling and security validation (auth, input validation, secret handling, dependency risk).
- `devops-agent`: Owns CI/CD, environments, deployment safety, rollback plans, and observability setup.
- `integration-agent`: Coordinates cross-module contract compatibility and end-to-end wiring between services/components.
- `release-manager-agent`: Runs release planning, go/no-go checks, change freeze policy, and cutover/rollback coordination.
- `docs-governance-agent`: Keeps architecture/contracts/rules docs synchronized with implementation and flags drift.
- `backlog-triage-agent`: Refines raw tickets into implementation-ready tasks with dependencies and acceptance criteria.
- `incident-agent`: Handles incident workflow: triage, containment, root-cause analysis, and follow-up actions.

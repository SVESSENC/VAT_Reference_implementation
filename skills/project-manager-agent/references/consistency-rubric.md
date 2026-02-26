# Consistency Rubric

Use this rubric to compare modules and identify system-level mismatches.

## Architecture Consistency

- Folder responsibilities are explicit and non-overlapping.
- Dependency direction is consistent (for example: handlers -> services -> repositories).
- Shared concerns are centralized instead of duplicated.

## Runtime and Configuration Consistency

- Environment variable names and defaults follow one convention.
- Feature flags and config loading behavior match across services.
- Deployment/runtime docs match actual startup behavior.

## Data and Contract Consistency

- API contracts align with DTOs, validation schemas, and persistence models.
- Error shapes and status-code conventions are uniform.
- Backward compatibility is preserved for existing consumers.

## Reliability and Safety Consistency

- Error handling and retries are deliberate and documented.
- Auth/authz checks are consistently applied at boundaries.
- Logging/metrics are present on critical flows.

## Testing Consistency

- Critical paths have unit/integration coverage.
- Test naming and fixture patterns are coherent.
- Contract changes include regression tests.

## Prioritization Rubric

Score each inconsistency 1-5 on:

- User impact
- Security/compliance risk
- Blast radius
- Urgency
- Dependency blocking power

Prioritize by total score, then schedule by dependency order.

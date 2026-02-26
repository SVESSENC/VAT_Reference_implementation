# Schema Design Checklist

Use this checklist before creating or approving a schema.

## 1. Workload Baseline

- Confirm read/write ratio and peak traffic profile.
- Estimate 12-24 month data growth and retention windows.
- Confirm latency SLOs for critical reads/writes.
- Identify hot entities and highest-frequency query paths.

## 2. Logical Model

- Define entities, aggregate boundaries, and cardinality.
- Model business invariants as explicit constraints.
- Normalize to 3NF unless measured workload justifies denormalization.
- Define lifecycle states and soft-delete vs hard-delete behavior.

## 3. Keys and Constraints

- Choose stable primary keys with clear generation strategy.
- Enforce foreign keys where ownership/reference integrity matters.
- Add unique constraints for business-level uniqueness.
- Make nullability explicit; avoid nullable columns without semantic meaning.

## 4. Data Types and Row Layout

- Use narrow, correct types (avoid over-wide text/numeric defaults).
- Store timestamps with timezone semantics defined.
- Keep hot rows compact; split cold or large attributes into side tables.
- Reserve JSON/document columns for truly flexible data, not core relational joins.

## 5. Access Patterns and Index Inputs

- List top queries by frequency and latency sensitivity.
- Validate predicate selectivity expectations (high vs low cardinality fields).
- Ensure every critical query has a planned access path.
- Avoid speculative indexes that have no measured query consumer.

## 6. Lifecycle and Partitioning

- Define archival and deletion policy before table growth becomes unbounded.
- Partition by lifecycle/time boundaries when pruneable ranges dominate queries.
- Keep partition key aligned to primary filter paths.
- Confirm partition management automation (create/drop/merge) is defined.

## 7. Multi-Tenant and Security

- Define tenant key strategy and isolation requirements.
- Ensure indexes include tenant filters where needed for locality/isolation.
- Encrypt sensitive data at rest and in transit per policy.
- Plan auditability for privileged changes and sensitive reads.

## 8. Design Review Exit Criteria

- Integrity rules are enforced by schema, not only application code.
- Every critical query has known cost profile and expected plan shape.
- Migration and rollback path exists for initial deployment.
- Monitoring hooks are defined for growth, lock contention, and error rates.

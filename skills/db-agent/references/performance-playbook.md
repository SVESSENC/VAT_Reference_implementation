# Performance Playbook

Use this playbook to optimize query performance without harming correctness or write stability.

## 1. Measure First

- Capture baseline p50/p95/p99 latency and throughput.
- Identify top slow queries by total time and frequency.
- Collect execution plans and key wait/saturation metrics.
- Do not tune based only on intuition.

## 2. Query Shape Review

- Remove `SELECT *` on wide/high-traffic tables.
- Ensure predicates are sargable (avoid wrapping indexed columns in functions).
- Verify joins are on typed, indexed, and selective keys.
- Eliminate N+1 access patterns in application code.

## 3. Index Strategy

- Create indexes for real high-impact queries only.
- Prefer composite indexes that match filter and order patterns.
- Put highest-selectivity or equality predicates first where engine guidance supports it.
- Evaluate covering indexes for read-heavy critical paths.
- Track write amplification and storage overhead per added index.

## 4. Execution Plan Triage

- Look for full scans on large tables, repeated nested loops, and excessive sorts.
- Re-check row estimate accuracy; stale stats can mislead planners.
- Confirm predicate pushdown and partition pruning are active where expected.
- Re-test after each change; avoid multi-change ambiguity.

## 5. Data Volume Controls

- Partition large append-heavy tables by lifecycle-friendly keys.
- Archive cold data to keep active working set compact.
- Address table/index bloat with engine-appropriate maintenance.
- Revisit fill factor/page settings only when measurements justify it.

## 6. Safe Optimization Sequence

1. Baseline metrics and plan capture.
2. Apply one targeted change.
3. Re-run representative workload.
4. Compare latency, throughput, CPU/IO, lock impact, and error rates.
5. Keep change only if net benefit is clear.

## 7. Engine Notes

- PostgreSQL: check `EXPLAIN (ANALYZE, BUFFERS)`, autovacuum health, and bloat.
- MySQL/InnoDB: inspect `EXPLAIN`, buffer pool hit rate, and lock wait trends.
- SQL Server: inspect actual execution plans, missing/unused indexes, and wait stats.

Use engine/version-specific commands when producing final recommendations.

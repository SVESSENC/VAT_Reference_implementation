# Operations Playbook

Use this playbook for safe schema delivery, resilience, and sustained database health.

## 1. Migration Safety Standard

Follow expand/migrate/contract:

1. Expand:
- Add nullable/new columns, new tables, or additive indexes first.
- Ship backward-compatible application code.

2. Migrate:
- Backfill in controlled batches with throttling and checkpoints.
- Verify data parity and performance during backfill.

3. Contract:
- Remove deprecated columns/indexes only after consumers are removed and validated.

For every migration:
- Define a rollback path.
- State lock risk and expected runtime.
- Schedule high-risk changes during low-traffic windows.

## 2. Backup and Restore

- Define explicit RPO and RTO targets by system criticality.
- Use automated backups with retention and integrity checks.
- Test restore procedures regularly; proof is a successful restore drill.
- Keep runbooks for point-in-time recovery and full disaster recovery.

## 3. Replication and High Availability

- Define primary/replica topology and failover strategy.
- Monitor replication lag and failover health continuously.
- Test failover and failback procedures under realistic traffic.
- Document write/read routing behavior during degradation.

## 4. Monitoring and Alerting Baseline

Track and alert on:
- Latency and throughput by critical query class.
- CPU, memory, IO saturation, and connection pool pressure.
- Lock waits/deadlocks and transaction retry rates.
- Storage growth, bloat, and backup job success.
- Replication lag and replica freshness.

Alerts should map to actionable runbooks, not just thresholds.

## 5. Incident Response Expectations

- Classify incident impact (correctness, availability, performance, security).
- Stabilize first, then optimize.
- Preserve forensic data (plans, logs, metrics, migration IDs).
- Produce post-incident actions with owner and due date.

## 6. Capacity Management

- Forecast growth using recent trends and product roadmap changes.
- Reassess indexing, partitioning, and hardware tier before saturation.
- Test scaling actions in non-production before rollout.
- Keep cost/performance trade-offs explicit in recommendations.

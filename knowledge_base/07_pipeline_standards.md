# Meridian Pipeline Engineering Standards

These standards apply to every data pipeline built at Meridian. Code review enforces them.

## Idempotency

Every pipeline must be idempotent: running it twice with the same input must produce the same
result, with no duplicates and no side effects from the second run. Writes use partition-overwrite
or merge/upsert patterns keyed on a stable business key, never blind appends that would double
data on a rerun. This is the single most important standard, because reruns are routine —
after an incident, a backfill, or a late-arriving file.

## Schema and contracts

Every source has a declared schema contract. Incoming data is validated against its contract at
the bronze boundary; records that violate the contract are quarantined to a `rejects` dataset
rather than silently dropped or allowed to corrupt downstream tables. Schema changes to a shared
model require a migration plan and a heads-up in `#data-help`.

## Data quality checks

Each transform must include data-quality checks that run as part of the pipeline, not as an
afterthought. At minimum every gold model checks: row count within an expected range, no
unexpected nulls in key columns, uniqueness of the primary key, and referential integrity to
its dimensions. A failed quality check blocks the model from being published to serving and
raises an alert.

## Partitioning and performance

Large tables are partitioned by date and clustered by customer ID. Pipelines process data
incrementally — only the new or changed partitions — rather than reprocessing full history on
every run. Full reprocessing is reserved for explicit backfills and must be reviewed, because it
is the most common cause of warehouse cost spikes.

## Orchestration standards

DAGs follow the `domain__customer__purpose` naming convention, declare explicit dependencies
(no implicit ordering), set sensible retries with exponential backoff, and define an SLA so that
a late run raises an alert. No DAG may depend on another DAG's internal task; cross-DAG
dependencies use datasets or explicit sensors.

## Observability

Every pipeline emits, at minimum: rows in, rows out, rows rejected, run duration, and a
freshness timestamp. These feed the platform's data-observability dashboards. A pipeline that
runs successfully but produces stale or empty output is considered failing, and the freshness
metric is what catches it.

## Cost awareness

Engineers are responsible for the cost of their pipelines. Before merging, check the estimated
bytes scanned for new BigQuery queries and prefer partition-pruned, clustered queries. The
platform team publishes a per-squad cost dashboard, and squads review their costs monthly.

## Documentation

Every pipeline has a short README covering: what it does, its sources and outputs, its schedule,
its owner, and how to safely rerun it. A pipeline without a rerun procedure is not considered
production-ready.

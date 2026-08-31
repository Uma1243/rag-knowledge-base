# Meridian Data Platform Architecture

This document describes the technical architecture of the Meridian Pulse data platform. It is
the reference for how data flows from customer sources to dashboards.

## High-level data flow

Data moves through five stages: **ingest → land → transform → serve → observe.**

1. **Ingest.** Customer data enters through connectors. Streaming sources publish to Google
   Cloud Pub/Sub topics; batch sources are pulled on a schedule by Airflow into Cloud Storage.
2. **Land.** Raw events are written to the **bronze** layer of the data lake in Cloud Storage,
   partitioned by `source/date/hour`, in Parquet format. Nothing is transformed at this stage;
   bronze is an immutable, append-only record of exactly what arrived.
3. **Transform.** Dataflow (for streaming) and Dataproc Spark jobs (for heavy batch) clean and
   model the data into the **silver** layer (deduplicated, typed, conformed) and then the
   **gold** layer (business-level aggregates and dimensional models).
4. **Serve.** Gold tables are loaded into BigQuery, which powers the semantic layer and the
   customer dashboards. Frequently accessed aggregates are additionally cached in a Redis layer.
5. **Observe.** Every stage emits metrics and logs to Cloud Monitoring; data-quality checks run
   as part of each transform.

This bronze/silver/gold pattern is called the **medallion architecture**, and all Meridian
pipelines are expected to follow it.

## The streaming backbone

Streaming ingestion is built on Pub/Sub and Dataflow. Each customer gets a dedicated set of
Pub/Sub topics namespaced by customer ID. A single Dataflow streaming job per customer reads
from those topics, applies windowing and deduplication, and writes to the bronze layer with a
target end-to-end latency of under 30 seconds for Pulse Enterprise customers.

Deduplication uses a 10-minute window keyed on the event's `event_id`. Late-arriving events
beyond the window are routed to a `late_events` side output and reprocessed in the nightly
batch reconciliation job rather than being dropped.

## Orchestration

Batch workflows are orchestrated with Apache Airflow running on Cloud Composer. Meridian runs
roughly 900 Airflow DAGs in production. DAGs are grouped by domain (ingestion, modeling,
reconciliation, exports) and follow a strict naming convention: `domain__customer__purpose`.

The platform team maintains a set of reusable Airflow operators and a shared DAG factory so
squads don't hand-write boilerplate. Any new DAG must pass the DAG-lint check in CI before merge.

## The warehouse and semantic layer

The serving warehouse is BigQuery. Gold-layer models are materialized as BigQuery tables and
partitioned by date, clustered by customer ID. The semantic layer is defined in dbt: every
metric a dashboard can show is defined once as a dbt metric, so numbers are consistent across
dashboards. There are about 1,400 dbt models in the repository.

## Storage tiers and retention

Bronze data is kept in Cloud Storage Standard for 30 days, then transitioned to Nearline for
90 days, then Coldline for long-term archival. Silver and gold tables in BigQuery follow the
retention rules described in the Data Retention Policy document.

# Meridian Data Co. — Company Overview

## About Meridian

Meridian Data Co. is a fictional B2B analytics company founded in 2019, headquartered in
Hyderabad with a second engineering hub in Bengaluru. Meridian builds a real-time customer
data platform (CDP) that helps mid-market retailers unify their sales, inventory, and
marketing data into a single warehouse and act on it through dashboards and automated
workflows.

As of 2026 Meridian serves roughly 340 customers, processes about 4.2 billion events per day,
and employs 210 people, of whom around 95 are in engineering and data roles.

## Mission and product

Meridian's mission is "to make every retailer's data as usable as a well-run spreadsheet, at
warehouse scale." The core product, **Meridian Pulse**, ingests event streams and batch feeds
from a retailer's point-of-sale systems, e-commerce platform, and marketing tools, lands them
in a governed data lake, transforms them into analytics-ready models, and exposes them through
a semantic layer and prebuilt dashboards.

The three product tiers are:

- **Pulse Starter** — batch ingestion only, daily refresh, up to 5 data sources.
- **Pulse Growth** — near-real-time ingestion (5-minute latency), up to 20 sources, custom models.
- **Pulse Enterprise** — streaming ingestion (sub-30-second latency), unlimited sources,
  dedicated infrastructure, and a 99.9% uptime SLA.

## Engineering organization

Engineering is split into four groups:

- **Ingestion** — owns connectors, the streaming backbone, and change-data-capture pipelines.
- **Platform** — owns the data lake, the warehouse, orchestration, and internal tooling.
- **Product Engineering** — owns dashboards, the semantic layer, and the customer-facing app.
- **Reliability** — owns observability, on-call, incident response, and cost governance.

Each group runs in squads of five to eight engineers. New engineers are assigned to a squad
during onboarding and paired with a buddy for their first month.

## Where Meridian runs

Meridian's platform runs primarily on Google Cloud Platform, with a smaller disaster-recovery
footprint on AWS. The primary region is asia-south1 (Mumbai), with asia-south2 (Delhi) as the
warm standby. All customer data stays within India for compliance reasons unless a customer
explicitly opts into a different data residency region.

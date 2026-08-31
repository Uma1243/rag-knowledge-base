# Meridian Data Retention and Privacy Policy

This policy defines how long Meridian keeps different categories of data and how customer data
is protected. It applies to all pipelines and all engineers.

## Retention periods by layer

- **Bronze (raw events):** retained for 13 months total — 30 days in Cloud Storage Standard,
  90 days in Nearline, then Coldline until the 13-month mark, after which it is permanently
  deleted by an automated lifecycle rule.
- **Silver (cleaned data):** retained for 25 months in BigQuery, then deleted.
- **Gold (aggregates and models):** retained for 37 months in BigQuery. Gold aggregates that
  feed regulatory or financial reporting are retained for 7 years in a separate archive dataset.
- **Application and audit logs:** retained for 400 days.

When a retention period elapses, deletion is automatic and irreversible. Engineers must never
disable a retention lifecycle rule without written approval from the Data Governance lead.

## Personally identifiable information (PII)

Meridian classifies data into three sensitivity levels: **public**, **internal**, and
**restricted**. All PII — names, email addresses, phone numbers, physical addresses, and
payment identifiers — is classified as restricted.

Restricted fields must be tokenized at ingestion. The raw PII is stored only in a separate,
access-controlled vault dataset; pipelines downstream of ingestion see only the token, never
the raw value. Re-identification (mapping a token back to raw PII) requires a formal request
and is logged and reviewed monthly.

## Customer data deletion requests

When a customer's end user exercises their right to be forgotten, the request enters the
`erasure` queue. Meridian is contractually obligated to complete erasure within **30 days**.
The erasure job removes the user's records from silver and gold, purges the raw PII from the
vault, and writes a tombstone record proving deletion occurred. Bronze data is not individually
edited; instead the user's tokens are added to a suppression list so they are excluded from any
future reprocessing, and the underlying bronze partitions age out under the normal 13-month rule.

## Data residency

By default all customer data is stored and processed within India (asia-south1 and asia-south2).
Customers on Pulse Enterprise may opt into an alternate residency region; this must be configured
at onboarding and cannot be changed afterward without a full data migration.

## Encryption

All data is encrypted at rest using Google-managed keys by default. Pulse Enterprise customers
may supply their own keys via customer-managed encryption keys (CMEK). All data in transit uses
TLS 1.2 or higher.

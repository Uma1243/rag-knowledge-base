# Meridian Incident Response Runbook

This runbook governs how Meridian responds to production incidents. On-call engineers must be
familiar with it.

## Severity levels

Incidents are graded from SEV1 (most severe) to SEV4:

- **SEV1** — customer-facing outage or data loss affecting multiple customers, or any breach of
  restricted data. Example: the streaming backbone is down and no events are being ingested.
- **SEV2** — significant degradation affecting one customer or a major feature, with no data
  loss. Example: one customer's dashboards are 6 hours stale.
- **SEV3** — minor degradation with a workaround available. Example: a non-critical export DAG
  is failing but data is still correct in the warehouse.
- **SEV4** — cosmetic or low-impact issue with no customer effect.

## Response time targets

- SEV1: acknowledge within 5 minutes, mitigate within 1 hour, resolve within 4 hours.
- SEV2: acknowledge within 15 minutes, mitigate within 4 hours.
- SEV3: acknowledge within 1 business day.
- SEV4: handled in the normal backlog.

## The on-call rotation

Reliability runs a primary and secondary on-call rotation, one week each, handed over every
Monday at 10:00 IST. The primary responds first; the secondary is escalated to if the primary
does not acknowledge within the target time. A dedicated incident commander is paged for all
SEV1s and takes over coordination so the responding engineer can focus on the fix.

## SEV1 procedure

1. Acknowledge the page and post in the `#incidents` channel to declare the incident.
2. The incident commander opens an incident doc from the template and assigns roles:
   commander, communications lead, and operations (the hands-on fixer).
3. Communications lead updates the status page within 15 minutes and every 30 minutes thereafter.
4. Operations focuses only on mitigation — restoring service — not root cause.
5. Once mitigated, the incident is downgraded and a blameless postmortem is scheduled within
   3 business days.

## Common mitigations

- **Streaming backlog:** if Dataflow lag exceeds 10 minutes, scale the streaming job's workers
  and check for a poison message in the dead-letter topic.
- **Warehouse cost spike:** if BigQuery spend alerts fire, identify the offending query via the
  cost dashboard and apply a temporary bytes-scanned quota to the responsible service account.
- **Failed reconciliation:** if the nightly reconciliation DAG fails, do not rerun blindly —
  first confirm the late_events side output is not being double-counted.

## Postmortems

Every SEV1 and SEV2 gets a blameless postmortem. The postmortem focuses on systemic causes and
action items, never on individual blame. Action items are tracked to completion by the
Reliability lead and reviewed in the monthly operations review.

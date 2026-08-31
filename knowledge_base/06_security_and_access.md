# Meridian Security and Access Standards

This document defines how access, secrets, and identities are managed at Meridian.

## Identity and access management

Meridian uses Google Cloud IAM with access granted to Google Groups, never to individual users
directly. Every engineer belongs to groups that reflect their squad and role; adding someone to
a squad group grants the standard bundle of permissions for that squad. This keeps access
auditable and makes offboarding a single action.

The principle of least privilege applies everywhere: engineers get the minimum access needed for
their role, and elevated access is time-boxed. Standing production write access is limited to
on-call-eligible engineers; everyone else requests just-in-time elevation through the access
portal when needed, which grants access for a maximum of 8 hours.

## Service accounts

Pipelines authenticate using service accounts, never personal credentials. Each pipeline has its
own dedicated service account scoped to exactly the resources it needs — one pipeline's service
account cannot read another pipeline's data unless explicitly granted. Service account keys are
not downloaded to laptops; workloads use workload identity or attached service accounts instead.

## Secrets management

All secrets — API keys, database passwords, third-party tokens — live in Google Secret Manager.
Secrets are referenced by pipelines at runtime through the pipeline's service account; they are
never hardcoded in source, never committed to Git, and never placed in environment files that
are checked in. A pre-commit hook and a CI secret-scanner block any commit that appears to
contain a credential.

If a secret is ever exposed — committed by accident, pasted in a ticket, shown in a log — it must
be treated as compromised and rotated immediately, even if the exposure seems minor. Report the
exposure in `#security` so it can be tracked.

## Data access tiers

Access to data follows the sensitivity classification from the retention policy:

- **Public/internal data:** available to all engineers in staging and, with training, in production.
- **Restricted data (PII):** available only through the access-controlled vault dataset, only by
  time-boxed, audited request, and never queried directly in analysis.

## Network and endpoints

Production services are not exposed to the public internet except through a small number of
audited API gateways. Internal service-to-service traffic stays on the private VPC. Access to
production infrastructure requires connecting through the company's zero-trust access proxy;
there is no shared VPN and no long-lived bastion host.

## Audits

Access grants, secret access, and PII re-identification are logged centrally. The security team
reviews restricted-data access monthly and reviews all standing production access quarterly,
revoking anything no longer justified.

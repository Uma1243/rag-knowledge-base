# Meridian Engineering Onboarding Guide

Welcome to Meridian. This guide walks new data and platform engineers through their first two
weeks.

## Before day one

Your manager requests your accounts a week before you start. On day one you should already have:
a Google Workspace account, access to the `meridian-eng` GitHub organization, a Slack account,
and a laptop with the standard image.

## Week one

- **Day 1:** meet your squad and your onboarding buddy. Your buddy is your first point of
  contact for any question, no matter how small, for your first month.
- **Day 2–3:** set up your local environment. Clone the `platform` monorepo, install the
  toolchain with the `make bootstrap` command, and get the test suite passing locally.
- **Day 4–5:** complete the "first pipeline" tutorial, in which you build a small end-to-end
  Airflow DAG that ingests a sample dataset into a personal sandbox dataset. Your buddy reviews
  the pull request.

## Accessing data

New engineers get read access to the sandbox and staging environments on day one. Access to
production data is **not** granted automatically. To get production read access you must
complete the data-handling training and have your manager approve the request in the access
portal. Write access to production is granted only to on-call-eligible engineers.

No engineer may query raw PII from the vault dataset. If your work genuinely requires it, raise
a request with Data Governance; access is time-boxed and audited.

## The development workflow

Meridian uses trunk-based development on the `platform` monorepo. The workflow is:

1. Cut a short-lived feature branch from `main`.
2. Make your change; keep pull requests small (under ~400 lines where possible).
3. Open a pull request. CI runs tests, DAG-lint, and the dbt build automatically.
4. Get one review from a squad member (two reviews for changes to shared platform code).
5. Squash-merge to `main`. Deploys to staging are automatic; production deploys happen on a
   twice-daily train that any engineer can ride once their change is verified in staging.

## Who to ask

- Your buddy: anything, first.
- `#platform-help`: tooling, local setup, CI issues.
- `#data-help`: questions about models, the semantic layer, or where a dataset lives.
- `#incidents`: only for declaring or discussing live incidents.

## Your first month goals

By the end of month one you should have shipped at least three small pull requests to
production, completed data-handling training, shadowed one on-call handover, and written one
piece of documentation (even improving this guide counts).

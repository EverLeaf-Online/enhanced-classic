# EverLeaf Staff Operations and Incident Handling

This document consolidates staff-facing operational principles that were previously scattered across deployment, production, security, and audit notes. It is a baseline, not a substitute for a future exhaustive GM-command or moderation handbook.

For production topology and release procedure, use [`../operations/PRODUCTION_AND_RELEASE.md`](../operations/PRODUCTION_AND_RELEASE.md). For current readiness gaps, use [`../EVERLEAF_MASTER_CHECKLIST.md`](../EVERLEAF_MASTER_CHECKLIST.md).

## Operating principles

- Preserve player data before making destructive changes.
- Prefer reversible source/config/database changes with a documented rollback path.
- Keep live emergency actions separate from ordinary gameplay development.
- Do not deploy guessed fixes directly because an automated or AI review labeled something suspicious.
- Record the source SHA, release identity, relevant timestamps, and evidence for material incidents.
- Never paste secrets, credentials, private tokens, or unnecessary player-sensitive data into public GitHub issues/logs.

## Routine production change

Before a normal production deployment:

1. Confirm intended source on canonical `master`.
2. Confirm required build/test/release gates.
3. Check whether a DB migration or client patch is involved.
4. Ensure the pre-deploy backup path is healthy.
5. Deploy through the maintained guarded release workflow.
6. Verify login, every configured channel, public relay ports, and any affected client/website endpoint.
7. Record the deployed release.
8. Roll back if required post-deploy validation fails.

Do not edit `/opt/everleaf/current` as an ad-hoc mutable release directory.

## Incident severity model

Use practical severity rather than waiting for perfect classification:

- **Critical:** active duplication/economy corruption, credential/secret exposure, remote compromise, mass account/data loss, or a release that is actively damaging persistent state.
- **High:** reproducible exploit with meaningful player/economy impact, widespread inability to log in/play, or serious account/authentication bypass.
- **Medium:** contained gameplay bug, single subsystem outage, or abuse path with limited impact.
- **Low:** cosmetic/documentation/non-destructive operational issue.

Escalate when impact is uncertain but persistent state may be at risk.

## Exploit / dupe response

For a suspected active duplication or transaction exploit:

1. Preserve logs and timestamps before cleanup/restart where practical.
2. Record affected account/character/item/currency identifiers without exposing them publicly.
3. Determine whether the exploit is still actively minting or corrupting state.
4. Disable or restrict the smallest affected feature when possible; use broader shutdown only when necessary to protect persistent state.
5. Take a database backup/snapshot before remediation if the system state permits.
6. Reproduce on staging/disposable QA, not using normal player accounts on production.
7. Fix the authoritative server-side state/transaction validation.
8. Add a regression test or deterministic audit when practical.
9. Identify and reconcile illegitimate gains separately from the code fix.
10. Document the incident and the rollback/remediation decision.

Do not publish exploit reproduction details while the vulnerability remains exploitable.

## Release rollback vs data remediation

Application rollback and database/economy remediation are different actions.

- A release rollback switches back to a known-good application release when the new release itself is unhealthy.
- Database/economy remediation corrects persistent state already written by an exploit/bug.
- Rolling back application code does not automatically undo bad database writes.
- Restoring an old database can destroy legitimate player progress and therefore requires explicit evidence, scope analysis, and owner approval.

Prefer targeted transactional remediation over a broad database restore when the affected state can be identified safely.

## Account / moderation evidence

For bans, appeals, account-compromise reports, or suspicious economy activity, preserve:

- timestamps with time zone;
- account/character identifiers needed for investigation;
- relevant command/action/transaction IDs where available;
- server-side logs or database evidence;
- staff actions already taken;
- the reason/evidence supporting a restriction.

Do not rely solely on screenshots from a third party when server-side evidence is available. Avoid collecting more personal data than needed for the investigation.

A definitive GM command/permission reference and full ban/appeal procedure are still separate documentation gaps tracked by the master checklist.

## Player support triage

Support should first classify the issue into account/authentication, launcher/update, client crash, gameplay/content, transaction/economy, moderation, or service outage.

Ask for reproducible facts rather than credentials. Never request a player's password, PIC/PIN, launcher token, or private authentication material.

For client problems, point players to the official launcher/repair path and never recommend globally disabling antivirus.

## Event operations

Do not activate dormant/seasonal event scripts simply because they exist in the repository. Event availability, schedule, reward tables, and instance cleanup behavior must be deliberate and tested. Reward replay/disconnect behavior and cleanup are release-critical for enabled events.

A fuller event-operation checklist remains future staff documentation work.

## Evidence retention

Dated audit captures and superseded live snapshots are stored under `../archive/audits/`. They are useful for provenance and incident reconstruction but do not override current production state.

The master checklist and current production/release guide should be consulted first for normal operations.

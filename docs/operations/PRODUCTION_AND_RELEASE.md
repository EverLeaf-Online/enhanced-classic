# EverLeaf Production and Release Operations

This is the maintained production/release guide for EverLeafMS. Project status and exact current release identity remain authoritative in [`../EVERLEAF_MASTER_CHECKLIST.md`](../EVERLEAF_MASTER_CHECKLIST.md).

## Current production contract

- Canonical repository: `EverLeaf-Online/enhanced-classic`
- Canonical branch: `master`
- Long-lived repository branch model: `master` only; temporary review branches may be used when useful and should be removed after reconciliation.
- MapleStory protocol/client baseline: v83 with EverLeaf-owned native extensions and selectively backported content.
- Level cap: 250.
- Production channels: 20.
- Login port: 8484.
- Channel ports: 7575–7594.
- Player-facing relay: `129.159.114.146`.
- Oracle origin/deployment host: `132.145.141.79`.
- Production source checkout: `/opt/everleaf/server`.
- Active release symlink: `/opt/everleaf/current`.
- Release storage: `/opt/everleaf/releases/`.
- Game service: `everleaf.service`.
- Website checkout: `/opt/everleaf/web-repo`.
- Website runtime symlink: `/opt/everleaf/web -> /opt/everleaf/web-repo/web`.
- Mutable website state: `/opt/everleaf/web-state`.
- Website service: `everleaf-web.service`.
- Canonical production v95 XML baseline: 44,237 files as of the September 10, 2026 synchronized production baseline.

The exact currently deployed SHA and release directory must be read from the master checklist or live release record rather than copied into multiple documents.

## Public gameplay policy baseline

Current project defaults documented by the repository are:

- EXP: 5x
- Mesos: 3x
- Normal drop: 2x
- Boss drop: 2x
- Quest multiplier: 1x with direct quest balancing
- No mandatory HP washing
- No paid power / no donation conversion into gameplay progression currencies

When a value is changed, update configuration and the master checklist before treating a prose document as authoritative.

## Branch and change policy

`master` is the single canonical production/development line. Do not recreate the former split among `release-dev`, client-only long-lived branches, content staging branches, or donor/reference branches.

Use a temporary branch when a change benefits from review, isolated validation, or a large multi-file reorganization. Once the behavior is represented on `master` and any required production validation passes, retire the temporary branch.

Historical branch-consolidation evidence is retained under `../archive/` and must not be used to infer the present branch model.

## Release flow

The maintained production path is release-based rather than editing the active runtime tree in place.

1. Start from canonical `master`.
2. Apply the maintained EverLeaf source/config transform chain.
3. Compile, test, and package the Java 21/Maven server.
4. Stage the canonical full-v95 WZ/XML baseline instead of replacing it with the smaller repository WZ tree.
5. Validate required content invariants and release metadata.
6. Take the required production backup before switching releases.
7. Stage a new immutable release directory under `/opt/everleaf/releases/`.
8. Atomically switch `/opt/everleaf/current`.
9. Restart `everleaf.service`.
10. Validate login, all configured channel listeners, and player-facing relay ports.
11. Record the deployed release identity.
12. If post-switch health validation fails, use the maintained rollback path to restore the previous release.

## Pre-deployment gates

Before a production change:

- Build/test/package must pass for the intended source.
- Production credentials, SSH keys, tokens, and mutable secrets must remain outside source control.
- The game server must not use the MySQL root account.
- MySQL must not be publicly exposed.
- Website registration remains authoritative unless policy is deliberately changed.
- Paid rate coupons and other paid-power paths must remain disabled.
- The build manifest must match the intended commit, protocol, level cap, and rates.
- Required database migrations must have a backup/rollback plan.
- Client/server compatibility changes must be tested from a clean managed-client path before publication.
- Never instruct players to disable antivirus globally.

## Runtime verification after deployment

A release is not healthy merely because the Java process starts. Verify:

- login listener on 8484;
- all 20 channel listeners on 7575–7594;
- the configured channel count matches the live channel count;
- all player-facing relay ports are reachable;
- the website/status integration reports the intended server state;
- the active release symlink points to the intended release;
- startup logs contain no unresolved production warnings;
- the patch/launcher endpoints are healthy when the deployment includes client artifacts.

The repository runtime verifier is:

```bash
python3 tools/verify_channel_runtime.py --config config.yaml --host 127.0.0.1
```

Treat any missing configured login/channel listener as a failed release gate.

## Database migrations

- Back up immediately before a production migration.
- Apply migrations in their documented dependency order.
- Verify schema constraints and indexes after migration.
- Test idempotency/safe failure before relying on a migration in production.
- Test rollback behavior for multi-step reward/currency mutations.
- Do not broaden database privileges simply to make a migration convenient.

Current EverLeaf systems include dedicated migrations for weekly progression, Verdant Marks, PQ Points, NX rewards, Rooted/Forge work, and other maintained features. Use the migration files themselves as the executable source of truth.

## Backup and disaster recovery

Production has automated OCI Object Storage backup coverage for MySQL and critical server/web/nginx/systemd/configuration state, plus broader periodic client/WZ recovery material. Production deployment invokes a backup before release switch.

Operational requirements:

- Preserve automated daily/weekly backup timers.
- Periodically download and validate an archive independently.
- Verify SHA256/archive integrity and SQL contents.
- Rehearse an isolated full restore periodically.
- Keep rollback and disaster recovery distinct: release rollback restores a prior application release; DR restores lost infrastructure/data.

## Security boundary

- Keep secrets out of Git.
- Use least-privilege database/service accounts.
- Keep MySQL private.
- Keep SSH key based and restrict exposed ports.
- Preserve launcher-ticket and website-authentication controls.
- Treat malformed packet, transaction-race, admin-command, and web-session testing as release-hardening work, not optional polish.
- Keep logs free of credentials, tokens, passwords, PIC/PIN values, and unnecessary player-sensitive data.

## Operations ownership

For exact readiness gaps, current production SHA, current WZ count, and remaining verification work, use the master checklist. Dated production snapshots and old network/release reports have been moved to `../archive/audits/` specifically so they cannot be mistaken for this current contract.

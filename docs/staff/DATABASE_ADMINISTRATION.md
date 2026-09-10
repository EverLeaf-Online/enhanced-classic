# EverLeaf Database Administration and DBeaver Runbook

This is the maintained staff procedure for inspecting and making deliberate production database changes. It documents the safe workflow, not production credentials. Secrets, passwords, SSH private keys, and connection strings must remain outside Git.

For backup/restore and disaster recovery, use [`RECOVERY_AND_RESTORE.md`](RECOVERY_AND_RESTORE.md). For moderation/economy remediation, use [`OPERATIONS_AND_INCIDENTS.md`](OPERATIONS_AND_INCIDENTS.md).

## Safety boundary

- Production MySQL must not be exposed publicly just to make GUI administration easier.
- Use the already configured private/tunneled administration path rather than opening port 3306 to the Internet.
- Do not use the MySQL `root` account for the game server runtime.
- Use the least-privilege administrative identity suitable for the task.
- Never save database passwords, SSH private keys, or production connection exports in the repository.
- Treat direct production edits as exceptional. Prefer source-controlled migrations/tools when a change is part of application behavior.
- Take a fresh backup before destructive, schema-changing, or broad corrective work.

## DBeaver connection profile

Use the existing approved EverLeaf production connection. A safe profile should use an SSH tunnel/private path to the Oracle origin rather than a public MySQL listener.

Typical logical settings are:

- database engine: MySQL;
- database/schema: `cosmic` for the game database when that is the intended target;
- SSH host: the EverLeaf Oracle origin/admin endpoint already configured for staff;
- SSH authentication: approved staff key material stored outside the repository;
- database host from the tunneled session: normally loopback/private MySQL, not the public relay IP;
- database user: approved administrative/maintenance user with only the privileges required for the task.

Do not copy the player-facing relay address into a database profile. The game relay and database administration path are separate concerns.

## Read-only inspection workflow

Prefer read-only inspection first.

1. Connect through the approved DBeaver profile.
2. Confirm the server/schema before running anything:

```sql
SELECT DATABASE();
SELECT CURRENT_USER();
SELECT @@hostname;
SELECT NOW();
```

3. Inspect the target rows with a narrow `SELECT` before editing.
4. Include stable identifiers such as account ID, character ID, inventory item ID, or transaction/ledger key when available.
5. Avoid unbounded table scans during peak production unless necessary.
6. Export/copy only the minimum evidence needed for an investigation; do not dump unrelated player data into tickets/chat.

## Safe manual data correction

Use a manual production correction only when the desired mutation is understood and a source-controlled migration/tool would be disproportionate or too slow for a contained incident.

Before the change:

1. Identify the exact table(s), row(s), and expected before/after state.
2. Capture the current values with `SELECT`.
3. Determine foreign-key/dependent-row implications.
4. Take/verify a fresh backup for destructive or material economy/account changes.
5. Use an explicit transaction when the engine/table path supports it.

Generic pattern:

```sql
START TRANSACTION;

SELECT ...
FROM ...
WHERE <stable-key> = ...
FOR UPDATE;

UPDATE ...
SET ...
WHERE <stable-key> = ...;

SELECT ROW_COUNT();

SELECT ...
FROM ...
WHERE <stable-key> = ...;

-- COMMIT only after the result is verified.
COMMIT;
```

Use `ROLLBACK` instead of `COMMIT` if the affected-row count or resulting state is not exactly what was intended.

Never run a broad `UPDATE` or `DELETE` without first proving the `WHERE` clause with the corresponding `SELECT`.

## Destructive delete workflow

Account/character deletion is currently a known policy/integrity area because dependent character/inventory/equipment/quest/social rows can remain if deletion is handled incorrectly.

Until the cleanup policy/tooling is complete:

- do not manually purge an account by deleting only the `accounts` row;
- do not assume cascading relationships cover every historical table;
- enumerate dependent rows first;
- preserve a backup;
- use a reviewed cleanup plan that covers character and dependent state;
- verify counts after the transaction.

The maintained known-issues register tracks this gap.

## Economy/currency corrections

For mesos, NX, Verdant Marks, PQ Points, merchant balances, or other valuable state:

- identify the authoritative balance table and any ledger/history table;
- preserve the pre-change balance and relevant ledger rows;
- prefer the same transactional invariants used by application code;
- do not adjust only one side of a balance/ledger pair if the system expects both;
- verify no concurrent session is racing the same state when that matters;
- record the remediation reason and affected identifiers.

A player ban and an economy correction are separate actions. Banning an account does not reconcile illegitimate currency/items automatically.

## Schema inspection

Before applying a migration or diagnosing a schema issue:

```sql
SHOW TABLES;
SHOW CREATE TABLE <table_name>;
SHOW INDEX FROM <table_name>;
```

Verify expected columns, uniqueness constraints, indexes, foreign keys, and storage engine rather than assuming a migration ran because a similarly named table exists.

## Migration workflow

EverLeaf migration files live under `database/sql/migration/`. The inherited migration README notes that migrations are manual and generally intended to run once; EverLeaf also has project-specific migrations for current systems.

For a production migration:

1. Review the SQL file in Git and identify prerequisites/dependencies.
2. Test it against a disposable/representative database first when practical.
3. Confirm whether the migration is idempotent; **do not assume it is**.
4. Take a production backup immediately before application.
5. Capture relevant pre-migration schema state.
6. Apply only the required migration(s), in documented dependency order.
7. Verify schema/index/constraint state afterward.
8. Verify the affected application subsystem.
9. Record the migration file(s), source SHA, time, and result.

Do not simply select every file in `database/sql/migration/` and execute the directory against production.

## DBeaver transaction settings

For production write work, make transaction boundaries deliberate. If DBeaver auto-commit is enabled, every statement may commit immediately and remove your chance to roll back a mistaken edit.

For material manual writes:

- disable auto-commit for the session when appropriate;
- execute the narrow `SELECT`/lock/mutation/verification sequence;
- review affected-row count;
- `COMMIT` explicitly only after verification;
- `ROLLBACK` on any unexpected result.

Re-enable your normal connection behavior afterward so a forgotten open transaction does not hold locks indefinitely.

## Avoid GUI grid-edit surprises

DBeaver's editable result grid can generate SQL on your behalf. Before saving grid edits on production:

- ensure the table has a stable primary/unique key;
- review the generated SQL/affected row targeting;
- avoid editing result sets built from ambiguous joins;
- avoid mass paste/fill operations on valuable state;
- prefer explicit SQL for sensitive account/economy changes because it is easier to review and record.

## Long-running queries and locks

If an administrative query is unexpectedly slow:

- do not repeatedly rerun it;
- inspect the query plan/index assumptions on a safe environment when possible;
- check whether the session holds locks or an open transaction;
- cancel the query rather than allowing an accidental unindexed mutation to monopolize production.

Never kill arbitrary MySQL sessions without identifying what they are doing and whether the game server depends on them.

## Credential and connection hygiene

- Do not commit `.dbeaver-*`, exported connection profiles containing secrets, SSH private keys, passwords, or screenshots showing credentials.
- Keep saved passwords in the approved local credential store only.
- Remove stale staff access promptly.
- Rotate credentials if a database password/private key is exposed.
- Do not paste production credentials into AI/chat/GitHub issues.

## After any material production write

Verify:

- exact affected-row count;
- expected resulting row values;
- related ledger/dependent state;
- application behavior for the affected account/subsystem;
- no new errors in server logs;
- the backup/recovery path remains available.

Record the reason, operator, time, affected identifiers, and SQL/migration/tool used without recording secrets.

## What belongs in Git instead of DBeaver

Use a source-controlled migration/tool when the change is:

- required for every environment/new install;
- part of a feature rollout;
- a schema/index/constraint change;
- a repeatable remediation pattern;
- important enough that future operators must reproduce it.

DBeaver is an administration client, not the source of truth for application schema evolution.
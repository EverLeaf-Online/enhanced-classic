# EverLeaf Production Recovery and Restore Runbook

This runbook covers normal service recovery, release rollback, pre-change backup, and disaster/data restore for EverLeaf production. It is intentionally separate from ordinary development and from gameplay moderation.

Canonical production topology and release policy are documented in [`../operations/PRODUCTION_AND_RELEASE.md`](../operations/PRODUCTION_AND_RELEASE.md). Incident handling is in [`OPERATIONS_AND_INCIDENTS.md`](OPERATIONS_AND_INCIDENTS.md).

## Production identifiers

Current maintained production layout:

- origin/deployment host: `132.145.141.79`
- player-facing relay: `129.159.114.146`
- source checkout: `/opt/everleaf/server`
- active release symlink: `/opt/everleaf/current`
- immutable releases: `/opt/everleaf/releases/`
- previous-release marker used by the guarded deploy: `/opt/everleaf/.previous-release`
- game service: `everleaf.service`
- website checkout: `/opt/everleaf/web-repo`
- website runtime symlink: `/opt/everleaf/web -> /opt/everleaf/web-repo/web`
- website mutable state: `/opt/everleaf/web-state`
- website service: `everleaf-web.service`
- backup service: `everleaf-backup.service`
- production login port: `8484`
- channel ports: `7575–7594` (20 channels)
- backup bucket: OCI Object Storage `everleaf-backups`

Do not assume a copied release SHA in this runbook is current. Read the master checklist and `readlink -f /opt/everleaf/current` at incident time.

## Safety rules

- Preserve evidence and data before destructive changes when possible.
- Never edit `/opt/everleaf/current` as a mutable working directory; it is a symlink to a release.
- Do not restore an old database merely because application code is unhealthy.
- Application rollback and persistent-state remediation are different operations.
- Take/verify a backup before schema changes or broad data remediation when the system state allows it.
- Keep credentials outside commands/history where possible; do not paste DB/cloud secrets into tickets or chat logs.
- When unsure whether state corruption is continuing, protect persistence first and investigate second.

## 1. Fast health triage

On the Oracle origin:

```bash
sudo systemctl status everleaf.service --no-pager
sudo systemctl status everleaf-web.service --no-pager
readlink -f /opt/everleaf/current
sudo journalctl -u everleaf.service -n 120 --no-pager
```

Verify the configured local login/channels using the runtime verifier shipped with the active release:

```bash
python3 /opt/everleaf/current/tools/verify_channel_runtime.py \
  --config /opt/everleaf/current/config.yaml \
  --host 127.0.0.1
```

Check listeners when needed:

```bash
ss -ltnp | grep -E ':(8484|757[5-9]|758[0-9]|759[0-4])\b'
```

If the Java process is active but the runtime verifier reports a missing listener, treat the release as unhealthy.

## 2. Normal service restart

A restart is appropriate when the active release is known-good and only the runtime/service needs recovery.

Before restart, record current release and recent logs:

```bash
readlink -f /opt/everleaf/current
sudo journalctl -u everleaf.service -n 120 --no-pager
```

Restart:

```bash
sudo systemctl restart everleaf.service
```

Then verify:

```bash
sudo systemctl is-active everleaf.service
python3 /opt/everleaf/current/tools/verify_channel_runtime.py \
  --config /opt/everleaf/current/config.yaml \
  --host 127.0.0.1
```

A restart does **not** repair bad database writes or an invalid release.

## 3. Trigger and verify a production backup

The guarded production deployment invokes the backup service before release switch. For a manual pre-change backup:

```bash
BEFORE="$(sudo find /opt/everleaf/backups -type f -printf '%T@ %p\n' 2>/dev/null | sort -nr | head -1 || true)"
sudo systemctl start everleaf-backup.service
systemctl show everleaf-backup.service --property=Result --value
AFTER="$(sudo find /opt/everleaf/backups -type f -printf '%T@ %p\n' 2>/dev/null | sort -nr | head -1 || true)"
printf 'Before: %s\nAfter:  %s\n' "$BEFORE" "$AFTER"
```

Required result:

- service result is `success`;
- a non-empty latest backup path exists;
- for high-risk work, also verify the expected Object Storage upload/remote object rather than relying only on a local file.

Do not delete the previous backup merely to make the latest result easier to identify.

## 4. Release rollback

Use release rollback when the **application release** is bad but the database/content state does not require restoration.

### Preferred automatic path

The maintained GitHub production deployment already records the previous release and automatically rolls back when its post-switch health/content validation fails.

### Manual rollback

First inspect current/previous release pointers:

```bash
CURRENT="$(readlink -f /opt/everleaf/current)"
PREVIOUS="$(cat /opt/everleaf/.previous-release 2>/dev/null || true)"
printf 'Current:  %s\nPrevious: %s\n' "$CURRENT" "$PREVIOUS"
test -n "$PREVIOUS" && test -d "$PREVIOUS"
```

Inspect the candidate previous release before switching:

```bash
test -f "$PREVIOUS/config.yaml"
test -s "$PREVIOUS/target/everleaf-server-1.0-SNAPSHOT.jar"
```

Switch atomically:

```bash
sudo ln -sfn "$PREVIOUS" /opt/everleaf/current.rollback
sudo mv -Tf /opt/everleaf/current.rollback /opt/everleaf/current
sudo systemctl restart everleaf.service
```

Validate:

```bash
sudo systemctl is-active everleaf.service
python3 "$PREVIOUS/tools/verify_channel_runtime.py" \
  --config "$PREVIOUS/config.yaml" \
  --host 127.0.0.1
readlink -f /opt/everleaf/current
```

If the rollback release is also unhealthy, stop cycling releases blindly. Preserve logs and escalate the incident.

## 5. Roll forward to an existing release

If a previously built immutable release is known-good and must be restored as active:

```bash
ls -ld /opt/everleaf/releases/*
```

Select the exact release deliberately, then validate its config/JAR/WZ before switching. Do not choose by directory timestamp alone.

Use the same atomic symlink procedure as rollback, then restart and run the runtime verifier.

## 6. Website recovery

Check the website service and runtime link:

```bash
sudo systemctl status everleaf-web.service --no-pager
readlink -f /opt/everleaf/web
sudo journalctl -u everleaf-web.service -n 120 --no-pager
```

The intended website runtime points to the Git-backed checkout while mutable state remains under `/opt/everleaf/web-state`.

For a simple runtime failure with known-good files:

```bash
sudo systemctl restart everleaf-web.service
sudo systemctl is-active everleaf-web.service
```

Do not replace `/opt/everleaf/web-state` with repository copies; it contains mutable production state/secrets that are deliberately externalized.

## 7. Database restore decision gate

A database restore is a **last-resort data-recovery operation**, not an application rollback.

Before restoring a database, answer:

- What exact data is corrupt/lost?
- When did corruption begin?
- Which backup is the last known-good point?
- How much legitimate player progress will a full restore discard?
- Can targeted transactional remediation safely repair only affected rows instead?
- Is the exploit/bug that caused the bad writes already contained?
- Has a current backup/snapshot of the damaged state been preserved for investigation?

Prefer targeted remediation when affected rows/transactions are identifiable.

## 8. Full backup restore rehearsal / disaster recovery

EverLeaf backups include MySQL and critical server/web/nginx/systemd/configuration state, with broader periodic recovery material. Restore should first be rehearsed **outside the live paths**.

### Obtain the archive

Use the configured OCI access path to list/download the intended object from the `everleaf-backups` bucket into a dedicated restore workspace. Object names and credentials vary by backup run, so do not paste a guessed object name into this runbook.

Example workspace:

```bash
sudo install -d -m 700 /opt/everleaf/restore-work
sudo chown "$USER":"$USER" /opt/everleaf/restore-work
cd /opt/everleaf/restore-work
```

After download, verify the recorded SHA256 if supplied and verify the archive before extracting. For zstd-compressed tar archives, typical checks are:

```bash
sha256sum <backup-archive>
tar --zstd -tf <backup-archive> >/tmp/everleaf-restore-filelist.txt
```

Never extract an unverified production backup directly over `/opt/everleaf/current`, `/opt/everleaf/server`, `/opt/everleaf/web-state`, or the live database.

### Extract into isolation

```bash
mkdir extracted
tar --zstd -xf <backup-archive> -C extracted
find extracted -maxdepth 3 -type f | sort | less
```

Confirm the archive contains the expected SQL dump and required critical files before touching production.

### Validate the SQL dump

Inspect headers/database names without importing into production. The current production database includes `cosmic`.

Use a disposable/local MySQL instance or isolated schema for the rehearsal when possible. Never put DB passwords directly into committed files or public command transcripts.

A generic import shape is:

```bash
mysql <approved-admin-connection-options> < <validated-dump.sql>
```

The exact credential option must come from the VM's approved secret/administration setup; this repository intentionally does not contain production credentials.

After an isolated import, verify expected tables/counts/constraints and run application-level checks before calling the backup restorable.

## 9. Production data restore

Only perform after the restore decision gate and owner/operator approval.

1. Stop/contain application writes if required.
2. Preserve a fresh backup of the damaged current state when possible.
3. Record the selected backup object/archive and its SHA256.
4. Verify archive integrity.
5. Verify the SQL dump and exact restore scope.
6. Restore into the intended database using the approved administrative credential path.
7. Apply only migrations required for the selected application release; do not blindly replay every historical SQL file.
8. Restart the required services.
9. Verify login, all 20 channels, account/character persistence, and the affected subsystem.
10. Record lost-time window/impact and any targeted reconciliation still required.

## 10. Release + database compatibility

After restoring old persistent state, confirm the active application release expects that schema/content baseline. Conversely, rolling the application back while leaving a newer incompatible schema can also fail.

Use migration files as executable source of truth, and review migration dependencies before changing schema during recovery.

## 11. Post-recovery verification

At minimum:

```bash
readlink -f /opt/everleaf/current
sudo systemctl is-active everleaf.service
sudo systemctl is-active everleaf-web.service
python3 /opt/everleaf/current/tools/verify_channel_runtime.py \
  --config /opt/everleaf/current/config.yaml \
  --host 127.0.0.1
```

Also verify as relevant:

- external relay ports;
- website status/auth paths;
- launcher/patch endpoints if client artifacts were involved;
- database writes/persistence;
- account login and character selection;
- the exact subsystem that triggered recovery;
- no unresolved startup warnings or rapid restart loop.

## 12. Recovery record

Record:

- incident/recovery start and end time;
- active release before/after;
- backup archive/object used, if any;
- SHA256/integrity result;
- database restore scope/time window, if any;
- services restarted;
- validation commands/results;
- player/economy impact;
- follow-up bug/fix/regression work.

## Periodic rehearsal

Even when production is healthy, periodically perform an isolated full restore rehearsal: download a real stored backup, verify checksum/archive, inspect SQL, restore into isolation, and confirm the recovered data/application assumptions. A backup that has never been restored is not fully validated disaster recovery.
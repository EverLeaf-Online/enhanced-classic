# EverLeaf Emergency Shutdown and Containment

Use this procedure only when continued production operation presents a greater risk than temporary downtime—for example, active persistent-state corruption, an uncontrolled duplication/economy exploit, credential/remote compromise, or another incident where writes must stop immediately.

For normal restart/rollback/restore, use [`RECOVERY_AND_RESTORE.md`](RECOVERY_AND_RESTORE.md). For exploit investigation/remediation, use [`OPERATIONS_AND_INCIDENTS.md`](OPERATIONS_AND_INCIDENTS.md).

## Decision rule

Prefer the **smallest safe containment** first. Disable/restrict one affected feature when that reliably stops the damage. Stop the entire game service when the harmful write path cannot be isolated quickly or when continued state mutation would make recovery materially worse.

Do not use a full shutdown to hide an ordinary gameplay bug, clear inconvenient map state, or avoid collecting evidence.

## Before stopping, when seconds permit

Record:

```bash
date -u
readlink -f /opt/everleaf/current
sudo systemctl status everleaf.service --no-pager
sudo journalctl -u everleaf.service -n 120 --no-pager
```

Preserve the incident time, affected accounts/characters/transactions, and current release identity. Do not delay containment merely to make the evidence package perfect while corruption is actively continuing.

## Emergency stop

On the Oracle production origin:

```bash
sudo systemctl stop everleaf.service
sudo systemctl is-active everleaf.service
```

Expected post-stop state is `inactive`/not active.

Confirm the local game listeners are gone:

```bash
ss -ltnp | grep -E ':(8484|757[5-9]|758[0-9]|759[0-4])\b' || true
```

If listeners remain, identify the process before killing anything manually. Do not use broad `pkill java`/`killall java` on a host that may run other Java workloads.

## Preserve data after containment

If the host/database are not themselves compromised and taking a backup will not re-enable harmful application writes, trigger the maintained backup service:

```bash
sudo systemctl start everleaf-backup.service
systemctl show everleaf-backup.service --property=Result --value
```

Preserve both:

- a known-good backup from before the incident if available;
- a post-containment snapshot/backup of the damaged state when useful for investigation and targeted remediation.

Do not overwrite/delete the only pre-incident backup.

## Website / account writes

Stopping `everleaf.service` stops the game service, not necessarily website/CMS account actions.

If the incident also affects website/auth/payment/account writes and those writes must stop, contain the website separately:

```bash
sudo systemctl stop everleaf-web.service
sudo systemctl is-active everleaf-web.service
```

Do this only when the website itself is part of the risk. Keeping a safe status/support page available can be preferable during a game-only outage.

## Do not restart until

At minimum:

- the damaging path is identified or reliably contained;
- required evidence is preserved;
- the intended application release/fix/rollback is selected;
- database/economy remediation scope is understood enough not to make it worse;
- any required backup has completed/been verified;
- the operator knows what health checks will be used after restart.

## Recovery choices

### Code/release regression

Roll back to the known-good immutable release using [`RECOVERY_AND_RESTORE.md`](RECOVERY_AND_RESTORE.md).

### Exploit in current source

Fix the authoritative server-side validation/transaction path, add regression coverage where practical, build/deploy through the guarded release flow, and separately remediate illegitimate persistent gains.

### Persistent database corruption

Prefer targeted remediation when affected rows/transactions are identifiable. Full DB restore is last resort because it discards legitimate progress after the selected backup point.

### Host/credential compromise

Keep affected services stopped, rotate/revoke compromised credentials through their approved systems, preserve forensic evidence, and do not trust the host/application merely because the service can restart.

## Restart after containment

Once approved:

```bash
sudo systemctl start everleaf.service
sudo systemctl is-active everleaf.service
python3 /opt/everleaf/current/tools/verify_channel_runtime.py \
  --config /opt/everleaf/current/config.yaml \
  --host 127.0.0.1
```

If the website was stopped and is safe to restore:

```bash
sudo systemctl start everleaf-web.service
sudo systemctl is-active everleaf-web.service
```

Also verify affected player/account/economy behavior before declaring the incident closed.

## Communication

During an active security/economy incident, communicate service status without publishing reproduction steps, detection gaps, private account/network data, credentials, or unpatched exploit details.

## Incident closure

Record:

- why emergency containment was required;
- who initiated it and when;
- services stopped/restarted;
- release before/after;
- backup/evidence identifiers;
- persistent-state remediation performed;
- regression/fix reference;
- validation performed before reopening.
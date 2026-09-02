# Everleaf Deployment Checklist

This checklist separates development convenience from public-server requirements.

## Before any public deployment

- [ ] Required GitHub `build` check is green.
- [ ] `master` contains only reviewed/squashed stable changes.
- [ ] Use a dedicated database user; never run the game server as MySQL `root`.
- [ ] Set a strong database password outside the repository through Everleaf environment overrides.
- [ ] Disable automatic account registration unless the public account system explicitly requires it.
- [ ] Keep Cash Shop rate coupons disabled.
- [ ] Configure public `EVERLEAF_HOST` / LAN / localhost values for the deployment topology.
- [ ] Restrict database network access so MySQL is not publicly exposed.
- [ ] Allow only required game/SSH ports through the host firewall.
- [ ] Use SSH-key authentication; disable password SSH where practical.
- [ ] Create database backup and restore procedures before inviting players.
- [ ] Configure log rotation and disk-usage monitoring.
- [ ] Confirm server startup emits no unresolved Everleaf deployment warnings.
- [ ] Verify the packaged build manifest matches the expected commit, protocol version, level cap, and rates.

## Post-start runtime verification

- [ ] Treat the configured channel count as a runtime release gate, not just a config value. EverLeaf currently targets **8 channels**.
- [ ] After the login/world/channel processes are started, run `python3 tools/verify_channel_runtime.py --config config.yaml --host 127.0.0.1` from the deployed server tree.
- [ ] Require exit code `0` before declaring the deployment healthy. Any missing login/channel port means the deployment failed even if some channels are reachable.
- [ ] Confirm the verifier reports `configuredChannels: 8`, `liveChannels: 8`, and no `missingChannelPorts` for the current production target.
- [ ] Confirm the website/status API reports the same configured total and live channel count; do not mask a partial runtime such as 3 live / 8 configured as a healthy eight-channel deployment.
- [ ] Re-run the runtime verifier after server restarts, config changes, or channel-count changes.

## Database migrations

- [ ] Back up the database immediately before applying a new Everleaf migration.
- [ ] Apply `database/sql/migration/everleaf_weekly_progression.sql` before enabling persistent post-200 weeklies.
- [ ] Apply `database/sql/migration/everleaf_verdant_marks.sql` after the weekly progression migration and before allowing weekly claims.
- [ ] Confirm `everleaf_weekly_account_state` exists and is keyed by account + week.
- [ ] Confirm `everleaf_weekly_character_objective` exists and is keyed by character + week + objective.
- [ ] Confirm `everleaf_verdant_mark_balance` exists and is keyed by account.
- [ ] Confirm `everleaf_verdant_mark_ledger` exists with the unique account + reason type + reason key constraint.
- [ ] Verify the account and character foreign keys cascade/delete as intended.
- [ ] Run a two-character/same-account claim test and confirm the valuable weekly reward budget and Verdant Marks balance are shared.
- [ ] Run a concurrent/double-claim test and confirm the second claim is rejected and no duplicate Marks are minted.
- [ ] Simulate a claim failure and confirm weekly accounting, objective state, balance, and ledger all roll back together.
- [ ] Verify spend attempts cannot take a Verdant Marks account balance below zero.
- [ ] Verify every successful earn/spend has exactly one matching ledger row.

## Gameplay validation

- [ ] New character creation and login work.
- [ ] Existing-character load migration applies survivability floors safely.
- [ ] Level-up works through 199 -> 200 and all extended milestones.
- [ ] Level 250 cannot gain an invalid 251st level.
- [ ] `@progress` reports the correct tier and next milestone.
- [ ] `@weekly` / `@weeklies` show the correct current UTC week, character objective progress, shared account budget, and Verdant Marks balance.
- [ ] Weekly completion pays Verdant Marks exactly once.
- [ ] Verdant Marks are account-bound and cannot be traded/transferred through normal player systems.
- [ ] Donation systems have no conversion path into Verdant Marks.
- [ ] Reward-shop retries use unique transaction IDs so failed/retried requests are idempotent without blocking legitimate repeat purchases.
- [ ] EXP requirements from 201 through 249 are valid and monotonic.
- [ ] Cash Shop does not expose paid rate coupons.
- [ ] Rankings sort characters correctly above level 200.
- [ ] Basic trade, storage, guild, party, PQ, boss, and logout flows are regression-tested.

## Client safety

- [ ] Do not tell players to disable antivirus globally.
- [ ] Document provenance and hashes for any distributed binaries.
- [ ] Keep proprietary client/game assets out of the server-source repository.
- [ ] Test client/server compatibility from a clean machine before publishing downloads.

## Launch gates

### Development test
Local/private connectivity only. Development defaults are acceptable if clearly isolated.

### Closed alpha
Invite-only accounts, backups enabled, operational logging enabled, known issue list published to testers.

### Public beta
Public registration flow, monitoring, abuse controls, backup restoration test, economy review, and deployment hardening complete.

### Public launch
Requires explicit project-owner approval after beta telemetry, balance, security, operational cost, and legal-risk review.

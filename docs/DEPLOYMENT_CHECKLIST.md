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

## Gameplay validation

- [ ] New character creation and login work.
- [ ] Existing-character load migration applies survivability floors safely.
- [ ] Level-up works through 199 -> 200 and all extended milestones.
- [ ] Level 250 cannot gain an invalid 251st level.
- [ ] `@progress` reports the correct tier and next milestone.
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

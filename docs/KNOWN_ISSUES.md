# EverLeaf Known Issues

This is the maintained EverLeaf known-issues register. It is intentionally separate from `docs/archive/upstream/issues.txt`, which is inherited historical material and is **not** EverLeaf's current issue list.

The master development checklist remains authoritative for project-wide readiness. This file focuses on defects, user-visible limitations, and unresolved validation risks that operators/testers should know about now.

## Severity guide

- **Critical** — active risk of persistent corruption, compromise, or large-scale economy/account damage.
- **High** — meaningful abuse/security/gameplay risk or broad inability to play correctly.
- **Medium** — material defect/limitation with a workaround or narrower scope.
- **Low** — minor behavior, polish, or operational inconvenience.
- **Validation** — not yet a confirmed defect, but an area that still lacks enough runtime evidence for public-beta confidence.

## Confirmed unresolved issues

### Medium — historical account purge/deletion can leave character data

**Status:** Preventive source fix ready; live audit/remediation and migration application pending

The legacy base schema does not enforce a foreign-key relationship from `characters.accountid` to `accounts.id`. A direct manual `DELETE` of an account row can therefore leave character rows behind, and deleting the character row through a blind database cascade would also bypass EverLeaf's existing application-level character cleanup for inventory, quests, pets, social state, merchant state, and related records.

Canonical `master` contains:

- `tools/everleaf-ops/audit-account-character-integrity.sql` — read-only audit for orphaned characters and key dependent-row integrity;
- `database/sql/migration/everleaf_account_character_integrity.sql` — a fail-closed relationship guard that installs `characters.accountid -> accounts.id` with **ON DELETE RESTRICT / ON UPDATE RESTRICT** only when the existing data is clean;
- migration smoke coverage proving an account with characters cannot be raw-deleted while an empty account remains removable.

The migration deliberately refuses to install if historical orphaned characters already exist. It also refuses to silently replace an unexpected pre-existing foreign-key rule.

This issue is **not closed in production yet**. Before applying the migration, run the read-only audit against production, identify any existing orphaned rows, back up the database, remediate those rows through an explicit reviewed cleanup plan, then apply and verify the guard. Do not mass-delete historical orphan trees automatically.

## Current user-facing limitations

### Medium — account recovery is staff-queue based, not self-service reset

**Status:** Implemented request intake; manual resolution required

The public `/recover` form accepts a username or valid account email, deduplicates pending submissions within a day, and deliberately returns the same success response to prevent account enumeration. Requests enter the staff CMS queue with `pending`, `resolved`, or `rejected` status.

The current code does **not** implement an automated password-reset token/email flow. Staff must verify and resolve requests under the recovery procedure.

### Low — direct modern class-card/Evan creation UI is paused

**Status:** Deferred by design

The accepted Evan flow remains Beginner creation followed by the in-game NPC conversion path. The broader login/world/character-select redesign and direct modern class cards are deferred until the Kaentake review/Phase 2 decision.

## Public-beta validation risks

The following are not automatically confirmed bugs, but they remain known risk areas because full runtime coverage is incomplete. Completed build, publish, deployment, and CI checks are intentionally omitted from this active list.

### GM command live smoke

**Status:** Validation required

The GM2 permission fixes for `gachalist`, `loot`, and `mobskill` and the `!startevent` participant-limit fix are deployed to production with regression coverage. One controlled live smoke remains: confirm an ordinary player cannot invoke the GM2 utilities, GM2+ can invoke them, and `!startevent 25` actually starts with a limit of 25.

### Boss and Party Quest lifecycle

**Status:** Validation required

Complete multi-client runs remain for major bosses/PQs, including prerequisite/entry behavior, leader loss, disconnect/rejoin, death/revive, timeout, stage/phase transitions, cleanup, lockouts, reward delivery, full-inventory behavior, and duplicate/replay resistance.

### Full class/combat parity

**Status:** Validation required

A systematic runtime matrix across Explorer, Cygnus, Aran, and Evan attacks, buffs, passives, summons, movement, status effects, formulas, and party interactions is still pending.

### Transaction/concurrency edge cases

**Status:** Validation required

Remaining checks are limited to explicit disconnect/replay/race paths not yet separately verified, including quest reward replay, drop/pickup races, concurrent custom-currency operations, and cross-system persistence races.

### Launcher-only and single-client runtime enforcement

**Status:** Published; runtime validation required

The managed launcher/client hardening is built and published. Remaining player-machine checks are direct `EverLeaf.exe` rejection, normal launcher launch, second-launch rejection, rapid/race second-launch rejection, interrupted-update rollback/retry, and crash/disconnect handling.

These controls enforce policy for the EverLeaf-managed stock binaries. A player who arbitrarily patches or replaces local binaries is outside what a purely client-side mutex/ticket can make tamper-proof; cryptographic server-backed launcher authorization would require a separate server-validated launch-session protocol.

### Display mode / resolution runtime verification

**Status:** Implemented and published; runtime validation required

The Kaentake-informed, independently implemented display work is now in the published managed client. Runtime-test the in-game resolution selector, persistence of the selected HD resolution, fullscreen behavior, and Alt+Enter transitions across the supported modes. Confirm there is no fallback to 800×600 and no UI placement or input-coordinate corruption.

### Discord Rich Presence gameplay runtime verification

**Status:** Implemented and published; runtime validation required

The richer native presence implementation is now in the published managed client. Verify character name, level, job, and field activity across login, character entry, level/job changes, map changes, channel changes, logout, reconnect, and Discord-not-running/reconnect cases, and confirm stale activity is cleared during transitions.

### Website/account release hardening

**Status:** Validation required

Remaining checks are limited to rankings behavior for stale/deleted/renamed characters and final admin authentication/session/CSRF/rate-limit controls.

### Performance/load/reliability

**Status:** Validation required

Remaining work is realistic concurrent-player load, concurrent boss/PQ instances, database and scheduler hotspot profiling, heap/GC/thread/socket/file-descriptor growth profiling, and reconnect/network-failure behavior.

## Reporting a new issue

For a gameplay/client issue, capture the exact action, expected vs actual behavior, character/job/level, map/NPC/boss/PQ involved, timestamp/time zone, reproduction frequency, and screenshot/video/log when useful.

For suspected duplication, authentication bypass, unauthorized GM/admin access, economy abuse, or another exploitable security defect, **do not publish detailed reproduction steps publicly while it is exploitable**. Preserve evidence and route it through staff/security handling.

Client logs/dumps may contain debugging context and should be submitted intentionally through an official support path. Never include passwords, PIC/PIN values, launcher/session tokens, or private credentials.

## Maintenance rule

- Keep this active register unresolved-only. When the needed production/runtime validation passes, remove the completed item or completed sub-check from this file rather than leaving it mixed into a remaining-risk entry.
- Convert fixed critical/high defects into regression coverage when practical.
- Do not add inherited Cosmic/HeavenMS issues here unless they are verified against the current EverLeaf source/release.
- Do not use this file as a replacement roadmap; broad planned work belongs in `EVERLEAF_MASTER_CHECKLIST.md`.

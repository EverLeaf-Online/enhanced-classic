# EverLeaf Known Issues

This is the maintained EverLeaf known-issues register. It is intentionally separate from `docs/archive/upstream/issues.txt`, which is inherited historical material and is **not** EverLeaf's current issue list.

The master development checklist remains authoritative for project-wide readiness. This file focuses on defects, user-visible limitations, and unresolved validation risks that operators/testers should know about now.

## Severity guide

- **Critical** — active risk of persistent corruption, compromise, or large-scale economy/account damage.
- **High** — meaningful abuse/security/gameplay risk or broad inability to play correctly.
- **Medium** — material defect/limitation with a workaround or narrower scope.
- **Low** — minor behavior, polish, or operational inconvenience.
- **Validation** — not yet a confirmed defect, but an area that still lacks enough runtime evidence for public-beta confidence.

## Fixed on canonical `master`, pending production deployment

### High — `gachalist`, `loot`, and `mobskill` were registered at rank 0

**Status:** Source-fixed; production deployment/verification pending

The three commands live in the `gm2` command package and are intended to be GM-only. They were previously registered through the overload that defaulted their minimum rank to 0, which allowed ordinary-player invocation through the `@` prefix.

Canonical `master` now explicitly registers all three at **GM rank 2**:

- `gachalist`
- `loot`
- `mobskill`

`src/test/java/client/command/CommandsExecutorGm2PermissionTest.java` guards the registrations so they cannot silently fall back to the rank-0 overload.

Until a production game-server deployment containing the fix is confirmed, operators should still treat any ordinary-player use of these commands on the currently running release as unintended and preserve relevant evidence.

### Low — `!startevent` ignored a single player-limit argument

**Status:** Source-fixed; production deployment/verification pending

The previous implementation only parsed `params[0]` when more than one parameter was supplied, so `!startevent 25` silently retained the default capacity of 50.

Canonical `master` now accepts either no argument (default **50**) or exactly one positive integer player limit. Zero, negative, non-numeric, and extra arguments are rejected with syntax guidance. `src/test/java/client/command/commands/gm3/StartEventCommandTest.java` covers the default, valid custom limits, and invalid inputs.

## Confirmed source/data-integrity issues

### Medium — historical account purge/deletion can leave character data

**Status:** Preventive source fix ready; live audit/remediation and migration application pending

The legacy base schema does not enforce a foreign-key relationship from `characters.accountid` to `accounts.id`. A direct manual `DELETE` of an account row can therefore leave character rows behind, and deleting the character row through a blind database cascade would also bypass EverLeaf's existing application-level character cleanup for inventory, quests, pets, social state, merchant state, and related records.

Canonical `master` now contains:

- `tools/everleaf-ops/audit-account-character-integrity.sql` — read-only audit for orphaned characters and key dependent-row integrity;
- `database/sql/migration/everleaf_account_character_integrity.sql` — a fail-closed relationship guard that installs `characters.accountid -> accounts.id` with **ON DELETE RESTRICT / ON UPDATE RESTRICT** only when the existing data is clean;
- migration smoke coverage proving an account with characters cannot be raw-deleted while an empty account remains removable.

The migration deliberately refuses to install if historical orphaned characters already exist. It also refuses to silently replace an unexpected pre-existing foreign-key rule.

This issue is **not closed in production yet**. Before applying the migration, run the read-only audit against production, identify any existing orphaned rows, back up the database, remediate those rows through an explicit reviewed cleanup plan, then apply and verify the guard. Do not mass-delete historical orphan trees automatically.

## Current user-facing limitations

### Medium — raw game EXE launch is not a supported install path

**Status:** Known limitation

Launching the game executable directly can bypass launcher update/repair and launcher-ticket/bootstrap assumptions. The supported flow is the EverLeaf Launcher. Players who bypass it may see version mismatch, failed login, or stale native/WZ files.

### Medium — account recovery is staff-queue based, not self-service reset

**Status:** Implemented request intake; manual resolution required

The public `/recover` form accepts a username or valid account email, deduplicates pending submissions within a day, and deliberately returns the same success response to prevent account enumeration. Requests enter the staff CMS queue with `pending`, `resolved`, or `rejected` status.

The current code does **not** implement an automated password-reset token/email flow. Staff must verify and resolve requests under the recovery procedure.

### Low — richer Discord Rich Presence activity is intentionally disabled

**Status:** Deferred, not a regression

The published client includes EverLeaf-native Discord Rich Presence, but character/map/job activity hooks remain disabled until their v83 memory contracts are verified. Basic presence is expected; richer per-character/map data is not yet promised.

### Low — direct modern class-card/Evan creation UI is paused

**Status:** Deferred by design

The accepted Evan flow remains Beginner creation followed by the in-game NPC conversion path. The broader login/world/character-select redesign and direct modern class cards are deferred until the Kaentake review/Phase 2 decision.

## Public-beta validation risks

The following are not automatically confirmed bugs, but they remain known risk areas because full runtime coverage is incomplete:

### Boss and Party Quest lifecycle

**Status:** Validation required

Complete multi-client runs remain for major bosses/PQs, including prerequisite/entry behavior, leader loss, disconnect/rejoin, death/revive, timeout, stage/phase transitions, cleanup, lockouts, reward delivery, full-inventory behavior, and duplicate/replay resistance.

### Full class/combat parity

**Status:** Validation required

Explorer, Cygnus, Aran, and Evan have substantial implementation/static coverage, but a systematic runtime matrix across attacks, buffs, passives, summons, movement, status effects, formulas, and party interactions is still pending.

### Transaction/concurrency edge cases

**Status:** Validation required

Trade, storage, merchants, PlayerShop, Cash Shop transfer/re-entry, quest reward replay, drop/pickup races, and concurrent custom-currency operations need broader multi-client/race testing despite existing hardening and targeted runtime evidence.

### Clean-machine launcher/client behavior

**Status:** Validation required

Launcher self-update, damaged-file repair, interrupted-update rollback/retry, clean-machine installation, Alt+Enter/windowing transitions, crash/disconnect handling, and full channel switching still need final clean-player-machine regression coverage.

### Website/account integration

**Status:** Partially verified; remaining validation required

Registration/login against the production game database, live server/channel status integration, and production download/manifest links have been runtime-verified. Remaining website/account release hardening is focused on rankings behavior for stale/deleted/renamed characters plus final admin/session/CSRF/rate-limit checks.

### Performance/load/soak

**Status:** Partially verified; remaining validation required

Multi-hour/day soak and simultaneous login/channel-change behavior have been runtime-verified. Remaining stress work is realistic concurrent-player load, concurrent boss/PQ instances, DB hotspots, scheduler behavior, heap/GC/thread/socket/file-descriptor growth profiling, and reconnect/network-failure behavior.

## Reporting a new issue

For a gameplay/client issue, capture the exact action, expected vs actual behavior, character/job/level, map/NPC/boss/PQ involved, timestamp/time zone, reproduction frequency, and screenshot/video/log when useful.

For suspected duplication, authentication bypass, unauthorized GM/admin access, economy abuse, or another exploitable security defect, **do not publish detailed reproduction steps publicly while it is exploitable**. Preserve evidence and route it through staff/security handling.

Client logs/dumps may contain debugging context and should be submitted intentionally through an official support channel. Never include passwords, PIC/PIN values, launcher/session tokens, or private credentials.

## Maintenance rule

- Remove an entry only after the fix/decision is represented on canonical `master` and the needed production/runtime validation passes.
- Convert fixed critical/high defects into regression coverage when practical.
- Do not add inherited Cosmic/HeavenMS issues here unless they are verified against the current EverLeaf source/release.
- Do not use this file as a replacement roadmap; broad planned work belongs in `EVERLEAF_MASTER_CHECKLIST.md`.

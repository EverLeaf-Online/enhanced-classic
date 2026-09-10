# EverLeaf Known Issues

This is the maintained EverLeaf known-issues register. It is intentionally separate from `docs/archive/upstream/issues.txt`, which is inherited historical material and is **not** EverLeaf's current issue list.

The master development checklist remains authoritative for project-wide readiness. This file focuses on defects, user-visible limitations, and unresolved validation risks that operators/testers should know about now.

## Severity guide

- **Critical** — active risk of persistent corruption, compromise, or large-scale economy/account damage.
- **High** — meaningful abuse/security/gameplay risk or broad inability to play correctly.
- **Medium** — material defect/limitation with a workaround or narrower scope.
- **Low** — minor behavior, polish, or operational inconvenience.
- **Validation** — not yet a confirmed defect, but an area that still lacks enough runtime evidence for public-beta confidence.

## Fixed on canonical `master`, pending production/client deployment

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

### Medium — launcher-only and single-client policy needed fail-closed enforcement

**Status:** Source-hardened; managed launcher/client publication and runtime verification pending

EverLeaf policy is **launcher-only** and **one game client per machine at a time**. Players are not supposed to open `EverLeaf.exe` directly or run multiple EverLeaf clients simultaneously.

Canonical `master` now hardens the stock managed client/launcher path in several layers:

- the launcher checks for an existing `EverLeaf` process before repair and immediately before Play;
- the launcher also checks the native machine-wide client mutex `Global\EverLeafMS.Client.SingleInstance` and refuses a second launch;
- the native `dinput8.dll` bootstrap acquires that machine-wide mutex and keeps it open for the lifetime of the client, so a second stock client exits even if two launcher instances race;
- the `.everleaf-launch` handoff remains mandatory for the managed native client;
- launch-ticket consumption now opens the ticket exclusively with `FILE_FLAG_DELETE_ON_CLOSE`, preventing two client processes from consuming the same ticket concurrently;
- the native bootstrap enforces both launcher-ticket and single-client checks from the normal post-unpack hook and both dinput export entry paths;
- `ClientLaunchPolicyTests` and the manual `client-v2-integration-guard` protect the source contract.

This should be validated with the published managed launcher/client by testing: direct `EverLeaf.exe` launch rejection, normal launcher launch, opening a second launcher while the game is running, and a deliberate rapid/race second-launch attempt.

**Security boundary:** these controls enforce the policy for the EverLeaf-managed stock binaries. A player who can arbitrarily patch/replace their local executable or bootstrap DLL is outside what a purely client-side guard can make tamper-proof. If EverLeaf later requires cryptographically server-backed proof that an unmodified launcher authorized each login, that requires a server-validated launch-session protocol rather than pretending a local mutex/ticket alone is unbreakable.

### Low — richer Discord Rich Presence gameplay activity was gated on v83 contracts

**Status:** Source-fixed; managed client publication and runtime verification pending

The published client already provides EverLeaf-native basic Discord Rich Presence. Canonical `master` now adds richer gameplay activity after pinning the required GMS v83 contracts from the project-supplied `Angel.idb` and cross-checking them against independent v83 client work.

The source now:

- samples gameplay state from `CUserLocal::Update` on Maple's game thread rather than reading Maple objects from the Discord IPC worker;
- reads the character name, level, job code, and field ID through pinned v83 getters rather than guessed struct offsets;
- cross-checks `CUserLocal::GetFieldID()` against `CWvsContext::GetCurFieldID()` before publishing map activity;
- requires an active field/local-user/context state and fails closed to the existing generic EverLeaf activity during login, logout, transitions, pointer/layout failures, or field-ID disagreement;
- formats supported EverLeaf v83 jobs from the server's maintained `Job` IDs instead of importing post-v83 job IDs from external references;
- retains the existing local Discord named-pipe IPC implementation, with no Discord bot token, OAuth secret, Game SDK DLL, or database access.

The pinned v83 addresses used by this feature are source-build-specific and must not be carried to another client version without re-verification. Regression coverage now checks supported job labels/gameplay formatting in addition to the existing Discord IPC framing/acknowledgement tests, and the native Discord workflow contains source-contract markers for the verified addresses and fail-closed map cross-check.

Runtime closure is intentionally still pending until the batched client build/publish pass. Verify Discord behavior across login, character entry, level/job state, map changes, channel changes, logout, reconnect, and Discord-not-running/reconnect cases, and confirm stale character/map activity is cleared during transitions.

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

### Medium — account recovery is staff-queue based, not self-service reset

**Status:** Implemented request intake; manual resolution required

The public `/recover` form accepts a username or valid account email, deduplicates pending submissions within a day, and deliberately returns the same success response to prevent account enumeration. Requests enter the staff CMS queue with `pending`, `resolved`, or `rejected` status.

The current code does **not** implement an automated password-reset token/email flow. Staff must verify and resolve requests under the recovery procedure.

### Low — direct modern class-card/Evan creation UI is paused

**Status:** Deferred by design

The accepted Evan flow remains Beginner creation followed by the in-game NPC conversion path. The broader login/world/character-select redesign and direct modern class cards are deferred until the Kaentake review/Phase 2 decision.

## Public-beta validation risks

The following are not automatically confirmed bugs, but they remain known risk areas because full runtime coverage is incomplete. Completed checks are intentionally omitted from this active list.

### Boss and Party Quest lifecycle

**Status:** Validation required

Complete multi-client runs remain for major bosses/PQs, including prerequisite/entry behavior, leader loss, disconnect/rejoin, death/revive, timeout, stage/phase transitions, cleanup, lockouts, reward delivery, full-inventory behavior, and duplicate/replay resistance.

### Full class/combat parity

**Status:** Validation required

A systematic runtime matrix across Explorer, Cygnus, Aran, and Evan attacks, buffs, passives, summons, movement, status effects, formulas, and party interactions is still pending.

### Transaction/concurrency edge cases

**Status:** Validation required

Trade, storage, merchants, PlayerShop, Cash Shop transfer/re-entry, quest reward replay, drop/pickup races, and concurrent custom-currency operations still need broader multi-client/race testing.

### Clean-machine launcher/client behavior

**Status:** Validation required

Launcher self-update, damaged-file repair, interrupted-update rollback/retry, clean-machine installation, direct-EXE rejection, single-client enforcement, Alt+Enter/windowing transitions, crash/disconnect handling, and full channel switching still need final clean-player-machine regression coverage.

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

# EverLeaf event / minigame audit — 2026-09-06

This records the Git-backed status of EverLeaf event, PQ, transport, area-boss and minigame infrastructure after the global-content cleanup.

## Already complete before this pass

- Event scripts are loaded through `EventScriptManager` from `scripts/event` and evaluated by the channel event-script manager.
- `ScriptEvaluationTest` evaluates every event script in the Maven test suite.
- `tools/audit_event_manager_links.py` is a required-build gate for missing, empty and case-mismatched `getEventManager("Name")` targets.
- Boss/PQ lifecycle hardening already validates leaders/parties/expeditions, rolls back failed instance setup, releases failed lobbies, makes timer replacement bounded/idempotent, and preserves cleanup behavior.
- PQ Points persistence and clear-time integration exist.
- Known Romeo/Juliet and GPQ reactor handlers were restored by the world-content hardening work.
- The RPS minigame has its server implementation, packet handler/opcodes, NPC id and client WZ marker.

## This pass

`tools/audit_event_inventory.py` adds a release-facing classification gate for every `scripts/event/*.js` file. It:

- requires an active `init()` function for every event manager;
- re-checks literal external `getEventManager` targets;
- classifies fallback, scheduled/background, PQ/instance, referenced, seasonal-dormant and dormant/unreferenced scripts;
- reports dormant scripts instead of inventing entry points or enabling legacy content;
- rejects case-colliding event-manager names;
- protects seasonal scripts from silently acquiring unapproved `scheduleAtTimestamp` activation;
- explicitly protects the legacy `2xEvent.js` hard-coded timestamp scheduler from becoming active;
- verifies the structural RPS dependency set (`RockPaperScissor`, handler, opcodes, NPC id and WZ marker).

The audit is wired into `.github/workflows/run-build.yml`, so pull requests and release-line builds fail if these structural safety rules regress.

## Seasonal / inactive behavior

The historical timestamp code in `2xEvent.js` is inside a block comment, so it does not auto-schedule. The new gate fails if that timestamp scheduler is reactivated without an explicit policy change.

Dormant or unreferenced seasonal/PQ scripts remain report-only. Presence in `scripts/event` means the script is evaluated at startup; it does **not** mean the content is automatically opened to players. No dormant content is enabled by this pass.

## Runtime boundary

Static event/minigame integrity is now release-gated. These remain gameplay validation rather than missing implementation:

- full stage-by-stage playthrough of every intended PQ;
- disconnect/reconnect/leader-change behavior in a real client session;
- reward delivery with full inventories and repeated clear attempts;
- seasonal events if/when explicitly activated;
- visual/client behavior of RPS and other minigames.

No live event was enabled, no production schedule was changed, and no reward table was modified by this pass.

## Drop parity context

Mob/drop parity is already closed separately by `docs/COMMUNITY_MYSQL_PARITY_FINAL_2026-09-03.md`: all 187 newly placed live-map mobs have drop coverage, 201 validated source-backed item rows were added, nonpositive rows were reduced to zero, and the final live verification reported `COMMUNITY_MYSQL_PARITY_FINAL_OK`.

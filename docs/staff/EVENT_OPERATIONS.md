# EverLeaf Event Operations

This is the maintained staff runbook for operating joinable GM events and retained scripted/classic map events. It does **not** authorize dormant or seasonal scripts merely because they exist in the repository.

For command permissions, see [`GM_COMMANDS_AND_PERMISSIONS.md`](GM_COMMANDS_AND_PERMISSIONS.md). For incident/evidence handling, see [`OPERATIONS_AND_INCIDENTS.md`](OPERATIONS_AND_INCIDENTS.md).

## Event types

EverLeaf currently has two distinct staff-facing event concepts that should not be mixed casually:

1. **Channel join event** — `!startevent` creates an `Event` tied to the staff member's current map and broadcasts that players may use `@joinevent`. `!endevent` clears the channel event reference so no more players may join.
2. **Classic/current-map event state** — `!startmapevent` calls the current map's `startEvent(...)`; `!stopmapevent` clears that map's event-started flag.

A scripted EventManager/PQ/boss instance is a separate lifecycle again. Do not assume `!endevent` or `!stopmapevent` safely disposes an arbitrary EventManager instance.

## Before running an event

Confirm all of the following:

- the event is intentionally enabled/supported for the current release;
- the map and required scripts/assets exist in the current production baseline;
- reward rules are known and do not violate the no-P2W/economy policy;
- entry/exit/return maps are valid;
- the event will not interfere with a boss/PQ/event instance already using the channel/map;
- the expected participant count is reasonable for the map/server;
- staff know how the event ends and how stranded players are returned;
- reward replay/disconnect behavior has either been tested or the event is being run as a controlled test with no valuable rewards;
- a staff operator remains present until the event is closed/cleaned up.

Do not activate a dormant seasonal script directly on production as an experiment. Validate it first on staging/disposable QA.

## Starting a channel join event

1. Move the staff character to the intended event map.
2. Confirm the map is safe for incoming players and not an active boss/PQ instance.
3. Run:

```text
!startevent
```

Current source behavior creates a channel event using the current map and defaults to **50 players**, then broadcasts `@joinevent` instructions to the world.

### Known parameter limitation

The current `StartEventCommand` only parses a participant-limit argument when more than one parameter is supplied. A single numeric argument is therefore ignored and the default of 50 remains. Do not rely on `!startevent <limit>` until that source defect is fixed/tested; it is tracked in `docs/KNOWN_ISSUES.md`.

4. Confirm the broadcast appears.
5. Use a second/player client when practical to verify `@joinevent` enters the intended map.
6. Watch participant count/map state as players join.

## Closing entry

When the join period is over, run:

```text
!endevent
```

Current source clears the channel's active event reference and reports that no more players may join.

Important: this closes the **join gate**. It does not by itself prove that map state, rewards, timers, spawned mobs, or already-joined players were cleaned up. Continue through event completion/cleanup.

## Starting/stopping a classic map event

On a map that intentionally supports the classic map-event mechanism:

```text
!startmapevent
```

calls the current map's event-start routine using the staff character as the initiator.

To stop the map's event-started state:

```text
!stopmapevent
```

Do not use these commands on an arbitrary map merely because the commands execute. The map's own implementation determines what `startEvent` actually does, including spawns/timers/mechanics.

## Running the event

During the event, staff should monitor:

- player count and disconnected players;
- map ownership/instance boundaries;
- spawned mobs/reactors/NPCs;
- event timer behavior;
- stage/phase transitions;
- party/leader state if applicable;
- death/revive/return-map behavior;
- reward eligibility and inventory-full behavior;
- duplicate completion/reward attempts;
- channel stability and unusual lag/error logs.

Avoid using unrelated GM commands to "repair" a live event unless the recovery action is understood. Ad hoc warps, kills, quest completion, item grants, or map reloads can change the evidence and create additional state problems.

## Rewards

Event rewards must be deliberate, documented, and compatible with EverLeaf's economy rules.

Before enabling valuable rewards, validate:

- exact reward item/currency and quantity;
- account vs character scope;
- repeatability/cooldown;
- full-inventory handling;
- disconnect/reconnect handling;
- duplicate/retry behavior;
- trade/account-bound behavior;
- whether the reward introduces an uncontrolled Chaos/White Scroll, NX, Verdant Mark, PQ Point, meso, or best-in-slot faucet.

Do not compensate players with arbitrary `!item`, `!givenx`, `!givems`, `!givevp`, `!giverp`, stat, or rate commands without a documented remediation reason.

## Completing and cleaning up

An event is not complete until all affected state is accounted for.

1. Close further joins with `!endevent` if a channel join event was opened.
2. Stop the map event with `!stopmapevent` if the classic map-event mechanism was used and the event design requires it.
3. Let the intended script/EventManager cleanup run when applicable rather than bypassing it.
4. Confirm participants reached the intended exit/return map.
5. Confirm temporary mobs/reactors/timers/map state are gone or reset.
6. Confirm rewards were paid once and only once.
7. Confirm no player is stranded in an inaccessible instance/map.
8. Confirm a new event/PQ/boss instance can be created normally afterward when relevant.
9. Record any abnormal disconnect, duplicate reward, stuck state, or cleanup failure in the known-issues/QA workflow.

## Abort procedure

Abort when the event is corrupting persistent state, duplicating rewards, trapping players broadly, destabilizing the channel, or interacting with an exploit.

1. Stop accepting new participants.
2. Preserve relevant logs/timestamps before destructive cleanup when practical.
3. Stop the smallest affected event/map feature first.
4. Return stranded players only through a known-safe path.
5. If persistent economy/account state may be at risk, escalate under `OPERATIONS_AND_INCIDENTS.md` rather than continuing the event.
6. Do not restart the whole production server merely to hide event state unless a restart is actually required for safety.
7. If a server restart/rollback becomes necessary, follow `RECOVERY_AND_RESTORE.md`.

## Testing a new/returning event

Before making a dormant/seasonal/minigame event public, test at minimum:

- entry prerequisites;
- join capacity;
- leader/party changes;
- disconnect/rejoin;
- death/revive;
- timeout/failure;
- map/stage transitions;
- cleanup/disposal;
- reward once-only behavior;
- full inventory;
- duplicate/replay attempts;
- concurrent instances if supported;
- channel change/relog state;
- expected WZ/client assets;
- reward economy impact.

Use controlled QA accounts and non-production environments for exploit/reward testing.

## After-action record

For significant events or first-time/returning events, record:

- event name/type;
- date/time and channel;
- operator;
- participant count;
- reward configuration;
- abnormal disconnect/cleanup/reward behavior;
- whether the event can be safely repeated without code/content changes.

This record is especially important when an event exposed a bug that needs a regression test or when staff compensated players afterward.

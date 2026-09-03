# SoloMapling QA Integration

EverLeaf is integrating the existing [SoloMapling](https://github.com/MadaraGameDev/SoloMapling) artificial-player framework for automated gameplay QA rather than developing a separate bot framework.

## Upstream pin

- Repository: `MadaraGameDev/SoloMapling`
- Version: `v0.3`
- Commit: `47b61b5381118ebdc1064ddbd0b1c32f75778871`
- Runtime: Java 21
- Server lineage: Cosmic / HeavenMS-style v83

Pinning the upstream commit makes compatibility work reproducible and prevents an upstream update from silently changing EverLeaf QA behavior.

## EverLeaf integration branch

- Base: `release-dev`
- Work branch: `feature/solomapling-qa-integration`
- Draft PR: `#260`

The integration is intentionally separate from active WZ/client modernization work. Nothing in this branch is deployed to production automatically.

## Current milestone

The first controlled GCMove runtime slice is now integrated.

- all 29 pinned GCMove classes are present in Git on the feature branch
- EverLeaf-adapted GCMove files remain authoritative where host compatibility or QA policy differs
- the complete pinned upstream GCMove package compiles against EverLeaf in the dedicated compatibility workflow
- the compatibility workflow is read-only
- automatic SoloMapling population remains disabled
- the shared headless `BotClient` is initialized, but EnvironmentManager population startup is not
- one GM-owned synthetic QA bot can be created on world 0 / channel 1
- GM operators can exercise baseline movement, patrol, portal and combat smoke paths
- GM operators can hand the same bot to GCMove manually with `!qabot gcmove <x> <y>`
- `!qabot gcstop` tears down that bot's GCMove session
- `!qabot status` reports map, coordinates, GCMove ownership and fallback-patrol state

This milestone is compile/runtime-control readiness. It is not yet proof of live map-by-map GCMove behavior; that requires the controlled staging smoke sequence.

## Compatibility confirmed

EverLeaf and SoloMapling share the important foundation required for the framework:

- Java 21
- Maven
- MySQL
- `net.server.Server` entry point
- Cosmic/HeavenMS-derived server layout
- `client.Client` world/channel routing
- `client.Character` gameplay model
- map/NPC/quest/combat server architecture

The current EverLeaf `Client` API supports SoloMapling's headless-client overrides:

- `sendPacket(Packet)`
- `isLoggedIn()`
- `updateLoginState(int)`
- `disconnectSession()`
- `closeSession()`
- `checkIfIdle(IdleStateEvent)`
- `getLastPacket()`

## Integration strategy

Do not merge SoloMapling's entire Cosmic fork over EverLeaf. EverLeaf contains substantial server, persistence, content, security, class, economy, and production changes that must remain authoritative.

Instead:

1. Keep EverLeaf as the host engine.
2. Pin SoloMapling at v0.3.
3. Vendor framework/runtime files only where they are needed.
4. Port or adapt only the host hooks required by the framework.
5. Preserve EverLeaf safety, content and economy behavior when upstream host files differ.
6. Keep automatic bot population disabled until controlled QA/staging validation passes.
7. Add automated population only after the single-bot runtime is proven safe.

## EverLeaf-specific compatibility policy

Several upstream behaviors are deliberately adapted rather than copied verbatim:

- **Version filtering:** EverLeaf intentionally contains backported/newer content, so the staged SoloMapling version policy does not hide maps/NPCs simply because they are outside stock v83 assumptions.
- **Ambient social reactions:** disabled for deterministic QA bots; chat/emote behavior is not needed for the first testing milestone.
- **Logging:** SoloMapling messages route through EverLeaf logging instead of creating an unmanaged `BotLog.txt`.
- **Movement ownership:** GCMove and the simpler packet-path patrol harness are never allowed to drive the same QA bot concurrently.
- **Map transitions:** both movement engines are stopped before the manual portal smoke path changes maps.
- **Bot cleanup:** replacing/removing a QA bot tears down its scheduled fallback patrol and GCMove state first.
- **Automatic population:** `SPAWN_BOTS_ON_STARTUP` remains `false`, and `EnvironmentManager::environmentLoadStartup` is absent from server startup.

## Current manual QA surface

The GM4 `!qabot` command is intentionally limited to a single bot owned by the invoking GM on world 0 / channel 1.

Available actions:

- `!qabot spawn`
- `!qabot status`
- `!qabot nudge <dx>`
- `!qabot move <x> <y>`
- `!qabot patrol start`
- `!qabot patrol stop`
- `!qabot portal <id>`
- `!qabot strike [damage]`
- `!qabot gcmove <x> <y>`
- `!qabot gcstop`
- `!qabot remove`

The baseline move/patrol path remains useful as a control group when diagnosing GCMove behavior.

## Next controlled runtime sequence

The next milestone is live/staging proof, still with one manually created bot and no automatic population:

1. spawn one QA bot beside a GM
2. verify `!qabot status`
3. run short same-foothold GCMove targets
4. run slope and foothold-boundary targets
5. exercise jump/drop transitions
6. exercise rope/ladder traversal
7. stop/restart GCMove repeatedly and verify movement ownership cleanup
8. combine movement with `strike`
9. traverse a portal with GCMove stopped, then resume GCMove on the destination map
10. exercise a multi-map GCMove travel path only after same-map physics is stable
11. verify bot removal leaves no per-bot driver/travel/follow/fidget state behind
12. then expand to NPC, quest, grind, boss/PQ and persistence scenarios

## Deferred until QA core works

These SoloMapling systems are useful but are not required for the first EverLeaf testing milestone:

- automatic EnvironmentManager population
- Free Market population
- artificial economy
- casino/minigames
- ambient social chatter
- filler populations
- decorative server-population choreography

## Compatibility probe

`.github/workflows/solomapling-compatibility.yml` checks out the exact pinned upstream SoloMapling v0.3 GCMove package, overlays it into the CI workspace, restores EverLeaf's deterministic `BotPlayerReaction` policy, applies the same EverLeaf source transforms used by normal builds, and compiles the full GCMove package against the current host API.

The workflow has `contents: read`; it is verification-only and cannot mutate the branch.

## Safety rules

- Never enable bot auto-spawn directly on production before QA/staging validation.
- Do not let test bots write normal account login/session state.
- Keep QA bots out of player rankings and production economy metrics.
- Preserve EverLeaf host logic when an upstream Cosmic/SoloMapling implementation conflicts with current EverLeaf behavior.
- Port the minimum host hook necessary instead of replacing whole host files.
- Keep manual smoke controls GM-only and channel-constrained until runtime behavior is proven.
- Do not merge PR #260 to `release-dev` or deploy it to production solely because compilation is green; controlled runtime smoke is a separate gate.

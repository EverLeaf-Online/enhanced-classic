# SoloMapling QA Integration

EverLeaf is integrating the existing [SoloMapling](https://github.com/MadaraGameDev/SoloMapling) artificial-player framework for automated gameplay QA rather than developing a separate bot framework.

## Upstream pin

- Repository: `MadaraGameDev/SoloMapling`
- Version: `v0.3`
- Commit: `47b61b5`
- Runtime: Java 21
- Server lineage: Cosmic / HeavenMS-style v83

Pinning the upstream commit makes compatibility work reproducible and prevents an upstream update from silently changing EverLeaf QA behavior.

## EverLeaf integration branch

- Base: `release-dev`
- Work branch: `feature/solomapling-qa-integration`
- Initial PR: `#260`

The integration is intentionally separate from active WZ/client modernization work.

## Compatibility already confirmed

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

Do not merge SoloMapling's entire Cosmic fork over EverLeaf. EverLeaf contains substantial server, persistence, content, security, Evan, economy, and production changes that must remain authoritative.

Instead:

1. Keep EverLeaf as the host engine.
2. Consume the pinned upstream `soloMapling/` framework.
3. Port only the host hooks required by that framework.
4. Keep bot startup disabled until headless smoke tests pass.
5. Enable QA-focused bot types before optional population/economy/casino features.

## First integration slice

The first target is automated gameplay validation, not artificial population.

Priority order:

1. **Headless client foundation**
   - `client.BotClient`
   - no Netty socket
   - no account/session writes
   - safe packet sink

2. **Framework bootstrap**
   - initialize shared headless bot client after channels/maps are ready
   - bot spawning remains opt-in

3. **Movement/navigation**
   - movement packet bridge
   - foothold/rope traversal support
   - portal navigation
   - JGraphT/JGraphX pathfinding dependencies

4. **Combat**
   - bot attack driver
   - monster damage/death interaction
   - skill/buff support needed by training bots

5. **QA scenarios**
   - map/portal traversal
   - monster grinding
   - death/recovery
   - NPC interaction
   - quests
   - parties/PQs/bosses
   - persistence and reconnect tests

## Deferred until QA core works

These SoloMapling systems are useful but not required for the first EverLeaf testing milestone:

- Free Market population
- artificial economy
- casino/minigames
- ambient social chatter
- filler populations
- decorative server-population choreography

## Compatibility probe

`.github/workflows/solomapling-compatibility.yml` overlays the pinned upstream `soloMapling/` package onto EverLeaf in CI and compiles it against the current EverLeaf host API. The probe temporarily injects the upstream graph dependencies and records the compiler output.

The compiler failures are treated as the authoritative host-hook porting checklist. This avoids blindly copying old Cosmic engine changes into EverLeaf.

## Safety rules

- Never enable bot auto-spawn directly on production before QA/staging validation.
- Do not let test bots write normal account login/session state.
- Keep bot changes out of player rankings and production economy metrics when used for QA.
- Preserve EverLeaf host logic when an upstream Cosmic/SoloMapling implementation conflicts with current EverLeaf behavior.
- Port the minimum hook necessary instead of replacing whole host files.

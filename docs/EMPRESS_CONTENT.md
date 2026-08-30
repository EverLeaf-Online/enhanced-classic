# EverLeaf Empress / Gate to the Future

## Goal

Add the Gate to the Future, Future Henesys, Knight Stronghold, Chief Knight progression, and Fallen Cygnus encounter to EverLeaf as one coherent level-180+ content package without breaking the v83 client or bypassing progression.

## Player progression

1. Reach level 180.
2. Unlock Gate to the Future.
3. Progress through Future Henesys and Knight Stronghold.
4. Complete Chief Knight prerequisites.
5. Gain access to the Cygnus encounter.
6. Enter as an expedition/party encounter.
7. Clear the final Cygnus body for the top reward table.

Target group size: 3-12 players for the final encounter, subject to private alpha testing and class-balance review.

## Safety rules

- The complete content package is imported together; orphan boss maps are not allowed.
- Server XML and matching client WZ/.IMG nodes must agree.
- Newer-version maps/mobs must not be activated until animations, MobSkills, map assets, strings, BGM, effects, and portal references are verified.
- Stronghold field monsters and Chief Knights must be retuned for EverLeaf instead of copying later-version health/damage values blindly.
- The content must remain unavailable to normal players until the activation gate is explicitly enabled after private testing.

## Encounter design

The Empress encounter will use the `8850000-8850011` family from the selected package. `8850011` is the final Cygnus body and is the only body eligible for EverLeaf's top rare-scroll reward roll.

Required encounter behavior:

- fresh instance per expedition
- party/expedition ownership
- explicit start and timeout
- Chief Knight / summon phase handling
- final Cygnus phase
- safe cleanup on failure
- safe cleanup on timeout
- death handling
- disconnect handling
- re-entry policy consistent with EverLeaf's future reconnect-in-boss-runs system
- no duplicate reward claims
- weekly account-scoped top-reward lockout

## Reward policy

Keep the economy sources diversified while preventing multipart-boss abuse.

### Final Cygnus body (`8850011`)

- Chaos Scroll: eligible
- White Scroll: eligible, substantially rarer
- endgame/progression materials: eligible
- Empress-themed equipment: eligible after item compatibility audit

### Not eligible for Chaos/White

- Chief Knight bodies/variants
- Shinsoo
- summons
- Stronghold mobs
- Future Henesys mobs
- transition/phase bodies

This preserves the existing EverLeaf policy where Chaos/White can come from selected bosses, PQ rewards, and the shared rare Gachapon pool, while ordinary monsters cannot drop them.

## Balance targets

Current server baseline stays unchanged:

- EXP: 5x
- Mesos: 3x
- Drop: 2x
- Boss Drop: 2x
- Quest: 1x

The imported source gives multiple encounter bosses 2.1 billion HP. Those values are not suitable as-is for EverLeaf's planned level-180 bridge and must be replaced with alpha-tested values.

Initial design principle:

- Stronghold mobs should feel tougher than normal grinding mobs but remain practical for quest progression.
- Chief Knights should be meaningful mini-boss/phase targets rather than multi-billion-HP walls.
- Cygnus should sit above Horntail and below/around EverLeaf's later Pink Bean/endgame progression depending on private DPS testing.

## Required implementation

- selective server XML staging
- selective matching client asset staging
- Gate to the Future entry NPC/portal flow
- Stronghold prerequisite quest/state tracking
- `out_cygnusBackGarden` portal script
- `back_cygnus` portal script
- Empress event/expedition script
- spawn/phase controller
- account-scoped weekly clear/reward persistence
- final-body reward table
- item/drop compatibility audit
- MobSkill compatibility audit
- strings/UI/BGM/effect validation
- private runtime map-by-map test
- private boss-phase test

## Release boundary

Do not enable the content in production and do not publish a client patch/manifest containing the new assets without explicit approval after private validation.

# EverLeaf Empress / Gate to the Future Asset Inventory

Source reviewed: `wz.zip` server-side WZ XML dump supplied for the Gate to the Future / Future Henesys / Knight Stronghold / Cygnus content set.

## Community donor verification

The supplied community XML archive is now pinned as the server-side reference for this package:

- SHA-256: `fd9d788d2b658f5e91877faf9e55d0fd841c735afaab60a15e6bf203b8b3ceaa`
- archive entries: `44,281`
- selected Empress package server XML: `91` files (`42` maps, `34` mobs, `15` NPCs)

The matching community client archive was integrity-tested before extraction and contains all 17 expected WZ families. A full hash comparison against the current EverLeaf launcher payload found 6 byte-identical WZs and 11 differing WZs. The differing families include every major client family needed by this package (`Map.wz`, `Mob.wz`, `Npc.wz`, `Reactor.wz`, `String.wz`) plus supporting `Effect.wz` and `Sound.wz`. This confirms the community pack must remain a donor: the final EverLeaf client WZs are to be merged from the selected nodes, not replaced wholesale.

A staging-only GitHub/Oracle workflow now exports the first-wave donor families through MapleLib at the v83 patch format and performs the existing node-level donor diff. Nothing in this evidence step deploys or modifies the live server.

## Confirmed package scope

Treat the following as one atomic content package. Do not ship only the final boss maps.

- Gate to the Future
- Future Henesys
- Knight Stronghold
- Chief Knight progression
- Cygnus Garden / Empress encounter

## Required map XML

42 maps in `wz/Map.wz/Map/Map2/`:

`271000000`, `271000100`, `271000200`, `271000210`, `271000300`,
`271010000`, `271010001`, `271010100`, `271010200`, `271010300`, `271010301`, `271010400`, `271010500`,
`271020000`, `271020100`,
`271030000`, `271030010`, `271030100`, `271030101`, `271030102`, `271030200`, `271030201`, `271030202`, `271030203`, `271030204`, `271030205`, `271030300`, `271030310`, `271030320`, `271030400`, `271030410`, `271030500`, `271030510`, `271030520`, `271030530`, `271030540`, `271030600`,
`271040000`, `271040100`, `271040200`, `271040210`, `271040300`.

## Required field mobs

Maps directly reference these 22 field mobs:

- `8600000-8600006`
- `8610000-8610014`

The archive also contains the encounter mob family `8850000-8850011`, which must be imported with the Empress encounter because those mobs are encounter-script/summon driven rather than normal map spawns.

### Empress encounter IDs

- `8850000` Mihile
- `8850001` Oz
- `8850002` Irena
- `8850003` Eckhart
- `8850004` Hawkeye
- `8850005` Mihile variant
- `8850006` Oz variant
- `8850007` Irena variant
- `8850008` Eckhart variant
- `8850009` Hawkeye variant
- `8850010` Shinsoo
- `8850011` Cygnus — final reward-bearing body

The source XML gives the Chief Knights, Shinsoo, and Cygnus 2,100,000,000 HP. EverLeaf must not import those values unchanged. The encounter is intended as a level-180 progression bridge and must be retuned before activation.

## Required NPCs

15 NPC IDs are directly referenced by the map package:

`2142000`, `2142001`, `2142002`, `2142003`, `2142004`, `2142005`, `2142006`, `2142007`, `2142008`, `2142009`, `2142010`, `2143000`, `2143001`, `2143003`, `2143004`.

## Required map assets

### BGM

- `Bgm18/QueensGarden`
- `Bgm25/CygnusGarden`
- `Bgm25/destructionTown`
- `Bgm25/knightsStronghold`
- `Bgm25/timeGate`

### Tiles

- `allblackTile`
- `darkEreb`
- `destructionField`
- `destructionTown1`
- `destructionTown2`

### Objects

- `acc14`
- `connect`

### Backgrounds

- `darkEreb`
- `destructionTown`
- `fakeDoors`

## Required portal scripts

The selected maps contain three scripted portal uses but only two unique scripts need to be authored/imported:

- `out_cygnusBackGarden`
  - used by `271040200`
  - used by `271040210`
- `back_cygnus`
  - used by `271040300`

Do not replace these with unconditional map warps; the scripts should enforce the intended encounter/exit flow.

## Reward policy

EverLeaf policy for this package:

- Chaos Scroll and White Scroll may only roll from the final Empress body (`8850011`).
- White Scroll must be substantially rarer than Chaos Scroll.
- No Chaos/White rolls from Chief Knights, Shinsoo, summons, Stronghold field mobs, or transition bodies.
- Existing normal-boss, PQ, and shared rare-Gachapon sources remain valid.
- No paid/VIP/vote-point combat advantage is introduced by this content.

## Activation rule

This package remains disabled until all required server XML and matching client assets are staged, the encounter scripts are complete, unsupported MobSkill behavior has been reviewed, the final selected asset manifest is frozen, and private runtime tests pass.

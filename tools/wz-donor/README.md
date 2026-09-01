# EverLeaf WZ donor pipeline

This directory contains the tooling for comparing newer MapleStory WZ exports against EverLeaf's canonical GMS v83 data.

## Safety model

- `release-dev/wz/` is the canonical server-side exported v83 baseline.
- Newer WZ sets are **donors**, never drop-in replacements.
- Do not commit proprietary raw `.wz` archives to this repository.
- Export donor WZ data to XML outside the repo or under a gitignored local workspace.
- Review client/server dependencies before importing any result.
- Start with content that is mostly data-driven (maps, mobs, NPCs, equipment, items, reactors) before packet- or UI-dependent systems.

## Donor order

1. GMS v95
2. GMS v117.2
3. TMS v120
4. GMS v167
5. GMS v213.2
6. selective current GMS content

The first controlled donor is **GMS v95** because it is the closest useful newer GMS generation to v83.

## Donor acquisition

The repository deliberately does not redistribute raw Nexon WZ archives.

For GMS v95, use a legitimately obtained v95 client and export its WZ files with a reader/editor that supports the old GMS format. HaSuite/HaRepacker is a maintained option with an explicit focus on GMS v95 and lower. Kinoko is also a useful v95 structural reference: it expects local `Character.wz`, `Item.wz`, `Skill.wz`, `Morph.wz`, `Map.wz`, `Mob.wz`, `Npc.wz`, `Reactor.wz`, `Quest.wz`, `String.wz`, and `Etc.wz` files rather than distributing them.

Useful public references:

- HaSuite / HaRepacker: https://github.com/iw2d/HaSuite
- Kinoko v95 server/reference: https://github.com/iw2d/kinoko
- MapleStoryUnity WZ archive index: https://github.com/MapleStoryUnity/wzData

The MapleStoryUnity archive currently indexes GMS v62/v83 and TMS v113/v119/v120, so **TMS v120 is a concrete public donor fallback** after the v95 pass.

## Expected donor layout

The diff tool accepts an exported XML tree with the same top-level shape as the server `wz/` directory:

```text
/path/to/gms-v95-export/
  Character.wz/
  Item.wz/
  Map.wz/
  Mob.wz/
  Npc.wz/
  Quest.wz/
  Reactor.wz/
  Skill.wz/
```

The comparison layer consumes exported XML rather than binding EverLeaf to one WZ editor.

## Run

From the repository root:

```bash
python3 tools/wz-donor/wz_diff.py \
  --baseline wz \
  --donor /path/to/gms-v95-export \
  --donor-id gms-v95 \
  --output tools/output/wz-gms-v95-diff.json
```

The tool is read-only. It produces:

- baseline ID counts
- donor ID counts
- IDs present only in the donor
- ID collisions with v83
- collisions whose underlying XML differs
- source paths for new entries
- conservative cross-content references from donor-new entries
- missing high-confidence dependencies

Current categories:

- maps
- mobs
- NPCs
- items
- equipment
- reactors
- quests
- skills

### Dependency scope

Dependency extraction intentionally under-reports instead of guessing. It currently recognizes high-confidence direct property names plus classic map structures such as:

- portal target maps (`portal/*/tm`)
- map life mob IDs (`type=m`)
- map life NPC IDs (`type=n`)
- map life reactor IDs (`type=r`)
- explicit map/mob/NPC/item/reactor/skill reference properties

A zero-missing-dependency report is therefore **not** proof that an import is complete. Visual assets, scripts, special client behavior, sounds, strings, footholds, tiles, objects, backgrounds, and packet-dependent mechanics still require review.

## Tests

```bash
python3 tools/wz-donor/test_wz_diff.py
```

The PR CI runs these regression checks automatically whenever the donor tooling changes.

## Import gate

A reported `newId` is **not automatically safe**. Before importing it, check at minimum:

1. client asset dependencies (Map/Tile/Obj/Back/Effect/Sound/String/etc.)
2. referenced mob/NPC/reactor/item/map IDs
3. script requirements
4. quest requirements
5. server packet/field compatibility
6. v83 parser assumptions
7. ID collisions across EverLeaf custom content
8. client/server XML parity after the final WZ edit

## Planned stages

- richer dependency extraction and missing-reference reports
- compatibility rules by WZ family/version
- per-content import manifests
- deterministic client/server parity checks
- a staging-only import command that copies only explicitly approved content

No automatic import of donor content is enabled.

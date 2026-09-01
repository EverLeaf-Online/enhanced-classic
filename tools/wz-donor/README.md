# EverLeaf WZ donor pipeline

This directory contains the first-stage tooling for comparing newer MapleStory WZ exports against EverLeaf's canonical GMS v83 data.

## Safety model

- `release-dev/wz/` is the canonical server-side exported v83 baseline.
- Newer WZ sets are **donors**, never drop-in replacements.
- Do not commit proprietary raw `.wz` archives to this repository.
- Export donor WZ data to XML outside the repo or under a gitignored local workspace.
- Review client/server dependencies before importing any result.
- Start with content that is mostly data-driven (maps, mobs, NPCs, equipment, items, reactors) before packet- or UI-dependent systems.

## First target

The first controlled donor is **GMS v95**. Later donors are tracked in `donors.json`.

Recommended order:

1. GMS v95
2. GMS v117.2
3. TMS v120
4. GMS v167
5. GMS v213.2
6. selective current GMS content

## Expected donor layout

The diff tool accepts an exported XML tree with the same top-level shape as the server `wz/` directory, for example:

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

The exact source WZ reader/repacker can vary; the comparison layer intentionally consumes exported XML rather than binding EverLeaf to one WZ editor.

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

Current categories:

- maps
- mobs
- NPCs
- items
- equipment
- reactors
- quests
- skills

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

## Next stages

The intended follow-up layers are:

- dependency extraction and missing-reference reports
- compatibility rules by WZ family/version
- per-content import manifests
- deterministic client/server parity checks
- a staging-only import command that copies only explicitly approved content

No automatic import is enabled in v1.

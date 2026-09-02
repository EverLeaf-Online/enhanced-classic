# EverLeaf WZ donor pipeline

This directory contains review-first tooling for comparing newer MapleStory WZ exports against EverLeaf's canonical GMS v83 data.

## Safety model

- `release-dev/wz/` is the canonical server-side exported v83 baseline.
- Newer WZ sets are **donors**, never drop-in replacements.
- Do not commit proprietary raw `.wz` archives to this repository.
- Raw donor files and exported donor archives belong under `/opt/everleaf/private/wz-donors/` on Oracle or another private workspace.
- Review client/server dependencies before importing any result.
- Start with mostly data-driven content before packet- or UI-dependent systems.

## First target: GMS v95.4

The primary v95 source is the preserved SourceForge `MapleStory Files v.95` collection. It exposes individual WZ files, so EverLeaf stages only the useful donor families rather than the whole client.

`.github/workflows/stage-gms-v95-donor.yml` stages these privately on Oracle:

- Character.wz
- Item.wz
- Map.wz
- Mob.wz
- Npc.wz
- Quest.wz
- Reactor.wz
- Skill.wz
- String.wz
- Etc.wz

The workflow validates minimum file sizes and records SHA-256 hashes, byte sizes, version and provenance. It does not deploy or modify the game server.

Recommended donor order:

1. GMS v95.4
2. GMS v117.2
3. TMS v120
4. GMS v167
5. GMS v213.2
6. selective current GMS content

## Exporting raw WZ to XML

The comparison layer consumes XML rather than binding EverLeaf to one editor. For v95, maintained options include HaSuite/HaRepacker (focused on GMS v95 and below) and WzComparerR2. WzComparerR2 also has Lua batch-dump scripts available publicly. Export fidelity must be checked before using an export as a donor source; do not assume every generic XML exporter preserves every WZ node type correctly.

Place the validated export in this shape:

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

Package the completed XML export as `/opt/everleaf/private/wz-donors/gms-v95.zip` for the Oracle-backed analysis workflow.

## Run locally

From the repository root:

```bash
python3 tools/wz-donor/wz_diff.py \
  --baseline wz \
  --donor /path/to/gms-v95-export \
  --donor-id gms-v95 \
  --output tools/output/wz-gms-v95-diff.json

python3 tools/wz-donor/build_import_manifest.py \
  tools/output/wz-gms-v95-diff.json \
  --output tools/output/wz-gms-v95-import-manifest.json
```

The diff tool is read-only. It reports:

- baseline and donor ID counts
- donor-new IDs
- v83 ID collisions
- content-different collisions
- source paths for donor-new entries
- high-confidence map life/portal dependencies
- missing referenced mobs, NPCs, reactors and maps

Current categories:

- maps
- mobs
- NPCs
- items
- equipment
- reactors
- quests
- skills

## Oracle analysis workflow

`.github/workflows/analyze-wz-donor.yml` accepts a private exported donor ZIP from `/opt/everleaf/private/wz-donors/`, compares it with `wz/`, and uploads two temporary GitHub Actions artifacts:

1. the full donor delta report
2. a disabled-by-default import manifest

The import manifest ranks candidates as low, medium, high or blocked. Every candidate starts with `approved=false`; missing high-confidence dependencies force `blocked`.

## Import gate

A reported donor-new ID is **not automatically safe**. Before approval, check at minimum:

1. client asset dependencies (Map/Tile/Obj/Back/Effect/Sound/String/etc.)
2. referenced mob/NPC/reactor/item/map IDs
3. script requirements
4. quest requirements
5. server packet/field compatibility
6. v83 parser assumptions
7. ID collisions across EverLeaf custom content
8. client/server XML parity after the final WZ edit

## Current limits

Dependency extraction is intentionally conservative and under-reports rather than guessing. Image links, arbitrary script logic, modern packet requirements and newer WZ schema semantics still require explicit review.

No automatic WZ import is enabled. A future staging importer must consume only explicitly approved manifest entries and must never write directly to the canonical baseline without a reviewable patch/package.

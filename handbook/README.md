# EverLeaf Handbook Reference Data

The `handbook/` directory is retained at its existing path because server/admin tooling may use these files as lookup/reference data. It is **not** the maintained EverLeaf documentation set and should not be used as a source of current production policy or feature status.

Use [`../docs/README.md`](../docs/README.md) for maintained documentation and [`../docs/EVERLEAF_MASTER_CHECKLIST.md`](../docs/EVERLEAF_MASTER_CHECKLIST.md) for authoritative project status.

## What is here

Most files are large lookup tables for MapleStory IDs and descriptions, including maps, mobs, NPCs, quests, items, jobs, pets, equipment, and related data. They are useful when resolving IDs or supporting legacy `!id`/handbook-style tooling.

`Commands.txt` is also legacy/reference material. Its command list may include inherited, retired, renamed, disabled, donor-only, or policy-incompatible commands. In particular, labels such as "Donator Commands" must **not** be interpreted as current EverLeaf monetization policy. EverLeaf's maintained policy is no pay-to-win.

## Rules

- Do not rewrite these tables into narrative documentation.
- Do not move or rename files casually; runtime/admin lookup code may depend on their paths.
- Do not infer current command availability or permissions from `Commands.txt`; verify against current source/configuration.
- Do not infer current game balance, content status, or monetization policy from handbook text.
- Add maintained explanations under `docs/` and leave this directory focused on reference data.

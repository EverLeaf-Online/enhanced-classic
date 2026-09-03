# EverLeaf Live Evan Skill Equivalence Audit — 2026-09-03

This report records direct scans of the current live Community-exported `Skill.wz` and `String.wz` XML on the Oracle server against the 43 Evan skill IDs expected by EverLeaf's server implementation.

## Result

The live Community `Skill.wz` XML contains **0 of the 43 expected Evan skill IDs**.

The preserved pre-wholesale EverLeaf baseline contains **all 43 of 43** expected IDs.

A first pass found no alternate records using the Evan job prefixes `2001`, `2200`, `2210`–`2218`.

A second, broader pass then searched the entire live Community `String.wz` by exact and fuzzy skill display name and cross-checked every matching ID against actual live `Skill.wz` records, without assuming any Evan-style prefix.

### What the broad alternate-ID scan found

Some Evan skill names also exist on unrelated/shared skills under other class IDs. Examples:

- `Teleport` matches existing mage/Cygnus records such as `2101002`, `2201002`, `2301001`, `12101003`, and GM/test variants.
- `Magic Guard` matches `2001002` and `12001001`.
- `Elemental Reset` matches `12101005`.
- `Slow` matches mage/Cygnus records such as `2101003`, `2201003`, `12101001`.
- `Maple Warrior` matches normal fourth-job variants across many classes.
- `Hero's Will` matches normal fourth-job variants across many classes.
- Beginner/shared names such as `Blessing of the Fairy`, `Three Snails`, `Recovery`, `Nimble Feet`, `Legendary Spirit`, `Monster Rider`, `Echo of Hero`, `Jump Down`, `Maker`, `Bamboo Thrust`, and `Invincible Barrier` also appear under existing non-Evan beginner/job IDs.

These are **name collisions/shared implementations, not replacement Evan records**. They do not provide an Evan job skill set because they belong to other jobs and IDs.

More importantly, the Evan-specific skills have no matching live Community skill record under another ID. No viable alternate skill IDs were found for the core Evan set including:

- Dragon Soul
- Magic Missile
- Fire Circle
- Lightning Bolt
- Ice Breath
- Magic Flare
- Magic Shield
- Critical Magic
- Dragon Thrust
- Magic Booster
- Magic Amplification
- Fire Breath
- Killer Wings
- Magic Resistance
- Dragon Fury
- Earthquake
- Phantom Imprint
- Recovery Aura
- Magic Mastery
- Illusion
- Flame Wheel
- Blessing of the Onyx
- Dark Fog
- Soul Stone

Fuzzy-name hits such as equipment named `Dragon's Soul` or `Dragon's Fury`, and an unrelated string entry named `Blaze`, were cross-checked and had no corresponding replacement Evan `Skill.wz` record.

Therefore the Community pack is **not simply using a different complete Evan ID scheme**. The Evan-specific Skill.wz data really is absent and must be merged back if EverLeaf is to retain Evan.

## Expected Evan skill IDs

`20010012`, `20011000`, `20011001`, `20011002`, `20011003`, `20011004`, `20011005`, `20011006`, `20011007`, `20011009`, `20011010`, `20011011`, `22000000`, `22001001`, `22101000`, `22101001`, `22111000`, `22111001`, `22121000`, `22121001`, `22131000`, `22131001`, `22140000`, `22141001`, `22141002`, `22141003`, `22150000`, `22151001`, `22151002`, `22151003`, `22160000`, `22161001`, `22161002`, `22161003`, `22170001`, `22171000`, `22171002`, `22171003`, `22171004`, `22181000`, `22181001`, `22181002`, `22181003`.

## Provenance

- Audit workflow: `.github/workflows/audit-live-evan-skill-equivalence.yml`
- Initial exact-ID run: `33709793980`
- Initial artifact ID: `9876507328`
- Full alternate-ID/name scan run: `33710455833`
- Full scan workflow commit: `ffb8647c2894c21ce9b9a82a9a805c7b3d2db58e`
- Full scan artifact ID: `9876728813`
- Full scan artifact ZIP SHA256: `632515a44b167616584d1f9bd52d49fc702b3482479d30ac0bfcaa59dc0aefb5`

## Recommended remediation

Keep the Community WZ as the base. Merge the preserved EverLeaf Evan skill groups/records back into the Community-based `Skill.wz`, regenerate the corresponding server XML, and rerun the Evan release audit plus real-client skill tests. Shared non-Evan records with the same display names should not be substituted for Evan IDs.

# EverLeaf Live Evan Skill Equivalence Audit — 2026-09-03

This report records the discovery, alternate-ID investigation, repair, and live verification of the Evan `Skill.wz` regression introduced by the wholesale Community WZ deployment.

## Final status — FIXED LIVE

The Community donor did not contain EverLeaf's Evan skill set under a different complete ID scheme. The 43 Evan IDs expected by the server were absent from the Community `Skill.wz`, while the preserved pre-wholesale EverLeaf baseline contained all 43.

EverLeaf now keeps the Community `Skill.wz` as its base and merges back only the preserved Evan groups:

- `2001.img`
- `2200.img`
- `2210.img`
- `2211.img`
- `2212.img`
- `2213.img`
- `2214.img`
- `2215.img`
- `2216.img`
- `2217.img`
- `2218.img`

The matching 11 server XML group files were restored alongside the rebuilt client `Skill.wz`.

### Verified live result

- **43/43 expected Evan skill IDs are present in the live server Skill XML.**
- **11/11 preserved Evan client Skill.wz groups were merged into the Community-based client Skill.wz.**
- Merged client `Skill.wz` SHA256: `04ef42e239a9bc7ac47ab75b3bac5ce028b68506772977444871d63ed9d70192`.
- Patch manifest regenerated successfully: **36/36 managed files**.
- `everleaf.service` verified active after restart.
- Port `8484` verified listening.
- Targeted rollback scratch was removed after successful verification.
- No duplicate 44,225-file server XML tree was created for the successful repair; only the 11 missing Skill XML groups were installed.

Successful live repair workflow:

- Run: `33711412416`
- Workflow commit: `fd6d6c925e7de257556186c817feca70f9f53c68`
- Final marker: `EVAN_FIX_FINAL_VERIFICATION_OK CLIENT_MERGE=11 SERVER_SKILLS=43 SERVICE=active PORT=8484`
- Deployment marker: `EVAN_SKILL_REGRESSION_FIXED_LIVE COUNT=43`

## Original regression

Immediately after the wholesale Community WZ deployment, the live Community `Skill.wz` XML contained **0 of the 43 expected Evan skill IDs**. The preserved pre-wholesale EverLeaf baseline contained **all 43 of 43** expected IDs.

A first pass found no alternate records using the Evan job prefixes `2001`, `2200`, `2210`–`2218`.

A second, broader pass searched the entire live Community `String.wz` by exact and fuzzy skill display name and cross-checked matching IDs against actual `Skill.wz` records without assuming an Evan-style prefix.

### Alternate-ID investigation

Some Evan skill names also existed on unrelated/shared skills under other class IDs. Examples included:

- `Teleport` on mage/Cygnus records such as `2101002`, `2201002`, `2301001`, `12101003`.
- `Magic Guard` on `2001002` and `12001001`.
- `Elemental Reset` on `12101005`.
- `Slow` on mage/Cygnus records such as `2101003`, `2201003`, `12101001`.
- `Maple Warrior` and `Hero's Will` on normal fourth-job variants across multiple classes.
- Beginner/shared skill names on non-Evan beginner/job IDs.

These were name collisions/shared implementations rather than replacement Evan records. Core Evan-specific skills such as Dragon Soul, Magic Missile, Fire Circle, Ice Breath, Magic Flare, Dragon Thrust, Fire Breath, Killer Wings, Dragon Fury, Earthquake, Phantom Imprint, Flame Wheel, Blessing of the Onyx, Dark Fog, and Soul Stone had no usable Community alternate skill records.

Therefore no server-side ID remap was performed. The preserved Evan data was restored instead.

## Expected Evan skill IDs

`20010012`, `20011000`, `20011001`, `20011002`, `20011003`, `20011004`, `20011005`, `20011006`, `20011007`, `20011009`, `20011010`, `20011011`, `22000000`, `22001001`, `22101000`, `22101001`, `22111000`, `22111001`, `22121000`, `22121001`, `22131000`, `22131001`, `22140000`, `22141001`, `22141002`, `22141003`, `22150000`, `22151001`, `22151002`, `22151003`, `22160000`, `22161001`, `22161002`, `22161003`, `22170001`, `22171000`, `22171002`, `22171003`, `22171004`, `22181000`, `22181001`, `22181002`, `22181003`.

## Audit provenance

- Initial exact-ID audit run: `33709793980`
- Initial artifact ID: `9876507328`
- Full alternate-ID/name scan run: `33710455833`
- Full scan artifact ID: `9876728813`
- Full scan artifact ZIP SHA256: `632515a44b167616584d1f9bd52d49fc702b3482479d30ac0bfcaa59dc0aefb5`
- Successful live repair run: `33711412416`

## Remaining validation

The client/server data regression itself is fixed and verified live. A real Evan character should still be used to exercise the restored skill animations and runtime behavior across the advancement stages; that is gameplay validation rather than missing-data remediation.

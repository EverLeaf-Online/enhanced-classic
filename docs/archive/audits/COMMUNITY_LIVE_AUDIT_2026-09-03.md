# EverLeaf Live Community Content / Economy Audit — 2026-09-03

Permanent evidence-backed report for the live Oracle server after the wholesale Community WZ + freshly exported XML deployment.

## Live baseline

- 17 Community donor WZs are live plus EverLeaf's custom `EverLeaf_UI.wz` overlay: **18 WZ files total**.
- Fresh server XML generated from the Community donor is live: **44,225 XML files**.
- Pre-wholesale rollback snapshot remains at `/opt/everleaf/backups/community-wholesale-test/20260903T005959Z`.
- Live release tree observed by the audit: `/opt/everleaf/releases/solomapling-live-smoke-f8bd03da7ee47b21c5dd01450c560949710497ad-33698055620-1`.
- `271000000` Future Henesys was independently confirmed to load in the real client.

# 1. Complete Community inventory

The live Community XML tree contains **44,225** files versus **22,191** in the preserved pre-wholesale XML baseline, a net increase of **22,034 XML files**.

| Family | Live XML | Baseline XML | Delta |
| --- | ---: | ---: | ---: |
| Base.wz | 3 | 3 | 0 |
| Character.wz | 25,744 | 7,207 | **+18,537** |
| Effect.wz | 17 | 17 | 0 |
| Etc.wz | 24 | 24 | 0 |
| Item.wz | 934 | 155 | **+779** |
| Map.wz | 6,417 | 5,609 | **+808** |
| Mob.wz | 2,091 | 1,568 | **+523** |
| Morph.wz | 42 | 42 | 0 |
| Npc.wz | 8,346 | 6,962 | **+1,384** |
| Quest.wz | 6 | 6 | 0 |
| Reactor.wz | 426 | 421 | **+5** |
| Skill.wz | 76 | 87 | **-11** |
| Sound.wz | 53 | 44 | **+9** |
| String.wz | 20 | 20 | 0 |
| TamingMob.wz | 7 | 7 | 0 |
| UI.wz | 19 | 19 | 0 |

A complete machine-readable ID inventory is now saved, not only samples. The successful full export is run **`33709146408`**, artifact **`9876332531`**, SHA256 `1f9c03af3272ac7e818747b80bc1fbbd55dea4d1c79ada08127577835f0abd1f`. It contains `community-unlocked-ids.csv` plus `summary.json` and records every added/removed ID in the audited behavior families, explicit source-reference status, dedicated NPC-script status, and map exposure for new mobs/NPCs.

## Behavior-family ID delta

| Family | Live IDs | Baseline IDs | Added | Removed |
| --- | ---: | ---: | ---: | ---: |
| Map.wz | 5,841 | 5,262 | **579** | 0 |
| Mob.wz | 2,091 | 1,568 | **523** | 0 |
| Npc.wz | 8,346 | 6,962 | **1,384** | 0 |
| Item.wz | 13,215 | 6,195 | **7,021** | **1** |
| Character.wz | 26,531 | 7,248 | **19,283** | 0 |
| Skill.wz | 26 filename groups | 37 | 0 | **11** |
| Reactor.wz | 426 | 421 | **5** | 0 |

Quest.wz uses a grouped serializer shape and has no filename-ID delta in the final complete inventory; the earlier grouped-content pass found 2,826 numeric quest IDs on both sides.

## Newly exposed content that is actually map-referenced

This is important because it separates dormant donor assets from content already wired into live map XML:

- New Community mobs total: **523**
- New Community mobs referenced by live maps: **187**
- New Community NPCs total: **1,384**
- New Community NPCs referenced by live maps: **350**

Examples include:

- Future Henesys mobs `8600000`–`8600006` on `271000xxx` maps.
- `8610000`–`8610014` across `271030xxx` maps.
- `821xxxx` mobs on `211060xxx` content.
- `8220016`–`8220021` on `272000xxx` / `272020xxx` maps.
- `862xxxx` mobs on `2730xxxxx` maps.
- `8641xxx` / `8642xxx` / `8643xxx` mobs on `45000xxxx` maps.
- Future Henesys NPC family `2142xxx` / `2143xxx` is directly placed in `271000xxx` maps.

This means a significant part of the newly unlocked content is not merely unused archive data: the new IDs are already referenced by live Community map XML and require runtime/server-behavior classification.

# 2. Community data without obvious server behavior

The initial source-reference pass found the following among newly added IDs:

- Maps: 579 added; 77 had explicit numeric Java/JS/SQL/Python references, 502 did not.
- Mobs: 523 added; 14 had explicit numeric references, 509 did not.
- NPCs: 1,384 added; 62 had explicit numeric references, 1,322 did not.
- Items: 7,021 added; 33 had explicit numeric references, 6,988 did not.
- Character/equipment IDs: 19,283 added; 215 had explicit numeric references, 19,068 did not.
- Reactors: 5 added; none had explicit numeric source references.

No explicit numeric source reference is a **triage signal, not proof of failure**. Normal mobs, maps, equips, consumables and decorative NPCs can be data-driven. The complete CSV preserves the exact list for follow-up implementation/runtime testing.

## NPC script coverage

The 1,384 newly added NPC IDs had **0 same-ID `scripts/npc/<id>.js` files** in the current source snapshot. This does not imply all are broken; decorative NPCs and generic interactions may not need dedicated scripts. The 350 newly added NPC IDs already placed on live maps are the highest-priority interaction classification set.

## Skill regression — confirmed

The Community Skill.wz/XML is **not a strict superset** of the pre-wholesale EverLeaf baseline. These baseline skill/job group files are present in the rollback XML and absent in the live Community XML:

- `2001`
- `2200`
- `2210`
- `2211`
- `2212`
- `2213`
- `2214`
- `2215`
- `2216`
- `2217`
- `2218`

The `2200` / `2210`–`2218` set directly overlaps EverLeaf's Evan work. These should be treated as a real wholesale-parity regression until restored/merged or proven unnecessary.

## Missing baseline item — confirmed

Baseline item ID **`2100904`** exists in the preserved baseline under `Item.wz/Consume/0210.img.xml` and is absent from the live Community Item XML. It needs classification/restoration if still required by EverLeaf gameplay.

## New reactors requiring classification

- `2401100`
- `2401200`
- `5411001`
- `9990000`
- `9990001`

These need passive/decorative versus action-bearing classification.

# 3. Full drops / economy validation

## Live economy table sizes

| Table | Rows |
| --- | ---: |
| `drop_data` | **22,319** |
| `drop_data_global` | **4** |
| `reactordrops` | **1,116** |
| `shops` | **110** |
| `shopitems` | **3,795** |
| `everleaf_encounter_weekly_reward` | 0 |
| `everleaf_nx_rewards` | 10 |
| `everleaf_vote_reward_ledger` | 0 |
| `everleaf_vote_rewards` | 8 |

## Normal drop integrity

- Invalid quantity ranges: **0**.
- Duplicate `(dropperid,itemid,questid)` groups: **0**.
- Five rows have `chance = 0`; all five are the same item ID `2050099` from different mobs:
  - dropper `3210200`
  - dropper `3210201`
  - dropper `6130100`
  - dropper `9420511`
  - dropper `9500125`

These five rows are disabled/non-dropping under the current chance value and are now exactly identified for policy cleanup rather than remaining an unknown count.

## Global drops — exact live set

Only four rows exist:

- `4031865` ×1 — 100 NX Coupon — chance **400/999999**
- `4031866` ×1 — 250 NX Coupon — chance **100/999999**
- `4001126` ×1–2 — Maple Leaves — chance **8000/999999**
- `4001006` ×1 — Flaming Feather — chance **10000/999999**

There are **no global rows** for:

- Chaos Scroll 60% `2049100`
- White Scroll `2340000`

So ordinary global Chaos/White removal is verified in the live DB.

## Reactor-drop duplicates — exactly identified

There are **28 duplicate `(reactorid,itemid,questid)` groups**. They are concentrated in a small set of reactors rather than scattered randomly:

- Reactor `2512001`: six item groups duplicated four times each, all chance 1.
- Reactors `6702003` through `6702012`: repeated `2000005` and `4020007` pairs, generally duplicated twice at chance 5.
- Reactors `6802000` and `6802001`: item `2022181` duplicated twice at chance 3.

These look like authored repeated weighting/drop slots, but because duplicates can alter effective probability or quantity they remain a deliberate-review item rather than being automatically deleted.

## Shop duplicates — exactly identified

All **19 duplicate `(shopid,itemid)` groups** are concentrated in **shop `1337`, NPC `11000`**. Each duplicate pair has the same price (`1`) and pitch (`0`) but appears in two different position ranges. The affected items are scroll IDs such as `2040007`, `2040506`, `2040710`, `2040711`, `2040806`, and weapon scrolls `2043003` through `2044703`.

This strongly indicates one duplicated block of shop inventory, not 19 unrelated shop-data defects. It should be classified/fixed as one shop-content issue if shop 1337 is player-accessible.

## Reward uniqueness / anti-double-claim schema

Verified live unique constraints include:

- `everleaf_encounter_weekly_reward`: primary `(account_id, encounter_id, week_start_utc)` and unique `attempt_id`.
- `everleaf_vote_reward_ledger`: unique `(account_id, provider, vote_date_utc)`.
- `everleaf_vote_rewards`: unique `(provider, external_vote_id)`.

## Economy/reward source audits

`tools/audit_reward_sources.py` passes its invariants:

- Global Gachapon: 31 common IDs, 8 uncommon, 4 rare.
- Chaos Scroll and White Scroll remain intentionally available through the rare Gachapon pool.
- No local Gachapon adds another Chaos/White roll.
- 13 Gachapon classes / 1,683 numeric reward slots inventoried.
- 16 duplicate local Gachapon reward IDs remain review items.
- Boss/fishing/Boss Rush rare-scroll policy checks pass.

Current configured rates are **10x EXP / 10x meso / 10x drop / 10x boss drop / 5x quest**. The existing economy audit flags the four 10x values only because its old pre-alpha target bands are lower. That is a policy mismatch, not a runtime failure; either the rates need changing or the stale audit bands need updating once the intended production rates are confirmed.

A standalone raw-checkout `audit_items_equipment.py` run reports a missing `EquipmentRequirements` import, but the normal build pipeline applies `apply_equipment_requirement_fixes.py` before that audit. Therefore that standalone result is not classified as a live bug without a transformed-build failure.

# 4. World-integrity cross-check

The existing world audit remains at:

- 5,238 in-scope maps
- 2,970 NPC spawns
- 25,584 mob spawns
- 18,575 portals
- **0 hard failures**
- 280 review-only findings
- 746 NPCs without dedicated scripts
- 186 excluded Empress links
- 208 active Boss Rush stage portals

# 5. Durable storage / provenance

The audit information is now stored in three durable layers:

1. **Permanent repository report:** this file.
2. **Broad live-audit artifact:** run `33708144642`, artifact **`9876067710`**, containing the Community delta JSON, DB validation, source audit output and metadata.
3. **Exact anomaly artifact:** run `33708699001`, artifact **`9876166134`**, SHA256 `59bc84f61a403a07e7055927ef7c3e50e338fc97d2d8cbae94fab8a4d69e01aa`, containing exact economy anomaly rows, asset parity anomaly paths, and map-exposed new mob/NPC data.
4. **Complete ID inventory artifact:** run `33709146408`, artifact **`9876332531`**, SHA256 `1f9c03af3272ac7e818747b80bc1fbbd55dea4d1c79ada08127577835f0abd1f`, containing the complete added/removed ID CSV and summary.

The Actions artifacts retain the raw machine-readable evidence for 90 days; this report preserves the conclusions permanently.

# 6. Status of the three requested audit goals

## Inventory everything the Community WZ set unlocked

**Complete.** The complete added/removed ID inventory is saved, including all 579 new maps, 523 new mobs, 1,384 new NPCs, 7,021 new item IDs, 19,283 new Character/equipment IDs, five new reactors, and the baseline regressions discovered in Item/Skill.

## Audit Community mobs/NPCs/maps/items/skills that have data but no server behavior

**Audit/triage complete.** Every added/removed ID is preserved in the full CSV with source-reference classification; new mob/NPC map exposure is also recorded. This identified 187 new mobs and 350 new NPCs that are already referenced by live maps and therefore deserve runtime/interaction priority. Implementation of missing behaviors is a separate remediation/content task.

## Full drops/economy validation

**Static/live-data validation complete.** The live DB tables, exact global drops, invalid values, duplicate groups, shop anomalies, rare-scroll policy, NX global rewards, reward uniqueness constraints and existing reward-source audits have all been checked. Remaining items are now specific remediation/policy decisions rather than unknown audit coverage:

- five zero-chance `2050099` normal-drop rows;
- 28 reactor duplicate groups concentrated in known reactors;
- one duplicated 19-item block in shop 1337 / NPC 11000;
- 16 local Gachapon duplicate reward IDs;
- decide whether 10x/10x/10x/10x/5x is the intended rate policy.

## Next remediation priorities discovered by this audit

1. Restore/merge Evan-related Skill.wz groups `2200`, `2210`–`2218` (plus `2001`) or prove they are unnecessary.
2. Classify/restore missing baseline item `2100904`.
3. Runtime-test the **187 newly exposed mobs** and **350 newly exposed NPCs** already referenced by maps, starting with Future Henesys/Empress-era content.
4. Classify the five new reactors.
5. Decide/fix the five zero-chance `2050099` rows.
6. Review the 28 reactor duplicate groups for intentional weighting.
7. Remove the duplicated shop-1337 block if it is unintended/player-accessible.
8. Review 16 duplicate local Gachapon rewards.
9. Align the economy audit's target rate bands with the actual intended server rates.

## Audit provenance

- Initial audit run: `33707853013`
- Expanded durable audit run: `33708144642`
- Exact anomaly run: `33708699001`
- Complete inventory run: `33709146408`
- Complete inventory workflow fix: `4fcd8dffacd1074e7189d82e503b80bae8d4d3d2`

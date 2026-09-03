# EverLeaf Live Community Content / Economy Audit — 2026-09-03

This report preserves findings from the live Oracle server after the wholesale Community WZ + freshly exported XML deployment.

## Live baseline

- Community client/server asset replacement is live.
- 18 live WZ files are present: 17 Community donor WZs plus EverLeaf's custom `EverLeaf_UI.wz` overlay.
- 44,225 fresh server XML files were deployed from the Community donor set.
- Pre-wholesale rollback snapshot: `/opt/everleaf/backups/community-wholesale-test/20260903T005959Z`.
- Live release tree observed by the audit: `/opt/everleaf/releases/solomapling-live-smoke-f8bd03da7ee47b21c5dd01450c560949710497ad-33698055620-1`.

## Full XML-family delta

Live Community XML count: **44,225**. Pre-wholesale baseline: **22,191**. Net increase: **22,034 XML files**.

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

## Behavior-family ID delta

The audit also compared numeric IDs and searched current Java/JS/SQL/Python sources for explicit numeric references. No explicit reference does **not** automatically mean an asset is unusable; many MapleStory systems are data-driven. These counts are triage signals for runtime/server-logic review.

| Family | Live IDs | Baseline IDs | Added | Removed | Added with explicit server ref | Added without explicit server ref |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Map.wz | 5,841 | 5,262 | **579** | 0 | 77 | 502 |
| Mob.wz | 2,091 | 1,568 | **523** | 0 | 14 | 509 |
| Npc.wz | 8,346 | 6,962 | **1,384** | 0 | 62 | 1,322 |
| Item.wz | 13,215 | 6,195 | **7,021** | **1** | 33 | 6,988 |
| Character.wz | 26,531 | 7,248 | **19,283** | 0 | 215 | 19,068 |
| Skill.wz | 32 | 43 | 0 | **11** | 0 | 0 |
| Quest.wz | 2,826 | 2,826 | 0 | 0 | 0 | 0 |
| Reactor.wz | 426 | 421 | **5** | 0 | 0 | 5 |

## Maps unlocked

The new map inventory includes, among many others:

- `211060xxx` / `211070xxx`
- `219000xxx` / `219010xxx` / `219020xxx`
- `271000xxx` / `271010xxx` / `271020xxx` / `271030xxx` / `271040xxx` — Future Henesys family
- `272000xxx` / `272010xxx` / `272020xxx` / `272030xxx`
- `273000xxx` and related ranges
- `450000xxx` appears in the newly exposed set as well

`271000000` was independently confirmed to load in the real client after the wholesale deployment.

## Mobs unlocked

The new mob inventory includes large later-content families, including:

- `821xxxx`
- `8220016`–`8220021`
- `8600000`–`8600006`
- large `861xxxx` family
- large `862xxxx` family
- `8641000+`
- Empress/Cygnus encounter family `8850000`–`8850011` is present in the Community source set

These assets are no longer an acquisition blocker. Encounter/summon/phase behavior remains server-logic work where required.

## NPC delta

The Community replacement exposes **1,384 additional NPC IDs**. The same-ID script check found **0/1,384** with a dedicated `scripts/npc/<id>.js` file in the current source snapshot.

This does not mean all 1,384 are broken. Decorative NPCs, non-interactive NPCs and generic handlers do not necessarily need a same-ID script. Every newly interactive NPC still needs classification before being considered complete.

## Item / equipment / character delta

- Item IDs: **+7,021**
- Character/equipment/cosmetic IDs: **+19,283**
- One baseline Item.wz ID is absent from the Community replacement: **`2100904`**

The missing `2100904` needs classification before asset parity can be called complete.

## Skill regression requiring action

The Community Skill.wz/XML set is **not a strict superset** of the pre-wholesale EverLeaf baseline. The audit found 11 baseline skill/job groups missing after the wholesale replacement:

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

The `2200` / `2210`–`2218` group is especially important because it overlaps EverLeaf's Evan progression work. These groups must be restored/merged or otherwise proven unnecessary before the wholesale WZ set is considered final.

## Quest delta

The numeric Quest.wz inventory is unchanged: **2,826 live IDs and 2,826 baseline IDs**. The Community replacement did not add or remove numeric quest IDs in this comparison.

## Reactor delta

Five reactor IDs are newly present and had no explicit server-source references in the audit:

- `2401100`
- `2401200`
- `5411001`
- `9990000`
- `9990001`

They need classification as passive/decorative versus action-bearing reactors.

# Live drops / economy validation

## Live table sizes

The live `cosmic` schema contains the expected economy surfaces. Current row counts:

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

Other relevant tables detected include `dueyitems`, `inventoryitems`, `makerrewarddata`, `mts_items`, `nxcode_items`, and `specialcashitems`.

## Drop integrity findings

- Normal drops with `chance <= 0`: **5** — needs exact-row classification.
- Normal invalid quantity ranges: **0**.
- Global drops with nonpositive chance: **0**.
- Global invalid quantity ranges: **0**.
- Reactor drops with nonpositive chance: **0**.
- Duplicate normal-drop groups `(dropperid,itemid,questid)`: **0**.
- Duplicate global-drop groups: **0**.
- Duplicate reactor-drop groups `(reactorid,itemid,questid)`: **28** — review required; may include intentional variants or true duplicates.

## Shop integrity findings

- Negative-price shop rows: **0**.
- Orphan shop-item rows: **0**.
- Duplicate `(shopid,itemid)` groups: **19** — needs classification for intentional repeated entries versus duplicates.

## Rare-scroll global policy — verified live

The live `drop_data_global` table contains **no** rows for:

- Chaos Scroll 60% `2049100`
- White Scroll `2340000`

So ordinary global monster-drop removal for those two items is live.

The reward-source audit separately confirms both remain intentionally available through the global rare Gachapon pool and approved authored boss/reward sources.

## NX global drops — verified live

- `4031865` — one global row at chance **400/999999**
- `4031866` — one global row at chance **100/999999**

These match the intended EverLeaf target values.

## Reward uniqueness protection — verified live schema

`everleaf_encounter_weekly_reward`:
- unique primary key `(account_id, encounter_id, week_start_utc)`
- unique `attempt_id`

`everleaf_vote_reward_ledger`:
- unique `(account_id, provider, vote_date_utc)`

`everleaf_vote_rewards`:
- unique `(provider, external_vote_id)`

The relevant duplicate-claim protection indexes therefore exist in the live schema.

# Existing source-audit findings

## Economy balance policy

Current configured rates read as:

- EXP: **10x**
- Meso: **10x**
- Drop: **10x**
- Boss drop: **10x**
- Quest: **5x**

`tools/audit_economy_balance.py` flags the four 10x values because its older pre-alpha target bands were lower. This is a **balance-policy mismatch**, not evidence of a runtime failure.

The same audit estimates the current intended NX global-drop target at roughly **65 NX per 1,000 kills** before playstyle-specific variation.

## Reward-source audit

`tools/audit_reward_sources.py` passes its invariants.

- Global Gachapon pool: 31 common IDs, 8 uncommon IDs, 4 rare IDs.
- Chaos Scroll and White Scroll remain in the global rare Gachapon pool.
- No local Gachapon pool adds an extra Chaos/White roll.
- 13 Gachapon classes / 1,683 numeric reward slots were inventoried.
- **16 duplicate Gachapon reward IDs** are marked for review across local machines.
- Boss/fishing/Boss Rush rare-scroll policy checks passed.

## Item/equipment standalone audit caveat

Running `tools/audit_items_equipment.py` directly on the raw checkout reports:

`ERROR ItemInformationProvider: missing required guard: import constants.inventory.EquipmentRequirements;`

The normal release build applies `tools/apply_equipment_requirement_fixes.py` before this audit. Therefore this raw-checkout result is not automatically a live-server defect; the transformed build pipeline remains the authoritative check.

## World integrity

The existing world audit still reports:

- **5,238** in-scope maps
- **2,970** NPC spawns
- **25,584** mob spawns
- **18,575** portals
- **0 hard failures**
- 280 review-only findings
- 746 NPCs without dedicated scripts
- 186 excluded Empress links
- 208 active Boss Rush stage portals

Many review-only findings are missing optional/scripted portal handlers and require content-level classification rather than being treated as immediate hard failures.

# Durable audit storage

The dedicated read-only workflow `.github/workflows/audit-live-community-unlocked.yml` completed successfully as run **`33708144642`**.

A 90-day artifact was saved:

- Artifact name: `everleaf-community-live-audit-33708144642`
- Artifact ID: **`9876067710`**
- ZIP SHA256: `2ef5e1bddedd4525e1fe755863aca55b92394b2e92c4554db708fb5972b53c5b`

It contains:

- `community-unlocked-audit.json`
- `economy-db-validation.txt`
- `release-audits.txt`
- `README.txt`

This repository document is the permanent summary so the important findings survive artifact expiry.

# Actionable remaining findings from these three audit goals

The broad inventory itself is complete. Follow-up implementation/classification work is now concrete:

1. **Skill parity:** restore/merge or prove unnecessary the 11 missing skill groups, especially Evan `2200` and `2210`–`2218`.
2. **Item parity:** classify missing baseline item `2100904`.
3. **New content behavior:** classify the 579 maps, 523 mobs, 1,384 NPCs, 7,021 items and 19,283 Character.wz IDs by data-driven versus custom server-logic needs.
4. **Reactor behavior:** classify the five newly exposed reactors.
5. **Drops:** inspect the exact five normal drop rows with nonpositive chance and 28 duplicate reactor-drop groups.
6. **Shops:** classify the 19 duplicate `(shopid,itemid)` groups.
7. **Gachapon:** classify the 16 duplicate local reward IDs.
8. **Economy policy:** decide whether the current 10x/10x/10x/10x/5x rates are intentional; if yes, update the stale pre-alpha audit bands instead of treating the rates as defects.

# Audit provenance

- Initial audit workflow run: `33707853013`
- Initial audit commit: `ee8697d06cf9593830577a0454a326e52fd4ceaf`
- Expanded durable audit workflow commit: `3492a4e2013dcf0b7978dde3779df8e083588f9f`
- Expanded successful audit run: `33708144642`
- Durable artifact ID: `9876067710`

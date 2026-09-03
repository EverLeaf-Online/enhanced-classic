# EverLeaf Live Community Content / Economy Audit — 2026-09-03

This report preserves findings from the live Oracle server after the wholesale Community WZ + freshly exported XML deployment.

## Live baseline

- Community client/server asset replacement is live.
- 18 live WZ files are present: 17 Community donor WZs plus EverLeaf's custom `EverLeaf_UI.wz` overlay.
- 44,225 fresh server XML files were deployed from the Community donor set.
- Pre-wholesale rollback snapshot: `/opt/everleaf/backups/community-wholesale-test/20260903T005959Z`.
- The live release tree observed by the first audit was `/opt/everleaf/releases/solomapling-live-smoke-f8bd03da7ee47b21c5dd01450c560949710497ad-33698055620-1`.

## First live delta pass

The first read-only pass compared the live Community XML tree with the preserved pre-wholesale server XML tree and searched current Java/JS/SQL/Python sources for explicit numeric references.

| Family | Live IDs | Baseline IDs | Added IDs | Added with explicit server reference | Added without explicit server reference |
| --- | ---: | ---: | ---: | ---: | ---: |
| Map.wz | 5,841 | 5,262 | 579 | 77 | 502 |
| Mob.wz | 2,091 | 1,568 | 523 | 14 | 509 |
| Npc.wz | 8,346 | 6,962 | 1,384 | 62 | 1,322 |
| Item.wz | 13,215 | 6,195 | 7,021 | 33 | 6,988 |
| Skill.wz | 32 | 43 | 0 | 0 | 0 |
| Quest.wz | 2,826 | 2,826 | 0 | 0 | 0 |
| Reactor.wz | 426 | 421 | 5 | 0 | 5 |

Important interpretation: an ID having no explicit numeric source reference does **not** automatically mean it is unusable. Many maps, mobs, items and skills are data-driven. This field is a triage signal for assets likely to need targeted runtime/server-logic review, not a definitive unsupported-content count.

### Notable newly exposed map ranges

The added map inventory includes, among many others:

- `211060xxx` / `211070xxx`
- `219000xxx` / `219010xxx` / `219020xxx`
- `271000xxx` / `271010xxx` / `271020xxx` / `271030xxx` — Future Henesys family
- `272000xxx` / `272010xxx` / `272020xxx` / `272030xxx`
- `273000xxx` and related ranges

`271000000` was independently confirmed to load in the real client after the wholesale deployment.

### Notable newly exposed mob ranges

The added mob inventory includes:

- `821xxxx`
- `8220016`–`8220021`
- `8600000`–`8600006`
- large `861xxxx` family
- large `862xxxx` family
- Empress/Cygnus encounter family `8850000`–`8850011` is present in the Community source set and is being treated as server-logic work rather than an asset-acquisition blocker.

### NPC delta

The first pass found 1,384 NPC IDs not present in the pre-wholesale XML tree. None had a same-ID `scripts/npc/<id>.js` file in the current source snapshot. This does **not** mean all 1,384 require scripts: decorative/non-interactive NPCs and NPCs handled generically are possible. It does mean every newly interactive NPC needs classification before being considered complete.

### Item delta

The first pass found 7,021 Item.wz IDs not present in the pre-wholesale server XML set. Many are chairs/cosmetics/consumables whose base behavior is data-driven. Items requiring custom effects, progression logic, quest handling, exchange rules or special packets still need classification.

### Reactor delta

Five reactor IDs were newly present and had no explicit server-source references in the first pass:

- `2401100`
- `2401200`
- `5411001`
- `9990000`
- `9990001`

These require classification as passive/decorative versus action-bearing reactors.

## Live economy/database surfaces

The live `cosmic` schema contains the expected economy-related tables, including:

- `drop_data`
- `drop_data_global`
- `reactordrops`
- `shops`
- `shopitems`
- `makerrewarddata`
- `inventoryitems`
- `dueyitems`
- `everleaf_encounter_weekly_reward`
- `everleaf_nx_rewards`
- `everleaf_vote_reward_ledger`
- `everleaf_vote_rewards`
- `mts_items`
- `nxcode_items`
- `specialcashitems`

The first source economy audit also confirmed the configured rates currently read as **10x EXP / 10x meso / 10x drop / 10x boss drop / 5x quest**. That audit intentionally flagged the four 10x values because its old pre-alpha target bands were lower. This is a balance-policy finding, not a runtime failure.

The same audit reported the intended rare/global-drop policy in source:

- ordinary global Chaos Scroll 60% (`2049100`) — removed
- ordinary global White Scroll (`2340000`) — removed
- NX global target values: 100 NX coupon `4031865` at 400/999999 and 250 NX coupon `4031866` at 100/999999

## Audit durability

A dedicated read-only workflow, `.github/workflows/audit-live-community-unlocked.yml`, now captures the live-vs-backup inventory, database validation, and existing source audit output into a 90-day GitHub Actions artifact. This report is the permanent repository-level summary so the findings do not disappear when workflow artifacts expire.

## Remaining classification work

- Classify newly added maps as fully data-driven, script-dependent, event-dependent or unsupported.
- Classify newly added mobs for ordinary data-driven behavior versus summon/phase/special-AI requirements.
- Classify newly added NPCs as decorative, generic-interaction, existing-script-compatible or missing-script.
- Classify newly added items as passive/data-driven versus special server behavior.
- Correctly inventory Skill.wz using its grouped serializer structure before drawing any conclusions from the preliminary ID count.
- Classify the five new reactors.
- Complete live drop/shop/reward integrity checks and preserve their exact counts/findings here.
- Prioritize Future Henesys / Empress / Stronghold content now that the underlying Community assets are available.

## Audit provenance

- Initial audit workflow run: `33707853013`.
- Initial audit commit: `ee8697d06cf9593830577a0454a326e52fd4ceaf`.
- Expanded durable audit workflow commit: `3492a4e2013dcf0b7978dde3779df8e083588f9f`.
- Expanded audit run: `33708144642` (results to be folded into this report after completion).

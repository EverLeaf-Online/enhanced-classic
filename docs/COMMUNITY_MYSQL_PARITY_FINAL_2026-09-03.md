# EverLeaf Community MySQL parity — final 2026-09-03

This records the production database remediation completed after the wholesale Community WZ + server XML deployment.

## Resolved live

- All **187** newly introduced mobs that are actually referenced by live maps now have `drop_data` coverage.
- The initial **181** mobs with no rows received conservative Cosmic MesoFetcher-compatible meso rows.
- A source-backed pass then added **201** validated item-drop rows affecting **40** new mobs.
  - **180** inserted rows are in content families validated against Hidden Street coverage.
  - **21** are exact-ID v90 fallback rows for Future Henesys IDs where matching Hidden Street post-v83 pages were not available.
  - Source rows were rejected when the item did not exist in the live WZ set or a quest-specific row referenced a quest absent from the live Quest data.
- The five inert `2050099` rows with `chance=0` were removed transactionally. Final `drop_data` rows with `chance<=0`: **0**.
- Final live `drop_data` count: **22,696**.
- Existing global drops, reactor drops, shops, and shop items were not wholesale-replaced.

## Intentionally not fabricated

- **350** newly placed NPCs have no new shop rows. The final name/context pass found no merchant-name candidates, and placement alone is not evidence that an NPC should own a shop. No inventories were invented.
- New reactor `2401100` is on map `240060201` and carries action `chaoshontaleBoss`; it has no `reactordrops` row. This is an action/boss reactor, so no DB drop row was fabricated.
- New reactor `5411001` is on map `541020800` and carries action `treeBossSG`; it has no `reactordrops` row. This is likewise action-driven, so no DB drop row was fabricated.

## Existing duplicates classified

- All **19** duplicate shop groups are shop `1337` / NPC `11000`. None duplicate the same position; each repeated item occupies two different positions. This is the GM/fallback shop layout/category data and was left intact rather than altering player economy data.
- All **28** existing reactor duplicate groups were left intact. Their repeated rows are concentrated in authored reactor sets and can encode weighting; no destructive de-duplication was performed without independent evidence that the weighting is accidental.

## Verification

Successful final verification run: **`33721507995`**.

Final markers:

- `placed_new_mobs_without_any_drop_data = 0`
- `nonpositive_drop_rows = 0`
- `drop_data = 22696`
- `drop_data_global = 4`
- `reactordrops = 1116`
- `shops = 110`
- `shopitems = 3795`
- `everleaf.service = active`
- TCP `8484` listening
- `COMMUNITY_MYSQL_PARITY_FINAL_OK`

Final artifact: **`9880392633`**, SHA256 `fa95a00e22ac09b7a7a03e750d937266cf89d99ebccdee6377e85507affbf39f`.

The artifact contains the final classification report, live verification output, and exact rollback SQL for the five removed zero-chance rows. The earlier source-backed remediation artifact `9880228555` contains exact rollback SQL for the 201 source-backed item rows, and artifact `9879732324` contains rollback SQL for the 181 conservative meso rows.

No blanket database import was performed, and no redundant full production backup was created.
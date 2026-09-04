# EverLeaf Production Contract

This is the authoritative EverLeaf production baseline. Checked-in release code and deployment gates must satisfy this contract; deployment transforms are validators/legacy normalizers, not an alternate source of truth.

## Runtime
- MapleStory protocol/client: **v83**
- Primary world: **20 channels**
- Login: **8484**
- Channels: **7575-7594**
- Public channel handoff host: **132.145.141.79**
- Level cap: **250**

## Rates
- EXP: **5x**
- Meso: **3x**
- Drop: **2x**
- Boss drop: **2x**
- Quest: **1x**
- Fishing: **2x**
- Travel: **2x**

## Account / economy guardrails
- Automatic in-game registration: **disabled**
- Supply rate coupons: **disabled**
- Website registration is authoritative
- Non-P2W policy remains authoritative

## Canonical content baseline
- Production server WZ is sourced from the validated shared full-v95 XML baseline at `/opt/everleaf/shared/wz-v95`; normal game deploys must not replace it with the smaller repository WZ tree.
- The canonical server WZ must contain at least **44,000 XML files**; the current verified baseline contains **44,236**.
- Future Henesys / Empress is part of the active production content baseline.
- Ninja Castle is part of the active production content baseline, including maps, mobs, NPCs and quests **8163-8171**.
- The live launcher/client manifest remains the source for managed client replacement files; the current managed set is **36/36** files.
- Production deploys must fail closed if representative Empress or Ninja Castle assets disappear from the canonical WZ baseline.

## Reference-source policy
- `Community-files` remains reference/donor material, not a deployment branch.
- Generic v95 donor/exporter/tooling history may be retained when it remains useful for future client/WZ maintenance.
- Region-specific staging/review branches that have been consumed or superseded by the canonical full-v95 baseline are cleanup candidates once they have no active PR.

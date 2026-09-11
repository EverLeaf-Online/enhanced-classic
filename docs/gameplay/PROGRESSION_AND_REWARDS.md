# EverLeaf Progression, Rewards, and Economy

This document consolidates the maintained design for level 200–250 progression, survivability, account-bound progression currencies, NX rewards, collection/account milestones, and controlled high-value reward sources. Current implementation status belongs in [`../EVERLEAF_MASTER_CHECKLIST.md`](../EVERLEAF_MASTER_CHECKLIST.md).

## Design principles

- Preserve the recognizable v83 experience through the classic game while extending meaningful progression beyond level 200.
- Keep the level cap at 250 without creating an infinite stat treadmill.
- Make intended PvE progression viable without legacy HP/MP washing knowledge.
- Keep best-in-slot power and competitive advantages gameplay-earned.
- Use multiple reward lanes so one activity is not the entire endgame.
- Prefer account-bound or purpose-specific currencies when unrestricted items/mesos would create inflation or RMT pressure.
- Make reward claims transactional and idempotent where retries, disconnects, or concurrent actions can occur.
- Reward meaningful alt progression with hard caps rather than rewarding unlimited mule creation.

## Post-200 tiers

- **200–209 — Rooted:** transition into EverLeaf endgame, introductory weeklies and entry progression.
- **210–224 — Awakened:** repeatable endgame progression and stronger group content.
- **225–239 — Ascendant:** advanced boss/content progression and account goals.
- **240–249 — Ancient:** capstone pre-250 progression.
- **250 — Evergreen:** level-cap state with continued mastery, collection, weekly, and prestige goals rather than further levels.

The 201–249 EXP curve and level-250 terminal behavior are implemented; pacing remains subject to live telemetry and balance review.

## Reward lanes

EverLeaf intentionally spreads post-200 value across several lanes:

1. Boss progression and boss-specific materials.
2. Weekly objectives and Verdant Marks.
3. Quest/story unlocks and meaningful quest rewards.
4. Party Quest and group-play rewards, including PQ Points.
5. Collections/exploration/achievements, including account milestone rings.
6. Guild/social objectives.
7. Cosmetics and prestige that do not create paid power.

## Account milestone rings

EverLeaf has three bounded account-wide milestone tracks. Progress is read from authoritative persisted character data, while each character may synchronize the ring tiers earned by the account.

### Monster Book track

- Counts **unique Monster Book card IDs across all non-GM characters on the account**. Finding duplicate copies or completing the same card on multiple alts does not multiply account progress.
- Tier 1: **50** unique cards — Moon Stone Ring 1 Carat (`1112300`).
- Tier 2: **150** unique cards — Moon Stone Ring 2 Carats (`1112301`).
- Tier 3: **300** unique cards — Moon Stone Ring 3 Carats (`1112302`).

### Quest track

- Counts **unique completed quest IDs across all non-GM characters on the account**. Repeating or abandoning a quest cannot inflate the account total because only persisted completed quest IDs are counted distinctly.
- Tier 1: **50** unique completed quests — Shining Star Ring 1 Carat (`1112303`).
- Tier 2: **150** unique completed quests — Shining Star Ring 2 Carats (`1112304`).
- Tier 3: **300** unique completed quests — Shining Star Ring 3 Carats (`1112305`).

### Account Legacy / linked-level track

- Uses only the **four highest-level non-GM characters** on the account.
- Each character contributes at most **200 levels**, so the tracked account score is capped at **800** even if the account has many more characters or levels past 200.
- Tier 1: **200** linked-level score — Gold Heart Ring 1 Carat (`1112306`).
- Tier 2: **400** linked-level score — Gold Heart Ring 2 Carats (`1112307`).
- Tier 3: **600** linked-level score — Gold Heart Ring 3 Carats (`1112308`).
- Power stops increasing at tier 3. A fourth developed character provides flexibility toward the cap but does not create a fourth power tier.

### Synchronization and safety

- `@progress milestones` shows the account's collection and linked-level progress.
- `@progress milestones sync all` synchronizes all currently unlocked rings to the character; `book`, `quest`, or `legacy` may be used to synchronize one track.
- A lower-tier milestone ring evolves by granting the unlocked tier first and only then removing the older EverLeaf-tagged copy, so a failed grant cannot destroy the previous reward.
- An equipped milestone ring must be unequipped before evolution.
- EverLeaf milestone copies carry track-specific owner markers. The upgrader only removes those marked copies and does not consume unrelated vanilla copies of the same ring IDs.
- The selected ring families are already present in the maintained v83/v95 client baseline and are trade-blocked, unique, non-sale equipment, so this layer does not require a new WZ/client package or a database migration.
- Reclaim/synchronization is intentionally character-local and non-economic: milestone rings cannot be used as a tradable item faucet.

## Hybrid weekly model

Weekly objective progress is character-scoped, while valuable weekly reward budgets are account-capped.

- Multiple characters may complete eligible objectives.
- The account cannot multiply high-value weekly rewards simply by creating alts.
- Weekly state and claims are persisted transactionally.
- Catch-up allowance is account-scoped and bounded.
- The weekly reset uses the maintained UTC-week policy.

## Verdant Marks

Verdant Marks are EverLeaf's account-bound post-200 progression currency.

- Earned through approved gameplay progression.
- Stored as account-level database state with an immutable ledger.
- Not a transferable inventory item.
- Cannot be traded between players.
- Donation/premium currency must not convert into Verdant Marks.
- Claim mutations use transactional/uniqueness protections to prevent duplicate payout.
- Appropriate reward categories include progression materials, catch-up items, cosmetics, utility/QoL rewards, and gear-upgrade components.
- Direct finished best-in-slot equipment is intentionally excluded.

Player command surfaces include `@marks` / `@verdant`, `@marks history`, `@weekly` / `@weeklies`, and `@progress` where enabled by the current release.

## PQ Points

PQ Points provide a controlled group-content reward layer rather than forcing every Party Quest to mint the same high-value item directly.

- Successful supported PQ clears award server-authoritative persistent points.
- Clear/reward handling is protected against duplicate payout.
- Different PQs may award different values according to difficulty/time.
- Exchange rewards should favor controlled progression materials, cosmetics, utility, and carefully priced rare items.
- Prices and clear values are balance parameters and should be tuned from actual completion times and economy telemetry.

## NX Credit

Earnable Cash Shop rewards use account-level NX Credit rather than character-scoped reward duplication.

The maintained implementation supports account-scoped daily/playtime/vote reward paths and idempotent verified-vote queueing. Exact reward amounts are balance configuration and should be checked against the implementation/configuration before publishing player-facing numbers.

Security/economy rules:

- external vote verification must not blindly mutate balances without idempotency;
- rewards are account-scoped;
- repeat provider callbacks must not double-pay;
- online character state must not overwrite externally queued/account-level rewards;
- paid rate coupons remain disabled under the no-P2W policy.

## No mandatory HP washing

EverLeaf uses a job- and progression-aware survivability floor instead of requiring players to perform INT washing/MP washing as hidden endgame prerequisites.

The survivability system:

- preserves natural class HP identity;
- guarantees only a minimum floor rather than flattening all jobs to one HP total;
- never reduces legitimate MaxHP above the floor;
- is idempotent;
- is applied during maintained progression/load paths;
- remains bounded by supported MaxHP limits;
- is protected from AP Reset loops that would cross below the EverLeaf floor.

Legacy washed HP above the floor is grandfathered. Final floor tuning remains tied to real boss damage and balance testing.

## Rare-scroll economy

Current policy removes ordinary global monster faucets for Chaos Scroll and White Scroll. Controlled sources may include selected bosses, Party Quest rewards/exchanges, and rare Gachapon pools. White Scroll supply should remain tighter than Chaos Scroll supply.

Before public beta/launch, the economy pass should validate:

- every explicit Chaos/White source;
- boss and PQ reward rates;
- Gachapon effective probabilities;
- meso generation/sinks;
- high-value item generation;
- inflation under projected concurrency;
- RMT-abuse signals and staff response policy.

## No-P2W boundary

Donations may support cosmetics and carefully reviewed noncompetitive convenience. They must not buy damage, survivability, best-in-slot items, better RNG/drop odds, progression currencies, ranking advantages, or bypass intended boss/PQ progression.

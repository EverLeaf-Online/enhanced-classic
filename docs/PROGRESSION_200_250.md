# Everleaf — Level 200–250 Progression

Everleaf treats level 200 as the beginning of enhanced endgame rather than the end of character progression.

## Design goals

- Preserve the recognizable v83 game through level 200.
- Give every post-200 milestone a clear purpose.
- Avoid a single optimal grind being the entire endgame.
- Keep progression earnable through gameplay rather than donations.
- Reward parties, bosses, quests, exploration, collections, and long-term account play.
- Avoid excessive permanent-stat inflation that invalidates classic equipment.

## Endgame tiers

### Tier I — Rooted (200–209)
Purpose: transition from classic endgame into Everleaf endgame.

Initial systems:
- Endgame introductory questline.
- First weekly objectives.
- Entry boss progression.
- Account journal/collection introduction.
- Gear-upgrade materials from multiple activities.

### Tier II — Awakened (210–224)
Purpose: establish repeatable endgame progression.

Initial systems:
- Stronger boss encounters.
- Expanded weekly objective pool.
- Party-focused progression routes.
- Improved endgame equipment acquisition.
- Collection milestones.

### Tier III — Ascendant (225–239)
Purpose: advanced character and account progression.

Initial systems:
- Hard-mode encounter tier.
- Advanced gear upgrade materials.
- High-level quest chains.
- Account achievement objectives.
- Guild-oriented endgame objectives.

### Tier IV — Ancient (240–249)
Purpose: final progression before cap.

Initial systems:
- Final pre-cap boss tier.
- Prestige cosmetics and visible achievements.
- Challenging weekly objectives.
- Capstone equipment progression.
- Long-form account goals.

### Tier V — Evergreen (250)
Purpose: level cap becomes a new state, not a dead end.

Initial systems:
- Capstone quest/achievement.
- Evergreen weekly objectives.
- Cosmetic prestige progression.
- Account collections and boss mastery continue.
- No infinite level/stat treadmill.

## Reward architecture

Post-200 rewards use several independent lanes so one activity cannot dominate the entire game:

1. **Boss lane** — boss-specific materials, equipment, cosmetics, mastery achievements.
2. **Weekly lane** — predictable account/character progression with sensible caps, paid out as Verdant Marks.
3. **Quest lane** — one-time story/progression unlocks and meaningful EXP.
4. **Party lane** — PQ/endgame group rewards and catch-up opportunities.
5. **Collection lane** — exploration, monsters, bosses, items, achievements, and cosmetics.
6. **Guild lane** — cooperative objectives and social prestige.

## Approved hybrid weekly model

Everleaf weeklies are intentionally split between character freedom and account-level economy control.

- Weekly objective progress is **character-scoped**.
- Different characters on the same account may complete their own eligible objectives.
- Valuable weekly rewards are **account-capped** per UTC week.
- Catch-up allowance is also account-scoped and capped at two weeks of core progression.
- Completing objectives on extra characters does not multiply the account's high-value reward budget.
- Claims are committed atomically so concurrent/double claims cannot exceed the account cap.
- Weekly windows reset Monday at 00:00 UTC.
- Persistent state uses a dedicated account table and character-objective table.

This model preserves alt play while preventing large alt rosters from multiplying capped endgame rewards.

## Verdant Marks

**Verdant Marks** are Everleaf's approved account-bound post-200 weekly progression currency.

- Successful weekly claims mint Verdant Marks into a shared account balance.
- The weekly claim, account budget update, Verdant Marks balance update, ledger entry, and objective claim are committed in one database transaction.
- Every earn/spend mutation is recorded in an immutable audit ledger.
- Verdant Marks cannot be traded between players.
- Donation currency must never convert into Verdant Marks.
- Boss-specific materials remain separate so weeklies do not replace boss progression.
- Level milestones at 200 / 210 / 225 / 240 / 250 unlock content directly rather than charging Verdant Marks.

The approved reward-shop categories are:

- Progression materials.
- Catch-up items.
- Cosmetics.
- Utility / quality-of-life rewards.
- Gear-upgrade components.

Finished/direct best-in-slot equipment is intentionally excluded. The reward-definition contract rejects direct-BiS and pay-to-win reward tags so future shop content cannot accidentally violate this rule without changing tested code.

## Economy rules

- Avoid raw meso as the primary endgame reward.
- Prefer bound or purpose-specific progression materials where inflation would be dangerous.
- Best-in-slot power must not be purchasable through donations.
- Verdant Marks must remain gameplay-earned and account-bound.
- Weekly caps should limit compulsory grinding without making additional play worthless.
- Alternate activities should provide comparable progress at different efficiencies and social requirements.
- Catch-up systems should target returning/new players without invalidating active-player effort.
- Reward-shop purchase operations require unique purchase transaction keys so retries are idempotent without preventing legitimate repeat purchases.

## Milestone rewards

Milestone rewards should primarily unlock systems and recognition rather than dump large amounts of permanent stats.

- **200:** unlock Everleaf endgame and introductory questline.
- **210:** unlock Tier II objectives and encounters.
- **225:** unlock Tier III objectives and hard-mode progression.
- **240:** unlock Tier IV capstone progression.
- **250:** capstone achievement, title/cosmetic recognition, Evergreen progression access.

Exact reward-shop items, item IDs, prices, and purchase limits are economy-tuning decisions and are intentionally kept outside the core tier policy.
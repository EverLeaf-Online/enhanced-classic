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
2. **Weekly lane** — predictable account/character progression currency with sensible caps.
3. **Quest lane** — one-time story/progression unlocks and meaningful EXP.
4. **Party lane** — PQ/endgame group rewards and catch-up opportunities.
5. **Collection lane** — exploration, monsters, bosses, items, achievements, and cosmetics.
6. **Guild lane** — cooperative objectives and social prestige.

## Approved hybrid weekly model

Everleaf weeklies are intentionally split between character freedom and account-level economy control.

- Weekly objective progress is **character-scoped**.
- Different characters on the same account may complete their own eligible objectives.
- Valuable weekly reward points are **account-capped** per UTC week.
- Catch-up allowance is also account-scoped and capped at two weeks of core progression.
- Completing objectives on extra characters does not multiply the account's high-value reward budget.
- Claims are committed atomically so concurrent/double claims cannot exceed the account cap.
- Weekly windows reset Monday at 00:00 UTC.
- Persistent state uses a dedicated account table and character-objective table.

This model preserves alt play while preventing large alt rosters from multiplying capped endgame rewards.

## Weekly reward layer boundary

The server now has the mechanics to calculate, persist, cap, and atomically claim abstract weekly progression points. Those points are intentionally **not yet mapped to a permanent player-facing currency or item**.

That separation lets the economy layer be chosen deliberately. The next economy decision is whether claimed weekly points become an account-bound spendable currency, directly unlock milestone rewards, or use a mixed model. Boss-specific materials remain a separate lane so weekly currency cannot replace all boss drops.

## Economy rules

- Avoid raw meso as the primary endgame reward.
- Prefer bound or purpose-specific progression materials where inflation would be dangerous.
- Best-in-slot power must not be purchasable through donations.
- Weekly caps should limit compulsory grinding without making additional play worthless.
- Alternate activities should provide comparable progress at different efficiencies and social requirements.
- Catch-up systems should target returning/new players without invalidating active-player effort.

## Milestone rewards

Milestone rewards should primarily unlock systems and recognition rather than dump large amounts of permanent stats.

- **200:** unlock Everleaf endgame and introductory questline.
- **210:** unlock Tier II objectives and encounters.
- **225:** unlock Tier III objectives and hard-mode progression.
- **240:** unlock Tier IV capstone progression.
- **250:** capstone achievement, title/cosmetic recognition, Evergreen progression access.

Exact items, bosses, currencies, and numerical reward values are introduced in isolated systems with tests rather than hard-coded into the tier policy.
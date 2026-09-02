# EverLeaf NX Rewards

EverLeaf uses **NX Credit** (`accounts.nxCredit`) as the canonical earnable Cash Shop currency.

## Player rewards

The initial non-P2W reward schedule is:

- Daily claim: **1,000 NX Credit** per account per UTC day.
- Daily streak: every 7th consecutive daily claim adds **1,000 bonus NX Credit**.
- Playtime: **500 NX Credit every 30 minutes**, capped at **4 rewards / 2,000 NX per UTC day**.
- Verified vote: default **1,500 NX Credit** per verified external vote.

Rewards are account-wide. Creating extra characters does not create extra daily or playtime claims.

## Player command

`@points nx`

Claims any currently available daily, playtime, and queued vote NX, then shows the current reward status.

`@points daily`

Claims only the daily reward.

`@points`

Shows Reward Points, Vote Points, and the current NX Credit balance. Playtime tracking starts automatically when the character enters the world and checkpoints remaining elapsed time during disconnect or channel-change cleanup.

## Vote integration

External vote validation should **not** directly modify `accounts.nxCredit`. Call `NxRewardService.queueVerifiedVote(...)` after the vote provider has been verified. The service stores an idempotent pending reward keyed by `(provider, external_vote_id)`.

The player claims queued vote rewards through `@points nx`. This design keeps the database balance synchronized with the in-memory Cash Shop balance and prevents an online character save from overwriting an externally granted NX update.

## Database

Apply:

`database/sql/migration/everleaf_nx_rewards.sql`

It creates:

- `everleaf_nx_rewards` — one account-level row for daily streak and playtime state.
- `everleaf_vote_rewards` — verified, idempotent vote rewards with claimed timestamps.

## Abuse controls

- Rewards use `account_id`, not character id.
- Daily claims use a UTC date boundary.
- Playtime claims are capped per UTC day.
- Vote events use a unique provider/external-vote identifier so webhook/API retries cannot double-pay.
- Vote amounts are bounded in the service.
- Pending votes are claimed transactionally.

The initial values are intentionally modest for beta and can be tuned after Cash Shop pricing and the broader economy are measured.

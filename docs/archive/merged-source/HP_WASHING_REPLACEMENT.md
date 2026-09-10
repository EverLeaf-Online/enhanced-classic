# HP Washing Replacement Strategy

Enhanced Classic will not require legacy HP washing for intended PvE progression.

## What the upstream code currently does

Cosmic retains the classic AP/HP/MP machinery in `AssignAPProcessor`:

- AP Resets can remove AP from HP or MP.
- HP/MP resets are constrained by job/level minimum pools.
- AP can be assigned directly into HP or MP.
- HP/MP gains differ by job and can depend on MaxHP-increase skills.
- The existing `hpMpApUsed` accounting tracks AP invested into the HP/MP pools.
- `USE_ENFORCE_HPMP_SWAP` can restrict HP/MP reset movement, but it does not remove the underlying washing mechanic.

This means simply hiding AP Resets or changing one config flag is not sufficient. We need an explicit survivability model.

## Enhanced Classic policy

1. **A normally built character must be able to survive every boss intended for that character's progression tier.**
2. **INT washing and MP washing must never be prerequisites for endgame access.**
3. **Base HP differences remain part of class identity.** Warriors should still feel naturally durable and ranged/magic classes should not receive identical HP pools.
4. **Defensive class skills remain meaningful.** The replacement system should complement, not invalidate, class-specific survivability tools.
5. **Legacy washed characters must not receive an overwhelming permanent advantage if character imports or old test data ever exist.**

## Chosen direction: progression-based HP floor

Rather than globally giving every job huge HP per level, Enhanced Classic will use a **job- and level-aware minimum MaxHP floor**.

At selected progression milestones, the server will ensure a character's permanent MaxHP is at least the configured floor for its job family and level/tier. If natural MaxHP is already above the floor, nothing is granted.

This gives us several advantages:

- Existing class HP growth remains intact.
- We can tune survivability against actual boss damage.
- Players cannot abuse the system for unlimited HP.
- New players do not need hidden knowledge about washing.
- Adjustments can be made later without rewriting every level-up formula.

## Proposed milestone model

Initial milestone candidates:

- First job advancement
- Second job advancement
- Third job advancement
- Fourth job advancement
- Level 120
- Level 140
- Level 160
- Level 180
- Level 200

Exact HP floors are **not locked yet**. They will be derived from boss progression and survivability testing rather than guessed in isolation.

## Compatibility plan

### AP assignment

Keep normal STR/DEX/INT/LUK assignment unchanged.

Direct AP assignment into HP/MP may remain technically functional during early development for compatibility, but it will not be required by progression. Before public release we will decide whether to:

- disable manual HP/MP AP assignment entirely, or
- permit it with a tightly controlled cap for build expression.

### AP Reset behavior

Legacy HP/MP AP Reset logic currently supports transferring invested HP/MP AP while enforcing minimum pools. We will preserve it initially to avoid destabilizing unrelated stat code, then narrow/disable it after the HP-floor system is tested.

### Existing MaxHP skills

Warrior/Dawn Warrior MaxHP-increase skills and equivalent job mechanics continue to function. HP floors are minimum guarantees, not replacements for those skills.

## Implementation stages

### Stage A — Audit

- Map all MaxHP/MaxMP level-up calculations.
- Map AP Reset handlers and `hpMpApUsed` persistence.
- Identify job-advancement HP grants.
- Catalog boss contact/magic damage relevant to progression.

### Stage B — Service

Introduce an Enhanced Classic survivability service with a single responsibility:

`ensureProgressionHpFloor(character, trigger)`

The service should:

- determine job family;
- determine progression milestone/tier;
- calculate the minimum permanent MaxHP;
- grant only the missing difference;
- never reduce legitimate MaxHP;
- log grants for balance telemetry;
- be idempotent so repeated calls cannot duplicate rewards.

### Stage C — Triggers

Call the service on:

- job advancement;
- milestone level-up;
- login as a migration/safety check.

Login checks let us safely update floor tables later without requiring database scripts for every existing character.

### Stage D — Tests

Automated tests must verify:

- repeated floor application does not stack;
- naturally high-HP characters receive no unnecessary grant;
- each job family reaches its intended floor;
- changing jobs applies the correct future tier without duplicating prior grants;
- HP never exceeds the game's supported MaxHP cap;
- AP Reset cannot bypass the floor into an exploit loop.

## Balance methodology

We will tune HP floors from the boss ladder backward.

For each boss/tier, define:

- largest unavoidable single hit;
- realistic defensive buffs for that class;
- potion/healing assumptions;
- desired safety margin;
- whether the mechanic is intended to be survivable or explicitly avoidable.

Then set class-family floors high enough to participate without washing while retaining meaningful differences in durability.

## No-P2W requirement

HP-floor progression is gameplay infrastructure and will never be tied to donations, supporter status, premium currency, paid pets, paid equipment, or paid RNG.

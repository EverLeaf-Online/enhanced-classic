# EverLeaf Reward Economy Direction

This document records the current reward/economy direction for EverLeaf while the server is still in pre-alpha balancing.

## Pet Vac

- Pet Vac should be earned with **Vote Points**, not sold as a VIP-only farming advantage.
- The existing server already has Vote Points on accounts and player/admin commands that read or grant VP, so EverLeaf should build on that system instead of inventing another premium currency.
- Pet Vac should remain a convenience feature: it must respect drop ownership, quest-item restrictions, map/event restrictions, and normal pet eligibility.
- Before implementation, define VP cost, duration/permanence, vacuum range, pickup cadence, and whether the unlock is account- or character-scoped.

## Chaos Scroll / White Scroll supply

Approved source direction:

- **No ordinary global monster drops** for Chaos Scroll 60% (2049100).
- **No ordinary global monster drops** for White Scroll (2340000).
- Keep both scrolls in **Gachapon** as rare rewards.
- Add controlled **boss** and **Party Quest** reward/drop sources.
- White Scroll should remain rarer than Chaos Scroll.
- Audit and rebalance any legacy synthesis, shop, event, quest, fishing, or other sources so those systems cannot silently flood the economy.

Current Gachapon behavior is compatible with this direction: both scrolls are in the global rare Gachapon pool, while each normal Gachapon rolls a 90/8/2 common/uncommon/rare tier split before combining its local reward pool with the global pool.

## Gachapon audit

Before launch:

- Inventory every reward in every Gachapon pool.
- Flag obsolete, GM/debug, event-only, broken, overpowered, or economy-breaking items.
- Check duplicated rewards and effective probabilities after the global pool is merged into local pools.
- Preserve Chaos Scroll and White Scroll as rare Gachapon rewards, but calculate their real effective chance per ticket.
- Review high-end equipment, chairs, throwing stars, bullets, scrolls, rare consumables, and currency-like items.
- Add a static audit so future reward-pool edits are visible in CI.

## Party Quest Points

EverLeaf should add a dedicated **PQ Point** progression layer rather than making every PQ directly drop the same high-value item.

Proposed behavior:

- Successful PQ clears award PQ Points.
- Harder/longer PQs award more points.
- Daily/weekly anti-farm controls can be added if telemetry shows abuse.
- A PQ Point Shop NPC exchanges points for controlled rewards.
- Candidate rewards include Chaos Scrolls, very expensive White Scrolls, cosmetics, chairs, utility items, progression materials, and rotating rewards.
- PQ Points must be server-authoritative and stored persistently.
- Reconnect/re-entry must not allow duplicate clear rewards.

Do not finalize prices until PQ clear times and reward rates are measured.

## Maple Leaves

Maple Leaves (4001126) currently exist as a universal global drop and are already referenced by legacy crafting/reward systems. Instead of deleting them, EverLeaf should turn them into a useful secondary gameplay currency/sink.

Possible EverLeaf uses:

- Maple Leaf exchange NPC/shop.
- Consumable utility items and cosmetics.
- Low/mid-tier enhancement materials.
- PQ Point Shop supplement costs for selected rewards.
- Monster Book / Quest Ring progression materials.
- Event and seasonal exchanges.
- Mesos + Maple Leaves combination costs to create an additional meso sink.

Rules:

- Do not put best-in-slot power behind raw Maple Leaf grinding alone.
- Do not let Maple Leaves directly replace boss/PQ progression.
- Audit all existing sources and sinks before changing the current 0.8% global drop rate.
- Once the sink design is known, tune the global Leaf rate from expected Leaves/hour rather than guessing.

## Current alpha rates

- EXP: 5x
- Mesos: 3x
- Normal drops: 2x
- Boss drops: 2x
- Quest EXP: 1x
- 100 NX Coupon: 0.040% global chance
- 250 NX Coupon: 0.010% global chance
- Chaos Scroll: no ordinary global monster drop
- White Scroll: no ordinary global monster drop

These remain alpha values and should be changed from telemetry/playtesting rather than intuition alone.

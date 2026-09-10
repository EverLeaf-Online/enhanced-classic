# EverLeaf QoL and Future Design Notes

This file preserves design intent for future quality-of-life work without acting as a second roadmap. **Implementation status belongs only in [`../EVERLEAF_MASTER_CHECKLIST.md`](../EVERLEAF_MASTER_CHECKLIST.md).**

Completed work such as attack-while-moving and No Breath is intentionally not tracked here as an unchecked proposal.

## Movement and combat convenience

Potential future work:

- Universal/expanded mobility only if class identity remains meaningful.
- Infinite/reduced-maintenance throwing-star behavior, with PvP/event compatibility reviewed separately.
- Additional client overlays for useful local information without weakening server authority.

## Long-term character progression

Potential systems include:

- Monster Book / quest milestone rings.
- Evolving rings with bounded upgrade tiers.
- Linked-level/account milestones with caps that reward alts without making large rosters mandatory.

The no-mandatory-HP-washing baseline is already implemented; future HP progression should extend that policy rather than recreate washing pressure.

## Inventory, storage, and shops

Candidate QoL features:

- earlier/unrestricted-level storage access where abuse controls permit it;
- restricted remote storage/merchant access from safe maps only;
- Sell All with strong protection/confirmation rules;
- bounded Buyback with dupe-safe persistence;
- explicit allowlists for transferable cosmetic Cash/NX items rather than making all cash items transferable.

Remote systems must never become an escape/restock/storage exploit inside bosses, PQs, events, or restricted instances.

## Pets and loot

Pet Vac should be universal/earnable or progression-based rather than a paid farming advantage. It must preserve ownership, quest-item, map/event, and pickup eligibility rules. Final range, cadence, duration, and account/character scope are balance decisions.

## Bossing and endgame QoL

Possible additions:

- Boss Codex / kill and mastery tracking.
- Controlled boss reward boxes.
- Personal lockout/respawn/cooldown displays.
- Reconnect-to-existing-instance support with strict identity, time-window, entry, death, and reward protections.

## Chat and UI

- Legacy chat throttles may be loosened where they are unnecessarily aggressive, but anti-flood/packet abuse protections remain.
- Optional overlay widgets must not obscure the playfield or make authoritative gameplay decisions client-side.

## Scrolling and enhancement design

Future enhancement work should preserve meaningful item progression while avoiding opaque or excessively destructive friction. Any change to Chaos/White Scroll behavior or protection systems requires an economy source/sink audit first.

Current design direction keeps ordinary global Chaos/White monster drops disabled and favors controlled sources. White Scroll supply should remain tighter than Chaos Scroll supply.

## Design rules

1. Remove annoyance, not gameplay.
2. No paid/VIP-only feature may materially improve combat power or farming throughput.
3. Boss/PQ/map restrictions stay server-authoritative.
4. Convenience systems must fail closed in restricted states.
5. Economy-changing features require source/sink analysis and exploit testing.
6. Client QoL never replaces server-side validation for gameplay state.

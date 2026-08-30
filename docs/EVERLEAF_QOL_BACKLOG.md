# EverLeaf QoL / Progression Backlog

This backlog tracks approved or proposed Enhanced Classic features that should remove friction without deleting progression, travel, economy, or encounter rules.

## Combat and movement

- [ ] Attack while moving
  - Allow classes to use eligible skills while moving instead of forcing unnecessary movement lock-in.
  - Audit client animation/state handling and server packet validation before enabling globally.
  - Preserve intentional skill-specific channeling/cast behavior where required.

- [ ] No breath lock
  - Remove unnecessary post-hit breath / weapon-swap delay.
  - Verify this does not bypass intended stun, seal, knockback, or other combat-control states.

- [ ] Flash Jump for every class
  - Provide a universal movement option without replacing class-specific mobility strengths.
  - Determine unlock level, key binding, animation, MP cost, and class-specific exceptions.

- [ ] Infinite Throwing Stars
  - Once a usable throwing-star stack is owned/equipped, normal PvE grinding should not require constant recharge trips.
  - Preserve star type identity and damage bonuses.
  - Audit PvP/minigame/event behavior separately if applicable.

## HP / long-term character progression

- [ ] Finalize the no-HP-washing progression path
  - Keep traditional HP washing unnecessary.
  - Use progression-based survivability rather than hidden stat-reset chores.
  - Evaluate Monster Book Ring, Quest Ring, evolving rings, boss progression, and other permanent HP/stat rewards.

- [ ] Monster Book Ring / Quest Ring
  - Passive stats from Monster Book completion and/or quest milestones.
  - Include meaningful Max HP progression so survivability grows through gameplay.
  - Prevent mandatory single-path grinding by offering multiple progression sources where practical.

- [ ] Evolving Rings
  - Rings scale through account/character progression milestones.
  - Define upgrade tiers, stat ceilings, replacement rules, and whether progression is character- or account-bound.

- [ ] Linked Level
  - Account-level bonuses for reaching level milestones on multiple characters.
  - Audit the existing linked-level code/data before creating a duplicate system.
  - Cap bonuses so alt progression is rewarding but not mandatory for baseline viability.

## Inventory, storage, shops, and trading

- [ ] Storage at any level
  - Remove the old level-15 storage restriction.
  - Verify new-character abuse protections are not relying on the level gate.

- [ ] Remote Storage / Merchant access
  - Add convenient remote access, but not unrestricted access from every possible map.
  - Block boss maps, active PQs/events/instances, and other restricted maps.
  - Prefer towns / Free Market / safe-map access or an unlockable convenience route.
  - Do not let remote access erase travel, encounter preparation, or map restrictions.

- [ ] Sell All
  - One-click sale for eligible inventory items.
  - Protect equipped, locked, favorite, quest, untradeable, cash, high-value, and explicitly excluded items.
  - Show a confirmation summary before irreversible bulk sales.

- [ ] Buyback
  - Maintain a recent-sale buyback list.
  - Define list size, expiration, character/account scope, and reconnect persistence.
  - Prevent duplication and price-manipulation exploits.

- [ ] Droppable / tradeable NX and Cash items
  - Do not globally make every cash item tradeable by default.
  - Build an allowlist for safe cosmetic/convenience items.
  - Keep account/security-sensitive and progression-sensitive items restricted.
  - Audit merchant, trade, drop, storage, and expiration behavior for duplication risks.

## Pets and loot

- [ ] Pet Vac
  - Pets can vacuum nearby eligible drops automatically.
  - Prefer universal, earnable, or progression-unlocked access instead of VIP-only power.
  - Keep quest/pickup restrictions and ownership rules intact.
  - Define range and pickup rate so it removes annoyance without creating a paid farming advantage.

## Bossing and endgame

- [ ] Boss Codex
  - Track boss kills, clears, difficulties, and milestones.
  - Expose account/character progression clearly.

- [ ] Boss Reward Boxes
  - Controlled reward boxes tied to boss clears/milestones.
  - Use them as a predictable source for rare progression materials where appropriate.
  - Define anti-multiclient and per-account/character reward rules.

- [ ] Boss Timers / Cooldown Tracking
  - In-game view for personal lockouts, respawn windows, entry limits, and reset times.
  - Distinguish world respawns from personal/account cooldowns.

- [ ] Reconnect in Boss Runs / PQs
  - Allow a disconnected participant to rejoin the same still-active instance.
  - Require matching character/party/instance identity.
  - Add time window and one-instance-only protection.
  - Do not allow reconnect to reset deaths, entries, loot eligibility, or cooldowns.

## UI / client overlays

- [ ] Overlay Widgets
  - Boss information / timers.
  - DPS and combat statistics where technically reliable.
  - Progression/codex information where useful.
  - Widgets must be optional and must not obscure the original UI.

## Chat QoL

- [ ] Loosen chat spam restrictions
  - Reduce overly aggressive legacy throttles.
  - Keep anti-flood, packet-abuse, bot-spam, and moderation protections.
  - Do not implement literally unlimited packet-rate chat.

## Scrolling / enhancement systems

- [ ] Custom Scrolling & Enhancements
  - Audit current scrolling, Chaos Scroll, White Scroll, shielding, and enhancement behavior.
  - Consider modern protection against destructive outcomes while retaining item progression risk/cost.
  - Define whether negative Chaos outcomes are removed, bounded, or protected through a separate resource.
  - Keep rare-scroll supply balanced with the boss/endgame economy.

## Rare scroll economy policy

- [x] Remove Chaos Scroll 60% from ordinary global monster drops.
- [x] Remove White Scroll from ordinary global monster drops.
- [ ] Audit all explicit Chaos Scroll sources: bosses, events, gachapon, synthesis, shops, quests, and custom systems.
- [ ] Audit all explicit White Scroll sources: bosses, events, gachapon, shops, quests, and custom systems.
- [ ] Finalize strict source policy after the source audit.

Current direction: **boss-focused / controlled progression sources, not universal mob drops.** White Scroll should be the tighter currency. Chaos Scroll can have somewhat broader controlled sources if the enhancement economy needs it. Literal boss-only sourcing should only be enabled after every non-boss source is inventoried so we do not accidentally leave hidden shops/gachapon routes or delete intended progression rewards.

## Design rules

1. Remove annoyance, not gameplay.
2. No VIP-only feature should materially improve combat power or farming throughput.
3. Boss/PQ restrictions must remain server-authoritative.
4. Remote systems must not work as an escape, restock, storage, or merchant exploit inside restricted encounters.
5. Every economy-changing feature needs a source/sink audit before public release.
6. Client QoL patches must retain server-side validation where the action affects gameplay state.

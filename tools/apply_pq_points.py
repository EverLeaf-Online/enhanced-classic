#!/usr/bin/env python3
"""Inject EverLeaf PQ/reward hardening into the legacy event manager.

Kept as deterministic build transforms while the large upstream event class is
still shared with Cosmic. Every transform is idempotent and fails loudly if an
upstream method shape changes.
"""

from pathlib import Path

PATH = Path("src/main/java/scripting/event/EventInstanceManager.java")

CLEAR_OLD = """    public final void setEventCleared() {
        eventCleared = true;

        for (Character chr : getPlayers()) {
            chr.awardQuestPoint(YamlConfig.config.server.QUEST_POINT_PER_EVENT_CLEAR);
        }

        scriptLock.lock();
"""
CLEAR_NEW = """    public final void setEventCleared() {
        // Event scripts can legitimately converge on the same clear path from
        // more than one callback (for example a final reactor plus a stage
        // completion callback). Treat clear as a one-way transition so legacy
        // Quest Points and EverLeaf PQ Points cannot be paid twice.
        synchronized (this) {
            if (eventCleared) {
                return;
            }
            eventCleared = true;
        }

        for (Character chr : getPlayers()) {
            chr.awardQuestPoint(YamlConfig.config.server.QUEST_POINT_PER_EVENT_CLEAR);
        }

        everleaf.progression.PqPointClearHook.onEventCleared(em.getName(), name, getPlayers());

        scriptLock.lock();
"""

REWARD_FIELD_OLD = """    // forces deletion of items not supposed to be held outside of the event, dealt on a player's leaving moment.
    private final Set<Integer> exclusiveItems = new HashSet<>();
"""
REWARD_FIELD_NEW = """    // forces deletion of items not supposed to be held outside of the event, dealt on a player's leaving moment.
    private final Set<Integer> exclusiveItems = new HashSet<>();

    // Successful legacy event rewards are claimable once per character and
    // reward level for the lifetime of this event instance. Failed inventory
    // checks intentionally do not reserve the claim so the player can retry.
    private final Set<Long> eventRewardClaims = new HashSet<>();
"""

REWARD_METHOD_OLD = """    //gives out EXP & a random item in a similar fashion of when clearing KPQ, LPQ, etc.
    public final boolean giveEventReward(Character player, int eventLevel) {
        List<Integer> rewardsSet, rewardsQty;
        Integer rewardExp;

        readLock.lock();
        try {
            eventLevel--;       //event level starts counting from 1
            if (eventLevel >= collectionSet.size()) {
                return true;
            }

            rewardsSet = collectionSet.get(eventLevel);
            rewardsQty = collectionQty.get(eventLevel);

            rewardExp = collectionExp.get(eventLevel);
        } finally {
            readLock.unlock();
        }

        if (rewardExp == null) {
            rewardExp = 0;
        }

        if (rewardsSet == null || rewardsSet.isEmpty()) {
            if (rewardExp > 0) {
                player.gainExp(rewardExp);
            }
            return true;
        }

        if (!hasRewardSlot(player, eventLevel)) {
            return false;
        }

        AbstractPlayerInteraction api = player.getAbstractPlayerInteraction();
        int rnd = (int) Math.floor(Math.random() * rewardsSet.size());

        api.gainItem(rewardsSet.get(rnd), rewardsQty.get(rnd).shortValue());
        if (rewardExp > 0) {
            player.gainExp(rewardExp);
        }
        return true;
    }
"""
REWARD_METHOD_NEW = """    //gives out EXP & a random item in a similar fashion of when clearing KPQ, LPQ, etc.
    public final boolean giveEventReward(Character player, int eventLevel) {
        if (player == null || eventLevel <= 0) {
            return false;
        }

        final int requestedEventLevel = eventLevel;
        final long rewardClaimKey = (((long) requestedEventLevel) << 32) | (player.getId() & 0xffffffffL);

        synchronized (eventRewardClaims) {
            // Treat an already-paid reward as a successful/complete claim so
            // retrying an NPC dialogue cannot mint another item or EXP while
            // still allowing the legacy dialogue to finish normally.
            if (eventRewardClaims.contains(rewardClaimKey)) {
                return true;
            }

            List<Integer> rewardsSet, rewardsQty;
            Integer rewardExp;

            readLock.lock();
            try {
                eventLevel--;       //event level starts counting from 1
                if (eventLevel >= collectionSet.size()) {
                    eventRewardClaims.add(rewardClaimKey);
                    return true;
                }

                rewardsSet = collectionSet.get(eventLevel);
                rewardsQty = collectionQty.get(eventLevel);
                rewardExp = collectionExp.get(eventLevel);
            } finally {
                readLock.unlock();
            }

            if (rewardExp == null) {
                rewardExp = 0;
            }

            if (rewardsSet == null || rewardsSet.isEmpty()) {
                if (rewardExp > 0) {
                    player.gainExp(rewardExp);
                }
                eventRewardClaims.add(rewardClaimKey);
                return true;
            }

            if (!hasRewardSlot(player, eventLevel)) {
                return false;
            }

            AbstractPlayerInteraction api = player.getAbstractPlayerInteraction();
            int rnd = (int) Math.floor(Math.random() * rewardsSet.size());

            api.gainItem(rewardsSet.get(rnd), rewardsQty.get(rnd).shortValue());
            if (rewardExp > 0) {
                player.gainExp(rewardExp);
            }
            eventRewardClaims.add(rewardClaimKey);
            return true;
        }
    }
"""


def replace_idempotent(text: str, old: str, new: str, label: str) -> str:
    if new in text:
        print(f"EverLeaf {label} already applied.")
        return text
    if old not in text:
        raise SystemExit(f"Expected EventInstanceManager source shape not found for {label}")
    print(f"EverLeaf {label} applied.")
    return text.replace(old, new, 1)


text = PATH.read_text(encoding="utf-8")
text = replace_idempotent(text, REWARD_FIELD_OLD, REWARD_FIELD_NEW, "event-reward claim state")
text = replace_idempotent(text, REWARD_METHOD_OLD, REWARD_METHOD_NEW, "event-reward exactly-once guard")
text = replace_idempotent(text, CLEAR_OLD, CLEAR_NEW, "PQ Point idempotent event-clear hook")
PATH.write_text(text, encoding="utf-8")

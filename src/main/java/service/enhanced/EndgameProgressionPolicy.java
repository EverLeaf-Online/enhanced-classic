package service.enhanced;

import java.util.EnumSet;
import java.util.Set;

/**
 * Central policy for Everleaf's level 200-250 progression unlocks.
 *
 * <p>This intentionally describes capabilities rather than handing out power
 * directly. Boss scripts, quests, weekly systems, gear progression and account
 * systems can consume the same policy without scattering raw level checks.</p>
 */
public final class EndgameProgressionPolicy {

    private EndgameProgressionPolicy() {
    }

    public enum Unlock {
        ENDGAME_QUESTLINE,
        WEEKLY_OBJECTIVES,
        ADVANCED_BOSS_TRACK,
        ACCOUNT_JOURNAL_TIER_2,
        HIGH_END_BOSS_TRACK,
        ADVANCED_GEAR_TRACK,
        LATE_ENDGAME_TRACK,
        ACCOUNT_JOURNAL_TIER_3,
        CAPSTONE_QUESTLINE,
        CAPSTONE_REWARDS
    }

    public static Set<Unlock> unlocksForLevel(int level) {
        EndgameTierPolicy.Tier tier = EndgameTierPolicy.forLevel(level);
        EnumSet<Unlock> unlocks = EnumSet.noneOf(Unlock.class);

        if (tier.rank() >= EndgameTierPolicy.Tier.TIER_1.rank()) {
            unlocks.add(Unlock.ENDGAME_QUESTLINE);
            unlocks.add(Unlock.WEEKLY_OBJECTIVES);
        }
        if (tier.rank() >= EndgameTierPolicy.Tier.TIER_2.rank()) {
            unlocks.add(Unlock.ADVANCED_BOSS_TRACK);
            unlocks.add(Unlock.ACCOUNT_JOURNAL_TIER_2);
        }
        if (tier.rank() >= EndgameTierPolicy.Tier.TIER_3.rank()) {
            unlocks.add(Unlock.HIGH_END_BOSS_TRACK);
            unlocks.add(Unlock.ADVANCED_GEAR_TRACK);
        }
        if (tier.rank() >= EndgameTierPolicy.Tier.TIER_4.rank()) {
            unlocks.add(Unlock.LATE_ENDGAME_TRACK);
            unlocks.add(Unlock.ACCOUNT_JOURNAL_TIER_3);
        }
        if (tier.rank() >= EndgameTierPolicy.Tier.TIER_5.rank()) {
            unlocks.add(Unlock.CAPSTONE_QUESTLINE);
            unlocks.add(Unlock.CAPSTONE_REWARDS);
        }

        return Set.copyOf(unlocks);
    }

    public static boolean isUnlocked(int level, Unlock unlock) {
        if (unlock == null) {
            throw new IllegalArgumentException("unlock cannot be null");
        }
        return unlocksForLevel(level).contains(unlock);
    }
}

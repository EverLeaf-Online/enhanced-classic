package everleaf.progression;

import java.util.Arrays;
import java.util.Locale;

/**
 * Account-wide collection/progression tracks that unlock bounded ring tiers.
 *
 * <p>The selected ring IDs already exist in the maintained v83/v95 client
 * baseline and are trade-blocked, unique, non-sale equipment. EverLeaf adds
 * an owner marker to rings granted through this system so unrelated copies of
 * the underlying vanilla items are never consumed during an upgrade.</p>
 */
public enum AccountMilestoneTrack {
    MONSTER_BOOK(
            "Monster Book",
            "Moon Stone Ring",
            "EL:MILE:BOOK",
            new int[]{50, 150, 300},
            new int[]{1112300, 1112301, 1112302}
    ),
    QUESTS(
            "Quest",
            "Shining Star Ring",
            "EL:MILE:QUEST",
            new int[]{50, 150, 300},
            new int[]{1112303, 1112304, 1112305}
    ),
    LEGACY(
            "Account Legacy",
            "Gold Heart Ring",
            "EL:MILE:LEGACY",
            new int[]{200, 400, 600},
            new int[]{1112306, 1112307, 1112308}
    );

    private final String displayName;
    private final String ringName;
    private final String ownerMarker;
    private final int[] thresholds;
    private final int[] ringIds;

    AccountMilestoneTrack(String displayName, String ringName, String ownerMarker,
                          int[] thresholds, int[] ringIds) {
        if (thresholds.length != ringIds.length || thresholds.length == 0) {
            throw new IllegalArgumentException("Milestone thresholds and ring tiers must align");
        }
        this.displayName = displayName;
        this.ringName = ringName;
        this.ownerMarker = ownerMarker;
        this.thresholds = thresholds.clone();
        this.ringIds = ringIds.clone();
    }

    public String displayName() {
        return displayName;
    }

    public String ringName() {
        return ringName;
    }

    public String ownerMarker() {
        return ownerMarker;
    }

    public int maxTier() {
        return thresholds.length;
    }

    public int tierFor(int value) {
        int tier = 0;
        for (int threshold : thresholds) {
            if (value < threshold) {
                break;
            }
            tier++;
        }
        return tier;
    }

    public int thresholdForTier(int tier) {
        if (tier < 1 || tier > maxTier()) {
            throw new IllegalArgumentException("Invalid milestone tier: " + tier);
        }
        return thresholds[tier - 1];
    }

    public int ringIdForTier(int tier) {
        if (tier < 1 || tier > maxTier()) {
            throw new IllegalArgumentException("Invalid milestone tier: " + tier);
        }
        return ringIds[tier - 1];
    }

    public int tierForRingId(int itemId) {
        for (int i = 0; i < ringIds.length; i++) {
            if (ringIds[i] == itemId) {
                return i + 1;
            }
        }
        return 0;
    }

    public boolean containsRingId(int itemId) {
        return tierForRingId(itemId) > 0;
    }

    public int[] thresholds() {
        return thresholds.clone();
    }

    public int[] ringIds() {
        return ringIds.clone();
    }

    public static AccountMilestoneTrack fromToken(String token) {
        if (token == null) {
            return null;
        }
        return switch (token.toLowerCase(Locale.ROOT)) {
            case "book", "cards", "monster", "monsterbook", "monster-book" -> MONSTER_BOOK;
            case "quest", "quests" -> QUESTS;
            case "legacy", "linked", "levels", "alts", "account" -> LEGACY;
            default -> Arrays.stream(values())
                    .filter(track -> track.name().equalsIgnoreCase(token))
                    .findFirst()
                    .orElse(null);
        };
    }
}

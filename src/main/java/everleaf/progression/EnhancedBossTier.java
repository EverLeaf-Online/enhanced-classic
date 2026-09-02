package everleaf.progression;

/**
 * Canonical post-200 encounter ladder for Everleaf's hybrid boss model.
 *
 * Early tiers enhance recognizable v83 encounters using server-side tuning
 * and mechanics. The final tier is reserved for Everleaf-original capstone
 * encounters once custom content assets are justified.
 */
public enum EnhancedBossTier {
    ROOTED(200, "Rooted", "Enhanced Classic", 1),
    AWAKENED(210, "Awakened", "Enhanced Classic", 2),
    ASCENDANT(225, "Ascendant", "Hard Classic", 3),
    ANCIENT(240, "Ancient", "Hard Classic / Everleaf", 4),
    EVERGREEN(250, "Evergreen", "Everleaf Capstone", 5);

    private final int requiredLevel;
    private final String displayName;
    private final String encounterStyle;
    private final int rank;

    EnhancedBossTier(int requiredLevel, String displayName, String encounterStyle, int rank) {
        this.requiredLevel = requiredLevel;
        this.displayName = displayName;
        this.encounterStyle = encounterStyle;
        this.rank = rank;
    }

    public int requiredLevel() { return requiredLevel; }
    public String displayName() { return displayName; }
    public String encounterStyle() { return encounterStyle; }
    public int rank() { return rank; }

    public static EnhancedBossTier forLevel(int level) {
        if (level >= 250) return EVERGREEN;
        if (level >= 240) return ANCIENT;
        if (level >= 225) return ASCENDANT;
        if (level >= 210) return AWAKENED;
        if (level >= 200) return ROOTED;
        throw new IllegalArgumentException("Everleaf endgame begins at level 200");
    }
}

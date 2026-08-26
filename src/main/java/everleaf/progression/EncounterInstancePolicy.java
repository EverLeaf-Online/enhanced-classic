package everleaf.progression;

/**
 * Rules for dedicated Everleaf enhanced-boss party instances.
 */
public record EncounterInstancePolicy(
        boolean dedicatedPartyInstance,
        boolean allowPracticeAfterWeeklyClear,
        int reconnectGraceSeconds,
        int cleanupDelaySeconds
) {
    public EncounterInstancePolicy {
        if (reconnectGraceSeconds < 0) throw new IllegalArgumentException("reconnectGraceSeconds cannot be negative");
        if (cleanupDelaySeconds < 0) throw new IllegalArgumentException("cleanupDelaySeconds cannot be negative");
    }

    public static EncounterInstancePolicy enhancedBossDefault() {
        return new EncounterInstancePolicy(true, true, 120, 30);
    }
}

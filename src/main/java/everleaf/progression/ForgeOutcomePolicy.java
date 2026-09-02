package everleaf.progression;

/**
 * Global safety contract for Everleaf equipment forging.
 * All progression forge recipes are deterministic: successful payment always
 * produces the declared outcome, with no RNG failure, downgrade, or item loss.
 */
public record ForgeOutcomePolicy(
        boolean deterministic,
        boolean canFail,
        boolean canDowngrade,
        boolean canDestroyItem,
        boolean usesRandomStatRolls
) {
    public ForgeOutcomePolicy {
        if (!deterministic) throw new IllegalArgumentException("Everleaf progression forging must be deterministic");
        if (canFail || canDowngrade || canDestroyItem || usesRandomStatRolls) {
            throw new IllegalArgumentException("Everleaf deterministic forging cannot include punitive RNG");
        }
    }

    public static ForgeOutcomePolicy everleafDefault() {
        return new ForgeOutcomePolicy(true, false, false, false, false);
    }
}

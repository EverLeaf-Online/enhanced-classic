package everleaf.progression;

/**
 * Server-side material identities for the first Everleaf endgame tier.
 * Concrete item IDs are intentionally bound separately from progression logic.
 */
public enum RootedMaterial {
    EMBER_CORE("Ember Core", true),
    ANCIENT_BARK("Ancient Bark", true),
    ROOTED_SIGIL("Rooted Sigil", true);

    private final String displayName;
    private final boolean accountBound;

    RootedMaterial(String displayName, boolean accountBound) {
        this.displayName = displayName;
        this.accountBound = accountBound;
    }

    public String displayName() { return displayName; }
    public boolean accountBound() { return accountBound; }
}

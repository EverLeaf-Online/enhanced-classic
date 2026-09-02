package everleaf.progression;

import java.util.Set;

/**
 * Stable gameplay contract for Everleaf's first enhanced encounter.
 * Engine-specific map/event wiring consumes this policy rather than
 * scattering Rooted Zakum constants through scripts.
 */
public final class RootedZakumPolicy {
    public static final String ENCOUNTER_ID = "rooted_zakum";
    public static final int REQUIRED_LEVEL = 200;
    public static final int MIN_PARTY_SIZE = 3;
    public static final int MAX_PARTY_SIZE = 6;
    public static final int TIME_LIMIT_MINUTES = 30;
    public static final int RECONNECT_GRACE_SECONDS = 120;

    public static final Set<String> MECHANICS = Set.of(
            "arm-pressure",
            "add-waves",
            "anti-burst-window"
    );

    private RootedZakumPolicy() {}

    public static boolean levelEligible(int level) {
        return level >= REQUIRED_LEVEL;
    }

    public static boolean partySizeEligible(int size) {
        return size >= MIN_PARTY_SIZE && size <= MAX_PARTY_SIZE;
    }
}

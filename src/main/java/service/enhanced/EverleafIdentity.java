package service.enhanced;

/** Central player-facing identity for the Everleaf fork. */
public final class EverleafIdentity {
    public static final String NAME = "Everleaf";
    public static final String TAGLINE = "Classic roots. New growth.";
    public static final String EDITION = "Enhanced Classic v83";
    public static final int CLIENT_VERSION = 83;

    private EverleafIdentity() {
    }

    public static String displayName() {
        return NAME + " - " + EDITION;
    }

    public static String welcomeMessage() {
        return "Welcome to " + NAME + " - " + TAGLINE;
    }
}

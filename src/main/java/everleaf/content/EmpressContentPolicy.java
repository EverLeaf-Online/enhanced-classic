package everleaf.content;

/**
 * Runtime safety gate for Gate to the Future / Knight Stronghold / Empress content.
 *
 * The content stays disabled unless the operator explicitly sets
 * EVERLEAF_ENABLE_EMPRESS_CONTENT=true. This keeps partially staged server/client
 * assets unreachable during development.
 */
public final class EmpressContentPolicy {
    private static final String ENV_NAME = "EVERLEAF_ENABLE_EMPRESS_CONTENT";

    private EmpressContentPolicy() {
    }

    public static boolean isEnabled() {
        return Boolean.parseBoolean(System.getenv().getOrDefault(ENV_NAME, "false"));
    }

    public static String disabledMessage() {
        return "Empress content is still being prepared for EverLeaf and is not available yet.";
    }
}

package service.enhanced;

import config.ServerConfig;

import java.util.ArrayList;
import java.util.List;

/** Non-fatal diagnostics for unsafe development defaults before public deployment. */
public final class DeploymentSafetyPolicy {
    private DeploymentSafetyPolicy() {
    }

    public static List<String> warnings(ServerConfig config) {
        if (config == null) {
            throw new IllegalArgumentException("config cannot be null");
        }

        List<String> warnings = new ArrayList<>();
        if (isBlank(config.DB_PASS)) {
            warnings.add("Database password is blank.");
        }
        if ("root".equalsIgnoreCase(trim(config.DB_USER))) {
            warnings.add("Database connection is using the root account; use a dedicated least-privilege user.");
        }
        if (config.AUTOMATIC_REGISTER) {
            warnings.add("Automatic account registration is enabled; disable it before public launch.");
        }
        if (config.USE_SUPPLY_RATE_COUPONS) {
            warnings.add("Cash Shop rate coupons are enabled, which conflicts with Everleaf's no-P2W policy.");
        }
        if (isLoopback(config.HOST)) {
            warnings.add("Server HOST is loopback-only; remote clients cannot connect until deployment host configuration is supplied.");
        }
        return List.copyOf(warnings);
    }

    private static boolean isLoopback(String value) {
        String host = trim(value);
        return "127.0.0.1".equals(host) || "localhost".equalsIgnoreCase(host) || "::1".equals(host);
    }

    private static boolean isBlank(String value) {
        return value == null || value.isBlank();
    }

    private static String trim(String value) {
        return value == null ? "" : value.trim();
    }
}

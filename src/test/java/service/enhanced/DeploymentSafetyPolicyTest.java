package service.enhanced;

import config.ServerConfig;
import org.junit.jupiter.api.Test;

import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

class DeploymentSafetyPolicyTest {

    @Test
    void flagsUnsafeDevelopmentDefaults() {
        ServerConfig config = new ServerConfig();
        config.DB_USER = "root";
        config.DB_PASS = "";
        config.AUTOMATIC_REGISTER = true;
        config.USE_SUPPLY_RATE_COUPONS = true;
        config.HOST = "127.0.0.1";

        List<String> warnings = DeploymentSafetyPolicy.warnings(config);

        assertEquals(5, warnings.size());
    }

    @Test
    void cleanDeploymentHasNoWarnings() {
        ServerConfig config = new ServerConfig();
        config.DB_USER = "everleaf";
        config.DB_PASS = "strong-placeholder";
        config.AUTOMATIC_REGISTER = false;
        config.USE_SUPPLY_RATE_COUPONS = false;
        config.HOST = "203.0.113.10";

        assertTrue(DeploymentSafetyPolicy.warnings(config).isEmpty());
    }

    @Test
    void rejectsMissingConfig() {
        assertThrows(IllegalArgumentException.class, () -> DeploymentSafetyPolicy.warnings(null));
    }
}

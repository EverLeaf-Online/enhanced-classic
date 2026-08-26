package config;

import org.junit.jupiter.api.Test;

import java.util.HashMap;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;

class YamlConfigTest {

    @Test
    void appliesDeploymentOverridesWithoutChangingUnspecifiedValues() {
        YamlConfig config = new YamlConfig();
        config.server = new ServerConfig();
        config.server.DB_HOST = "localhost";
        config.server.DB_USER = "root";
        config.server.DB_PASS = "";
        config.server.DB_URL_FORMAT = "jdbc:mysql://%s:3306/cosmic";
        config.server.HOST = "127.0.0.1";
        config.server.LANHOST = "127.0.0.1";
        config.server.LOCALHOST = "127.0.0.1";
        config.server.AUTOMATIC_REGISTER = true;

        Map<String, String> env = new HashMap<>();
        env.put("EVERLEAF_DB_HOST", "db.internal");
        env.put("EVERLEAF_DB_USER", "everleaf");
        env.put("EVERLEAF_DB_PASS", "secret");
        env.put("EVERLEAF_HOST", "203.0.113.10");
        env.put("EVERLEAF_AUTOMATIC_REGISTER", "false");

        YamlConfig.applyEnvironmentOverrides(config, env);

        assertEquals("db.internal", config.server.DB_HOST);
        assertEquals("everleaf", config.server.DB_USER);
        assertEquals("secret", config.server.DB_PASS);
        assertEquals("jdbc:mysql://%s:3306/cosmic", config.server.DB_URL_FORMAT);
        assertEquals("203.0.113.10", config.server.HOST);
        assertEquals("127.0.0.1", config.server.LANHOST);
        assertFalse(config.server.AUTOMATIC_REGISTER);
    }

    @Test
    void ignoresBlankOverrides() {
        YamlConfig config = new YamlConfig();
        config.server = new ServerConfig();
        config.server.DB_USER = "root";

        YamlConfig.applyEnvironmentOverrides(config, Map.of("EVERLEAF_DB_USER", "  "));

        assertEquals("root", config.server.DB_USER);
    }

    @Test
    void rejectsInvalidBooleanOverride() {
        YamlConfig config = new YamlConfig();
        config.server = new ServerConfig();

        assertThrows(IllegalArgumentException.class,
                () -> YamlConfig.applyEnvironmentOverrides(
                        config, Map.of("EVERLEAF_AUTOMATIC_REGISTER", "sometimes")));
    }
}

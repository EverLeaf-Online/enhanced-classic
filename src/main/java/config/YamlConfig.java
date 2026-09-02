package config;

import com.esotericsoftware.yamlbeans.YamlReader;
import constants.string.CharsetConstants;

import java.io.FileNotFoundException;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.Map;


public class YamlConfig {
    public static final String CONFIG_FILE_NAME = "config.yaml";
    public static final YamlConfig config = loadConfig();

    public List<WorldConfig> worlds;
    public ServerConfig server;

    private static YamlConfig loadConfig() {
        try {
            YamlReader reader = new YamlReader(Files.newBufferedReader(Path.of(CONFIG_FILE_NAME), CharsetConstants.CHARSET));
            YamlConfig config = reader.read(YamlConfig.class);
            reader.close();
            applyEnvironmentOverrides(config, System.getenv());
            return config;
        } catch (FileNotFoundException e) {
            throw new RuntimeException("Could not read config file " + YamlConfig.CONFIG_FILE_NAME + ": " + e.getMessage());
        } catch (IOException e) {
            throw new RuntimeException("Could not successfully parse config file " + YamlConfig.CONFIG_FILE_NAME + ": " + e.getMessage());
        }
    }

    /**
     * Deployment-safe overrides for values that should not be committed to the
     * repository. Local development still works from config.yaml when these
     * variables are absent.
     */
    static void applyEnvironmentOverrides(YamlConfig config, Map<String, String> environment) {
        if (config == null || config.server == null || environment == null) {
            return;
        }

        ServerConfig server = config.server;
        server.DB_HOST = envOrDefault(environment, "EVERLEAF_DB_HOST", server.DB_HOST);
        server.DB_USER = envOrDefault(environment, "EVERLEAF_DB_USER", server.DB_USER);
        server.DB_PASS = envOrDefault(environment, "EVERLEAF_DB_PASS", server.DB_PASS);
        server.DB_URL_FORMAT = envOrDefault(environment, "EVERLEAF_DB_URL_FORMAT", server.DB_URL_FORMAT);
        server.HOST = envOrDefault(environment, "EVERLEAF_HOST", server.HOST);
        server.LANHOST = envOrDefault(environment, "EVERLEAF_LANHOST", server.LANHOST);
        server.LOCALHOST = envOrDefault(environment, "EVERLEAF_LOCALHOST", server.LOCALHOST);

        String automaticRegister = environment.get("EVERLEAF_AUTOMATIC_REGISTER");
        if (automaticRegister != null && !automaticRegister.isBlank()) {
            server.AUTOMATIC_REGISTER = parseBoolean("EVERLEAF_AUTOMATIC_REGISTER", automaticRegister);
        }

        // EverLeaf uses the account password as its only interactive login secret.
        // The v83 PIN/PIC prompts add friction without adding useful protection for
        // our launcher-backed account flow, so always advertise both systems as disabled.
        server.ENABLE_PIN = false;
        server.ENABLE_PIC = false;
    }

    private static String envOrDefault(Map<String, String> environment, String key, String fallback) {
        String value = environment.get(key);
        return value == null || value.isBlank() ? fallback : value;
    }

    private static boolean parseBoolean(String key, String value) {
        if ("true".equalsIgnoreCase(value)) {
            return true;
        }
        if ("false".equalsIgnoreCase(value)) {
            return false;
        }
        throw new IllegalArgumentException(key + " must be true or false");
    }
}

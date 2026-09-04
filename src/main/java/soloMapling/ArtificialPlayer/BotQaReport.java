package soloMapling.ArtificialPlayer;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.LinkedHashMap;
import java.util.Map;

/** Emits compact machine-readable QA evidence tied to the deployed EverLeaf source SHA. */
public final class BotQaReport {
    private static final Logger log = LoggerFactory.getLogger(BotQaReport.class);
    private static final String SOURCE_SHA = resolveSourceSha();

    private BotQaReport() {}

    public static String sourceSha() {
        return SOURCE_SHA;
    }

    public static String emit(String type, Map<String, ?> fields) {
        Map<String, Object> payload = new LinkedHashMap<>();
        payload.put("type", type == null ? "unknown" : type);
        payload.put("sourceSha", SOURCE_SHA);
        payload.put("timestamp", System.currentTimeMillis());
        if (fields != null) payload.putAll(fields);
        String json = toJson(payload);
        log.info("SOLOMAPLING_QA_REPORT={}", json);
        return json;
    }

    public static String toJson(Map<String, ?> values) {
        StringBuilder out = new StringBuilder("{");
        boolean first = true;
        for (Map.Entry<String, ?> entry : values.entrySet()) {
            if (!first) out.append(',');
            first = false;
            out.append('"').append(escape(entry.getKey())).append("\":");
            appendValue(out, entry.getValue());
        }
        return out.append('}').toString();
    }

    private static void appendValue(StringBuilder out, Object value) {
        if (value == null) {
            out.append("null");
        } else if (value instanceof Number || value instanceof Boolean) {
            out.append(value);
        } else {
            out.append('"').append(escape(String.valueOf(value))).append('"');
        }
    }

    private static String escape(String value) {
        if (value == null) return "";
        return value.replace("\\", "\\\\")
                .replace("\"", "\\\"")
                .replace("\n", "\\n")
                .replace("\r", "\\r")
                .replace("\t", "\\t");
    }

    private static String resolveSourceSha() {
        Path marker = Path.of(".everleaf-source-sha");
        try {
            if (Files.isRegularFile(marker)) {
                String sha = Files.readString(marker).trim();
                if (!sha.isBlank()) return sha;
            }
        } catch (IOException ignored) { }
        String env = System.getenv("EVERLEAF_RELEASE_SHA");
        if (env == null || env.isBlank()) env = System.getenv("GITHUB_SHA");
        return env == null || env.isBlank() ? "unknown" : env.trim();
    }
}

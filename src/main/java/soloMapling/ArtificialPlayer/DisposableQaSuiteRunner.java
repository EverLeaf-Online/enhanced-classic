package soloMapling.ArtificialPlayer;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import server.TimerManager;
import tools.DatabaseConnection;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.util.concurrent.atomic.AtomicBoolean;

/**
 * Explicitly armed full SoloMapling suite runner for the disposable QA Docker stack only.
 *
 * <p>The runner is inert unless the exact suite token is present and the configured DB host is
 * the isolated {@code qa-db} service. Production cannot satisfy both gates under the normal
 * EverLeaf deployment topology.</p>
 */
public final class DisposableQaSuiteRunner {
    private static final Logger log = LoggerFactory.getLogger(DisposableQaSuiteRunner.class);
    private static final String ARM_ENV = "EVERLEAF_SOLOMAPLING_SUITE";
    private static final String ARM_TOKEN = "I_UNDERSTAND_DISPOSABLE_QA_SUITE_ONLY";
    private static final String QA_DB_HOST = "qa-db";
    private static final long POLL_MS = 1_000L;
    private static final long SUITE_TIMEOUT_MS = 15 * 60_000L;
    private static final AtomicBoolean started = new AtomicBoolean(false);

    private DisposableQaSuiteRunner() {}

    public static void startIfRequested() {
        if (!ARM_TOKEN.equals(System.getenv(ARM_ENV))) return;
        if (!QA_DB_HOST.equals(System.getenv("EVERLEAF_DB_HOST"))) {
            log.error("SOLOMAPLING_QA_SUITE_RESULT FAIL safety=db-host host={}", System.getenv("EVERLEAF_DB_HOST"));
            return;
        }
        if (!started.compareAndSet(false, true)) return;
        log.info("SOLOMAPLING_QA_SUITE armed against disposable qa-db only");
        TimerManager.getInstance().schedule(DisposableQaSuiteRunner::startSuite, 2_000L);
    }

    private static void startSuite() {
        try {
            Template template = findQaTemplate();
            BotQaSuiteRunner.SuiteResult initial = BotQaSuiteRunner.start(
                    template.characterId(), template.characterId(), template.mapId(), 3, "ARM");
            if (!initial.success()) {
                log.error("SOLOMAPLING_QA_SUITE_RESULT FAIL reason={} phase={}", initial.reason(), initial.phase());
                cleanup(template.characterId());
                return;
            }
            log.info("SOLOMAPLING_QA_SUITE_START owner={} template={} map={} phase={}",
                    template.characterId(), template.characterId(), template.mapId(), initial.phase());
            long deadline = System.currentTimeMillis() + SUITE_TIMEOUT_MS;
            poll(template.characterId(), deadline);
        } catch (Throwable t) {
            log.error("SOLOMAPLING_QA_SUITE_RESULT FAIL error={}", t.toString(), t);
        }
    }

    private static void poll(int ownerId, long deadline) {
        BotQaSuiteRunner.SuiteResult result = BotQaSuiteRunner.status(ownerId);
        String phase = result.phase();
        if ("complete".equalsIgnoreCase(phase)) {
            boolean pass = result.success() && result.failed() == 0;
            log.info("SOLOMAPLING_QA_SUITE_RESULT {} phase={} passed={} failed={} skipped={} elapsedMs={} reason={} stages={}",
                    pass ? "PASS" : "FAIL", phase, result.passed(), result.failed(), result.skipped(),
                    result.elapsedMs(), result.reason(), result.stageSummary());
            cleanup(ownerId);
            return;
        }
        if ("failed".equalsIgnoreCase(phase) || "stopped".equalsIgnoreCase(phase)) {
            log.error("SOLOMAPLING_QA_SUITE_RESULT FAIL phase={} passed={} failed={} skipped={} elapsedMs={} reason={} stages={}",
                    phase, result.passed(), result.failed(), result.skipped(), result.elapsedMs(),
                    result.reason(), result.stageSummary());
            cleanup(ownerId);
            return;
        }
        if (System.currentTimeMillis() >= deadline) {
            log.error("SOLOMAPLING_QA_SUITE_RESULT FAIL reason=timeout phase={} passed={} failed={} skipped={} stages={}",
                    phase, result.passed(), result.failed(), result.skipped(), result.stageSummary());
            cleanup(ownerId);
            return;
        }
        log.info("SOLOMAPLING_QA_SUITE_STATUS phase={} passed={} failed={} skipped={} elapsedMs={}",
                phase, result.passed(), result.failed(), result.skipped(), result.elapsedMs());
        TimerManager.getInstance().schedule(() -> poll(ownerId, deadline), POLL_MS);
    }

    private static void cleanup(int ownerId) {
        if (BotQaSuiteRunner.isRunning(ownerId)) BotQaSuiteRunner.stop(ownerId);
        BotQaFleet.remove(ownerId);
    }

    private static Template findQaTemplate() throws Exception {
        String explicit = System.getenv("EVERLEAF_SOLOMAPLING_TEMPLATE_CHARACTER_ID");
        if (explicit != null && !explicit.isBlank()) {
            int characterId = Integer.parseInt(explicit.trim());
            try (Connection con = DatabaseConnection.getConnection();
                 PreparedStatement ps = con.prepareStatement(
                         "SELECT c.id, c.map FROM characters c JOIN accounts a ON a.id=c.accountid " +
                                 "WHERE c.id=? AND a.name LIKE 'qa\\_%' ESCAPE '\\\\' LIMIT 1")) {
                ps.setInt(1, characterId);
                try (ResultSet rs = ps.executeQuery()) {
                    if (rs.next()) return new Template(rs.getInt("id"), rs.getInt("map"));
                }
            }
            throw new IllegalStateException("explicit template is not owned by a qa_ account: " + characterId);
        }

        try (Connection con = DatabaseConnection.getConnection();
             PreparedStatement ps = con.prepareStatement(
                     "SELECT c.id, c.map FROM characters c JOIN accounts a ON a.id=c.accountid " +
                             "WHERE a.name LIKE 'qa\\_%' ESCAPE '\\\\' ORDER BY c.id LIMIT 1");
             ResultSet rs = ps.executeQuery()) {
            if (!rs.next()) throw new IllegalStateException("disposable QA DB has no qa_ character template");
            return new Template(rs.getInt("id"), rs.getInt("map"));
        }
    }

    private record Template(int characterId, int mapId) {}
}

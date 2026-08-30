package everleaf.progression;

import javax.sql.DataSource;
import java.sql.*;
import java.time.Instant;
import java.time.LocalDate;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

/** JDBC persistence for Everleaf enhanced-boss attempts and weekly reward ownership. */
public final class JdbcEncounterRepository implements EncounterRepository {
    private final DataSource dataSource;

    public JdbcEncounterRepository(DataSource dataSource) {
        if (dataSource == null) throw new IllegalArgumentException("dataSource cannot be null");
        this.dataSource = dataSource;
    }

    @Override
    public EncounterAttempt createAttempt(int accountId, int characterId, String encounterId, Instant startedAt) {
        String sql = "INSERT INTO everleaf_encounter_attempt "
                + "(account_id, character_id, encounter_id, started_at, result, weekly_reward_claimed) "
                + "VALUES (?, ?, ?, ?, 'IN_PROGRESS', 0)";
        try (Connection connection = dataSource.getConnection();
             PreparedStatement statement = connection.prepareStatement(sql, Statement.RETURN_GENERATED_KEYS)) {
            statement.setInt(1, accountId);
            statement.setInt(2, characterId);
            statement.setString(3, encounterId);
            statement.setTimestamp(4, Timestamp.from(startedAt));
            statement.executeUpdate();
            try (ResultSet keys = statement.getGeneratedKeys()) {
                if (!keys.next()) throw new SQLException("Missing generated encounter attempt id");
                return new EncounterAttempt(keys.getLong(1), accountId, characterId, encounterId,
                        startedAt, null, EncounterResult.IN_PROGRESS, false);
            }
        } catch (SQLException e) {
            throw new IllegalStateException("Failed to create Everleaf encounter attempt", e);
        }
    }

    @Override
    public Optional<EncounterAttempt> findAttempt(long attemptId) {
        String sql = "SELECT id, account_id, character_id, encounter_id, started_at, finished_at, result, "
                + "weekly_reward_claimed FROM everleaf_encounter_attempt WHERE id = ?";
        try (Connection connection = dataSource.getConnection();
             PreparedStatement statement = connection.prepareStatement(sql)) {
            statement.setLong(1, attemptId);
            try (ResultSet rs = statement.executeQuery()) {
                return rs.next() ? Optional.of(read(rs)) : Optional.empty();
            }
        } catch (SQLException e) {
            throw new IllegalStateException("Failed to load Everleaf encounter attempt", e);
        }
    }

    @Override
    public EncounterAttempt finishAttempt(long attemptId, EncounterResult result, Instant finishedAt) {
        if (result == EncounterResult.IN_PROGRESS) throw new IllegalArgumentException("cannot finish as IN_PROGRESS");
        String sql = "UPDATE everleaf_encounter_attempt SET result = ?, finished_at = ? "
                + "WHERE id = ? AND result = 'IN_PROGRESS'";
        try (Connection connection = dataSource.getConnection();
             PreparedStatement statement = connection.prepareStatement(sql)) {
            statement.setString(1, result.name());
            statement.setTimestamp(2, Timestamp.from(finishedAt));
            statement.setLong(3, attemptId);
            if (statement.executeUpdate() != 1) throw new IllegalStateException("attempt_already_finished");
            return findAttempt(attemptId).orElseThrow();
        } catch (SQLException e) {
            throw new IllegalStateException("Failed to finish Everleaf encounter attempt", e);
        }
    }

    @Override
    public boolean hasWeeklyRewardClaim(int accountId, String encounterId, LocalDate weekStartUtc) {
        String sql = "SELECT 1 FROM everleaf_encounter_weekly_reward "
                + "WHERE account_id = ? AND encounter_id = ? AND week_start_utc = ? LIMIT 1";
        try (Connection connection = dataSource.getConnection();
             PreparedStatement statement = connection.prepareStatement(sql)) {
            statement.setInt(1, accountId);
            statement.setString(2, encounterId);
            statement.setDate(3, Date.valueOf(weekStartUtc));
            try (ResultSet rs = statement.executeQuery()) {
                return rs.next();
            }
        } catch (SQLException e) {
            throw new IllegalStateException("Failed to check Everleaf weekly encounter reward", e);
        }
    }

    @Override
    public boolean markWeeklyRewardClaimed(long attemptId, LocalDate weekStartUtc, Instant claimedAt) {
        try (Connection connection = dataSource.getConnection()) {
            boolean originalAutoCommit = connection.getAutoCommit();
            connection.setAutoCommit(false);
            try {
                EncounterAttempt attempt = lockAttempt(connection, attemptId);
                if (attempt == null || !attempt.cleared() || attempt.weeklyRewardClaimed()) {
                    connection.rollback();
                    return false;
                }

                String insert = "INSERT IGNORE INTO everleaf_encounter_weekly_reward "
                        + "(account_id, encounter_id, week_start_utc, attempt_id, claimed_at) VALUES (?, ?, ?, ?, ?)";
                try (PreparedStatement statement = connection.prepareStatement(insert)) {
                    statement.setInt(1, attempt.accountId());
                    statement.setString(2, attempt.encounterId());
                    statement.setDate(3, Date.valueOf(weekStartUtc));
                    statement.setLong(4, attemptId);
                    statement.setTimestamp(5, Timestamp.from(claimedAt));
                    if (statement.executeUpdate() != 1) {
                        connection.rollback();
                        return false;
                    }
                }

                try (PreparedStatement statement = connection.prepareStatement(
                        "UPDATE everleaf_encounter_attempt SET weekly_reward_claimed = 1 WHERE id = ?")) {
                    statement.setLong(1, attemptId);
                    statement.executeUpdate();
                }
                connection.commit();
                return true;
            } catch (SQLException | RuntimeException e) {
                connection.rollback();
                throw e;
            } finally {
                connection.setAutoCommit(originalAutoCommit);
            }
        } catch (SQLException e) {
            throw new IllegalStateException("Failed to claim Everleaf weekly encounter reward", e);
        }
    }

    @Override
    public List<EncounterAttempt> recentAttempts(int characterId, int limit) {
        if (limit < 1) return List.of();
        String sql = "SELECT id, account_id, character_id, encounter_id, started_at, finished_at, result, "
                + "weekly_reward_claimed FROM everleaf_encounter_attempt WHERE character_id = ? "
                + "ORDER BY id DESC LIMIT ?";
        try (Connection connection = dataSource.getConnection();
             PreparedStatement statement = connection.prepareStatement(sql)) {
            statement.setInt(1, characterId);
            statement.setInt(2, limit);
            List<EncounterAttempt> attempts = new ArrayList<>();
            try (ResultSet rs = statement.executeQuery()) {
                while (rs.next()) attempts.add(read(rs));
            }
            return attempts;
        } catch (SQLException e) {
            throw new IllegalStateException("Failed to load recent Everleaf encounter attempts", e);
        }
    }

    private EncounterAttempt lockAttempt(Connection connection, long attemptId) throws SQLException {
        String sql = "SELECT id, account_id, character_id, encounter_id, started_at, finished_at, result, "
                + "weekly_reward_claimed FROM everleaf_encounter_attempt WHERE id = ? FOR UPDATE";
        try (PreparedStatement statement = connection.prepareStatement(sql)) {
            statement.setLong(1, attemptId);
            try (ResultSet rs = statement.executeQuery()) {
                return rs.next() ? read(rs) : null;
            }
        }
    }

    private static EncounterAttempt read(ResultSet rs) throws SQLException {
        Timestamp finished = rs.getTimestamp("finished_at");
        return new EncounterAttempt(
                rs.getLong("id"),
                rs.getInt("account_id"),
                rs.getInt("character_id"),
                rs.getString("encounter_id"),
                rs.getTimestamp("started_at").toInstant(),
                finished == null ? null : finished.toInstant(),
                EncounterResult.valueOf(rs.getString("result")),
                rs.getBoolean("weekly_reward_claimed")
        );
    }
}

package everleaf.progression;

import javax.sql.DataSource;
import java.sql.Connection;
import java.sql.Date;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Timestamp;
import java.time.Instant;
import java.time.LocalDate;
import java.util.Optional;

/** JDBC persistence for Everleaf's hybrid weekly progression model. */
public final class JdbcWeeklyProgressRepository implements WeeklyProgressRepository {
    private static final String WEEKLY_MARK_REASON = "WEEKLY_OBJECTIVE";

    private final DataSource dataSource;

    public JdbcWeeklyProgressRepository(DataSource dataSource) {
        if (dataSource == null) throw new IllegalArgumentException("dataSource cannot be null");
        this.dataSource = dataSource;
    }

    @Override
    public Optional<AccountWeeklyState> findAccountState(int accountId, LocalDate weekStartUtc) {
        String sql = "SELECT reward_points_claimed, catchup_points_bank FROM everleaf_weekly_account_state "
                + "WHERE account_id = ? AND week_start_utc = ?";
        try (Connection connection = dataSource.getConnection();
             PreparedStatement statement = connection.prepareStatement(sql)) {
            statement.setInt(1, accountId);
            statement.setDate(2, Date.valueOf(weekStartUtc));
            try (ResultSet rs = statement.executeQuery()) {
                if (!rs.next()) return Optional.empty();
                return Optional.of(new AccountWeeklyState(
                        accountId,
                        weekStartUtc,
                        rs.getInt("reward_points_claimed"),
                        rs.getInt("catchup_points_bank")
                ));
            }
        } catch (SQLException e) {
            throw new IllegalStateException("Failed to load Everleaf account weekly state", e);
        }
    }

    @Override
    public AccountWeeklyState saveAccountState(AccountWeeklyState state) {
        String sql = "INSERT INTO everleaf_weekly_account_state "
                + "(account_id, week_start_utc, reward_points_claimed, catchup_points_bank) VALUES (?, ?, ?, ?) "
                + "ON DUPLICATE KEY UPDATE reward_points_claimed = VALUES(reward_points_claimed), "
                + "catchup_points_bank = VALUES(catchup_points_bank)";
        try (Connection connection = dataSource.getConnection();
             PreparedStatement statement = connection.prepareStatement(sql)) {
            bindAccountState(statement, state);
            statement.executeUpdate();
            return state;
        } catch (SQLException e) {
            throw new IllegalStateException("Failed to save Everleaf account weekly state", e);
        }
    }

    @Override
    public Optional<CharacterObjectiveState> findCharacterObjective(
            int characterId,
            LocalDate weekStartUtc,
            String objectiveId
    ) {
        String sql = "SELECT progress_count, completed_at, claimed_at FROM everleaf_weekly_character_objective "
                + "WHERE character_id = ? AND week_start_utc = ? AND objective_id = ?";
        try (Connection connection = dataSource.getConnection();
             PreparedStatement statement = connection.prepareStatement(sql)) {
            statement.setInt(1, characterId);
            statement.setDate(2, Date.valueOf(weekStartUtc));
            statement.setString(3, objectiveId);
            try (ResultSet rs = statement.executeQuery()) {
                if (!rs.next()) return Optional.empty();
                return Optional.of(readCharacterState(characterId, weekStartUtc, objectiveId, rs));
            }
        } catch (SQLException e) {
            throw new IllegalStateException("Failed to load Everleaf character objective state", e);
        }
    }

    @Override
    public CharacterObjectiveState saveCharacterObjective(CharacterObjectiveState state) {
        String sql = "INSERT INTO everleaf_weekly_character_objective "
                + "(character_id, week_start_utc, objective_id, progress_count, completed_at, claimed_at) "
                + "VALUES (?, ?, ?, ?, ?, ?) ON DUPLICATE KEY UPDATE progress_count = VALUES(progress_count), "
                + "completed_at = VALUES(completed_at), claimed_at = VALUES(claimed_at)";
        try (Connection connection = dataSource.getConnection();
             PreparedStatement statement = connection.prepareStatement(sql)) {
            bindCharacterState(statement, state);
            statement.executeUpdate();
            return state;
        } catch (SQLException e) {
            throw new IllegalStateException("Failed to save Everleaf character objective state", e);
        }
    }

    @Override
    public ClaimCommitResult commitClaim(
            int accountId,
            int characterId,
            LocalDate weekStartUtc,
            String objectiveId,
            int pointsToAward,
            int maximumAccountPoints,
            Instant claimedAt
    ) {
        try (Connection connection = dataSource.getConnection()) {
            boolean originalAutoCommit = connection.getAutoCommit();
            connection.setAutoCommit(false);
            try {
                CharacterObjectiveState objective = lockObjective(connection, characterId, weekStartUtc, objectiveId);
                if (objective == null || !objective.completed()) {
                    connection.rollback();
                    return ClaimCommitResult.rejected("not_complete");
                }
                if (objective.claimed()) {
                    connection.rollback();
                    return ClaimCommitResult.rejected("already_claimed");
                }

                AccountWeeklyState account = lockOrCreateAccount(connection, accountId, weekStartUtc);
                int remaining = Math.max(0, maximumAccountPoints - account.rewardPointsClaimed());
                int awarded = Math.min(pointsToAward, remaining);
                if (awarded <= 0) {
                    connection.rollback();
                    return ClaimCommitResult.rejected("account_budget_exhausted");
                }

                VerdantBalance balance = lockOrCreateVerdantBalance(connection, accountId);
                int nextBalance = Math.addExact(balance.balance(), awarded);
                String reasonKey = weekStartUtc + ":" + characterId + ":" + objectiveId;

                // Weekly accounting, currency minting, ledger audit, and objective
                // claiming commit together. A crash can never award Marks without
                // consuming the claim (or consume the claim without awarding Marks).
                updateClaimedPoints(connection, accountId, weekStartUtc, account.rewardPointsClaimed() + awarded);
                creditVerdantMarks(connection, accountId, awarded, nextBalance);
                insertVerdantLedger(connection, accountId, characterId, awarded, nextBalance, reasonKey, objectiveId);
                markClaimed(connection, characterId, weekStartUtc, objectiveId, claimedAt);

                connection.commit();
                return ClaimCommitResult.committed(awarded);
            } catch (SQLException | RuntimeException e) {
                connection.rollback();
                throw e;
            } finally {
                connection.setAutoCommit(originalAutoCommit);
            }
        } catch (SQLException e) {
            throw new IllegalStateException("Failed to atomically claim Everleaf weekly reward", e);
        }
    }

    private CharacterObjectiveState lockObjective(Connection connection, int characterId, LocalDate week, String objectiveId)
            throws SQLException {
        String sql = "SELECT progress_count, completed_at, claimed_at FROM everleaf_weekly_character_objective "
                + "WHERE character_id = ? AND week_start_utc = ? AND objective_id = ? FOR UPDATE";
        try (PreparedStatement statement = connection.prepareStatement(sql)) {
            statement.setInt(1, characterId);
            statement.setDate(2, Date.valueOf(week));
            statement.setString(3, objectiveId);
            try (ResultSet rs = statement.executeQuery()) {
                return rs.next() ? readCharacterState(characterId, week, objectiveId, rs) : null;
            }
        }
    }

    private AccountWeeklyState lockOrCreateAccount(Connection connection, int accountId, LocalDate week) throws SQLException {
        String insert = "INSERT IGNORE INTO everleaf_weekly_account_state "
                + "(account_id, week_start_utc, reward_points_claimed, catchup_points_bank) VALUES (?, ?, 0, 0)";
        try (PreparedStatement statement = connection.prepareStatement(insert)) {
            statement.setInt(1, accountId);
            statement.setDate(2, Date.valueOf(week));
            statement.executeUpdate();
        }

        String select = "SELECT reward_points_claimed, catchup_points_bank FROM everleaf_weekly_account_state "
                + "WHERE account_id = ? AND week_start_utc = ? FOR UPDATE";
        try (PreparedStatement statement = connection.prepareStatement(select)) {
            statement.setInt(1, accountId);
            statement.setDate(2, Date.valueOf(week));
            try (ResultSet rs = statement.executeQuery()) {
                if (!rs.next()) throw new SQLException("Unable to lock Everleaf account weekly row");
                return new AccountWeeklyState(accountId, week,
                        rs.getInt("reward_points_claimed"), rs.getInt("catchup_points_bank"));
            }
        }
    }

    private VerdantBalance lockOrCreateVerdantBalance(Connection connection, int accountId) throws SQLException {
        try (PreparedStatement statement = connection.prepareStatement(
                "INSERT IGNORE INTO everleaf_verdant_mark_balance (account_id, balance, lifetime_earned, lifetime_spent) VALUES (?, 0, 0, 0)")) {
            statement.setInt(1, accountId);
            statement.executeUpdate();
        }

        try (PreparedStatement statement = connection.prepareStatement(
                "SELECT balance, lifetime_earned FROM everleaf_verdant_mark_balance WHERE account_id = ? FOR UPDATE")) {
            statement.setInt(1, accountId);
            try (ResultSet rs = statement.executeQuery()) {
                if (!rs.next()) throw new SQLException("Unable to lock Everleaf Verdant Marks balance");
                return new VerdantBalance(rs.getInt("balance"), rs.getLong("lifetime_earned"));
            }
        }
    }

    private void updateClaimedPoints(Connection connection, int accountId, LocalDate week, int points) throws SQLException {
        String sql = "UPDATE everleaf_weekly_account_state SET reward_points_claimed = ? "
                + "WHERE account_id = ? AND week_start_utc = ?";
        try (PreparedStatement statement = connection.prepareStatement(sql)) {
            statement.setInt(1, points);
            statement.setInt(2, accountId);
            statement.setDate(3, Date.valueOf(week));
            statement.executeUpdate();
        }
    }

    private void creditVerdantMarks(Connection connection, int accountId, int awarded, int nextBalance) throws SQLException {
        String sql = "UPDATE everleaf_verdant_mark_balance SET balance = ?, lifetime_earned = lifetime_earned + ? WHERE account_id = ?";
        try (PreparedStatement statement = connection.prepareStatement(sql)) {
            statement.setInt(1, nextBalance);
            statement.setInt(2, awarded);
            statement.setInt(3, accountId);
            if (statement.executeUpdate() != 1) throw new SQLException("Unable to update Verdant Marks balance");
        }
    }

    private void insertVerdantLedger(
            Connection connection,
            int accountId,
            int characterId,
            int awarded,
            int nextBalance,
            String reasonKey,
            String objectiveId
    ) throws SQLException {
        String sql = "INSERT INTO everleaf_verdant_mark_ledger "
                + "(account_id, character_id, amount, balance_after, reason_type, reason_key, metadata) "
                + "VALUES (?, ?, ?, ?, ?, ?, ?)";
        try (PreparedStatement statement = connection.prepareStatement(sql)) {
            statement.setInt(1, accountId);
            statement.setInt(2, characterId);
            statement.setInt(3, awarded);
            statement.setInt(4, nextBalance);
            statement.setString(5, WEEKLY_MARK_REASON);
            statement.setString(6, reasonKey);
            statement.setString(7, "objective=" + objectiveId);
            statement.executeUpdate();
        }
    }

    private void markClaimed(Connection connection, int characterId, LocalDate week, String objectiveId, Instant claimedAt)
            throws SQLException {
        String sql = "UPDATE everleaf_weekly_character_objective SET claimed_at = ? "
                + "WHERE character_id = ? AND week_start_utc = ? AND objective_id = ? AND claimed_at IS NULL";
        try (PreparedStatement statement = connection.prepareStatement(sql)) {
            statement.setTimestamp(1, Timestamp.from(claimedAt));
            statement.setInt(2, characterId);
            statement.setDate(3, Date.valueOf(week));
            statement.setString(4, objectiveId);
            if (statement.executeUpdate() != 1) {
                throw new SQLException("Everleaf weekly objective claim lost a concurrency race");
            }
        }
    }

    private static void bindAccountState(PreparedStatement statement, AccountWeeklyState state) throws SQLException {
        statement.setInt(1, state.accountId());
        statement.setDate(2, Date.valueOf(state.weekStartUtc()));
        statement.setInt(3, state.rewardPointsClaimed());
        statement.setInt(4, state.catchupPointsBank());
    }

    private static void bindCharacterState(PreparedStatement statement, CharacterObjectiveState state) throws SQLException {
        statement.setInt(1, state.characterId());
        statement.setDate(2, Date.valueOf(state.weekStartUtc()));
        statement.setString(3, state.objectiveId());
        statement.setInt(4, state.progressCount());
        statement.setTimestamp(5, state.completedAt() == null ? null : Timestamp.from(state.completedAt()));
        statement.setTimestamp(6, state.claimedAt() == null ? null : Timestamp.from(state.claimedAt()));
    }

    private static CharacterObjectiveState readCharacterState(
            int characterId,
            LocalDate week,
            String objectiveId,
            ResultSet rs
    ) throws SQLException {
        Timestamp completed = rs.getTimestamp("completed_at");
        Timestamp claimed = rs.getTimestamp("claimed_at");
        return new CharacterObjectiveState(
                characterId,
                week,
                objectiveId,
                rs.getInt("progress_count"),
                completed == null ? null : completed.toInstant(),
                claimed == null ? null : claimed.toInstant()
        );
    }

    private record VerdantBalance(int balance, long lifetimeEarned) {
    }
}

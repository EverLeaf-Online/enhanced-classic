package everleaf.progression;

import javax.sql.DataSource;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.sql.Timestamp;
import java.util.ArrayList;
import java.util.List;

/** JDBC PQ Point repository with account row locking and immutable ledger entries. */
public final class JdbcPqPointRepository implements PqPointRepository {
    private final DataSource dataSource;

    public JdbcPqPointRepository(DataSource dataSource) {
        if (dataSource == null) throw new IllegalArgumentException("dataSource cannot be null");
        this.dataSource = dataSource;
    }

    @Override
    public PqPointAccount getAccount(int accountId) {
        try (Connection connection = dataSource.getConnection()) {
            ensureAccountRow(connection, accountId);
            String sql = "SELECT balance, lifetime_earned, lifetime_spent FROM everleaf_pq_point_balance WHERE account_id = ?";
            try (PreparedStatement ps = connection.prepareStatement(sql)) {
                ps.setInt(1, accountId);
                try (ResultSet rs = ps.executeQuery()) {
                    if (!rs.next()) throw new SQLException("PQ Point balance row missing");
                    return new PqPointAccount(
                            accountId,
                            rs.getInt("balance"),
                            rs.getLong("lifetime_earned"),
                            rs.getLong("lifetime_spent")
                    );
                }
            }
        } catch (SQLException e) {
            throw new IllegalStateException("Failed to load PQ Point balance", e);
        }
    }

    @Override
    public MutationResult credit(int accountId, Integer characterId, int amount, String reasonType, String reasonKey, String metadata) {
        if (amount <= 0) throw new IllegalArgumentException("amount must be positive");
        return mutate(accountId, characterId, amount, reasonType, reasonKey, metadata, false);
    }

    @Override
    public MutationResult spend(int accountId, Integer characterId, int amount, String reasonType, String reasonKey, String metadata) {
        if (amount <= 0) throw new IllegalArgumentException("amount must be positive");
        return mutate(accountId, characterId, -amount, reasonType, reasonKey, metadata, true);
    }

    private MutationResult mutate(
            int accountId,
            Integer characterId,
            int delta,
            String reasonType,
            String reasonKey,
            String metadata,
            boolean spending
    ) {
        try (Connection connection = dataSource.getConnection()) {
            boolean oldAutoCommit = connection.getAutoCommit();
            connection.setAutoCommit(false);
            try {
                ensureAccountRow(connection, accountId);
                PqPointAccount current = lockAccount(connection, accountId);
                if (spending && current.balance() < -delta) {
                    connection.rollback();
                    return MutationResult.rejected("insufficient_balance", current.balance());
                }

                int nextBalance = Math.addExact(current.balance(), delta);
                String update = spending
                        ? "UPDATE everleaf_pq_point_balance SET balance = ?, lifetime_spent = lifetime_spent + ? WHERE account_id = ?"
                        : "UPDATE everleaf_pq_point_balance SET balance = ?, lifetime_earned = lifetime_earned + ? WHERE account_id = ?";
                try (PreparedStatement ps = connection.prepareStatement(update)) {
                    ps.setInt(1, nextBalance);
                    ps.setInt(2, Math.abs(delta));
                    ps.setInt(3, accountId);
                    ps.executeUpdate();
                }

                String ledger = "INSERT INTO everleaf_pq_point_ledger " +
                        "(account_id, character_id, amount, balance_after, reason_type, reason_key, metadata) " +
                        "VALUES (?, ?, ?, ?, ?, ?, ?)";
                try (PreparedStatement ps = connection.prepareStatement(ledger, Statement.RETURN_GENERATED_KEYS)) {
                    ps.setInt(1, accountId);
                    if (characterId == null) ps.setNull(2, java.sql.Types.INTEGER); else ps.setInt(2, characterId);
                    ps.setInt(3, delta);
                    ps.setInt(4, nextBalance);
                    ps.setString(5, reasonType);
                    ps.setString(6, reasonKey);
                    ps.setString(7, metadata);
                    ps.executeUpdate();
                }

                connection.commit();
                return MutationResult.success(Math.abs(delta), nextBalance);
            } catch (SQLException e) {
                connection.rollback();
                if (isDuplicateKey(e)) {
                    return MutationResult.rejected("duplicate_reason", getAccount(accountId).balance());
                }
                throw e;
            } finally {
                connection.setAutoCommit(oldAutoCommit);
            }
        } catch (SQLException e) {
            throw new IllegalStateException("Failed to mutate PQ Point balance", e);
        }
    }

    @Override
    public List<PqPointLedgerEntry> recentLedger(int accountId, int limit) {
        String sql = "SELECT id, character_id, amount, balance_after, reason_type, reason_key, metadata, created_at " +
                "FROM everleaf_pq_point_ledger WHERE account_id = ? ORDER BY id DESC LIMIT ?";
        try (Connection connection = dataSource.getConnection(); PreparedStatement ps = connection.prepareStatement(sql)) {
            ps.setInt(1, accountId);
            ps.setInt(2, limit);
            try (ResultSet rs = ps.executeQuery()) {
                List<PqPointLedgerEntry> rows = new ArrayList<>();
                while (rs.next()) {
                    Object character = rs.getObject("character_id");
                    Timestamp created = rs.getTimestamp("created_at");
                    rows.add(new PqPointLedgerEntry(
                            rs.getLong("id"),
                            accountId,
                            character == null ? null : ((Number) character).intValue(),
                            rs.getInt("amount"),
                            rs.getInt("balance_after"),
                            rs.getString("reason_type"),
                            rs.getString("reason_key"),
                            rs.getString("metadata"),
                            created.toInstant()
                    ));
                }
                return List.copyOf(rows);
            }
        } catch (SQLException e) {
            throw new IllegalStateException("Failed to load PQ Point ledger", e);
        }
    }

    private static void ensureAccountRow(Connection connection, int accountId) throws SQLException {
        try (PreparedStatement ps = connection.prepareStatement(
                "INSERT IGNORE INTO everleaf_pq_point_balance (account_id, balance, lifetime_earned, lifetime_spent) VALUES (?, 0, 0, 0)")) {
            ps.setInt(1, accountId);
            ps.executeUpdate();
        }
    }

    private static PqPointAccount lockAccount(Connection connection, int accountId) throws SQLException {
        try (PreparedStatement ps = connection.prepareStatement(
                "SELECT balance, lifetime_earned, lifetime_spent FROM everleaf_pq_point_balance WHERE account_id = ? FOR UPDATE")) {
            ps.setInt(1, accountId);
            try (ResultSet rs = ps.executeQuery()) {
                if (!rs.next()) throw new SQLException("Unable to lock PQ Point balance");
                return new PqPointAccount(
                        accountId,
                        rs.getInt("balance"),
                        rs.getLong("lifetime_earned"),
                        rs.getLong("lifetime_spent")
                );
            }
        }
    }

    private static boolean isDuplicateKey(SQLException e) {
        return "23000".equals(e.getSQLState()) && e.getErrorCode() == 1062;
    }
}

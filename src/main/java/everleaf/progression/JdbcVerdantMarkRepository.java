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

/** JDBC implementation with row locking and an immutable audit ledger. */
public final class JdbcVerdantMarkRepository implements VerdantMarkRepository {
    private final DataSource dataSource;

    public JdbcVerdantMarkRepository(DataSource dataSource) {
        if (dataSource == null) throw new IllegalArgumentException("dataSource cannot be null");
        this.dataSource = dataSource;
    }

    @Override
    public VerdantMarkAccount getAccount(int accountId) {
        try (Connection connection = dataSource.getConnection()) {
            ensureAccountRow(connection, accountId);
            String sql = "SELECT balance, lifetime_earned, lifetime_spent FROM everleaf_verdant_mark_balance WHERE account_id = ?";
            try (PreparedStatement ps = connection.prepareStatement(sql)) {
                ps.setInt(1, accountId);
                try (ResultSet rs = ps.executeQuery()) {
                    if (!rs.next()) throw new SQLException("Verdant Marks balance row missing");
                    return new VerdantMarkAccount(accountId, rs.getInt("balance"), rs.getLong("lifetime_earned"), rs.getLong("lifetime_spent"));
                }
            }
        } catch (SQLException e) {
            throw new IllegalStateException("Failed to load Verdant Marks balance", e);
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

    private MutationResult mutate(int accountId, Integer characterId, int delta, String reasonType, String reasonKey, String metadata, boolean spending) {
        try (Connection connection = dataSource.getConnection()) {
            boolean oldAutoCommit = connection.getAutoCommit();
            connection.setAutoCommit(false);
            try {
                ensureAccountRow(connection, accountId);
                VerdantMarkAccount current = lockAccount(connection, accountId);
                if (spending && current.balance() < -delta) {
                    connection.rollback();
                    return MutationResult.rejected("insufficient_balance", current.balance());
                }

                int nextBalance = Math.addExact(current.balance(), delta);
                String update = spending
                        ? "UPDATE everleaf_verdant_mark_balance SET balance = ?, lifetime_spent = lifetime_spent + ? WHERE account_id = ?"
                        : "UPDATE everleaf_verdant_mark_balance SET balance = ?, lifetime_earned = lifetime_earned + ? WHERE account_id = ?";
                try (PreparedStatement ps = connection.prepareStatement(update)) {
                    ps.setInt(1, nextBalance);
                    ps.setInt(2, Math.abs(delta));
                    ps.setInt(3, accountId);
                    ps.executeUpdate();
                }

                String ledger = "INSERT INTO everleaf_verdant_mark_ledger (account_id, character_id, amount, balance_after, reason_type, reason_key, metadata) VALUES (?, ?, ?, ?, ?, ?, ?)";
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
                if (isDuplicateKey(e)) return MutationResult.rejected("duplicate_reason", getAccount(accountId).balance());
                throw e;
            } finally {
                connection.setAutoCommit(oldAutoCommit);
            }
        } catch (SQLException e) {
            throw new IllegalStateException("Failed to mutate Verdant Marks balance", e);
        }
    }

    @Override
    public List<VerdantMarkLedgerEntry> recentLedger(int accountId, int limit) {
        String sql = "SELECT id, character_id, amount, balance_after, reason_type, reason_key, metadata, created_at FROM everleaf_verdant_mark_ledger WHERE account_id = ? ORDER BY id DESC LIMIT ?";
        try (Connection connection = dataSource.getConnection(); PreparedStatement ps = connection.prepareStatement(sql)) {
            ps.setInt(1, accountId);
            ps.setInt(2, limit);
            try (ResultSet rs = ps.executeQuery()) {
                List<VerdantMarkLedgerEntry> rows = new ArrayList<>();
                while (rs.next()) {
                    Object character = rs.getObject("character_id");
                    Timestamp created = rs.getTimestamp("created_at");
                    rows.add(new VerdantMarkLedgerEntry(
                            rs.getLong("id"), accountId, character == null ? null : ((Number) character).intValue(),
                            rs.getInt("amount"), rs.getInt("balance_after"), rs.getString("reason_type"),
                            rs.getString("reason_key"), rs.getString("metadata"), created.toInstant()
                    ));
                }
                return List.copyOf(rows);
            }
        } catch (SQLException e) {
            throw new IllegalStateException("Failed to load Verdant Marks ledger", e);
        }
    }

    private static void ensureAccountRow(Connection connection, int accountId) throws SQLException {
        try (PreparedStatement ps = connection.prepareStatement(
                "INSERT IGNORE INTO everleaf_verdant_mark_balance (account_id, balance, lifetime_earned, lifetime_spent) VALUES (?, 0, 0, 0)")) {
            ps.setInt(1, accountId);
            ps.executeUpdate();
        }
    }

    private static VerdantMarkAccount lockAccount(Connection connection, int accountId) throws SQLException {
        try (PreparedStatement ps = connection.prepareStatement(
                "SELECT balance, lifetime_earned, lifetime_spent FROM everleaf_verdant_mark_balance WHERE account_id = ? FOR UPDATE")) {
            ps.setInt(1, accountId);
            try (ResultSet rs = ps.executeQuery()) {
                if (!rs.next()) throw new SQLException("Unable to lock Verdant Marks balance");
                return new VerdantMarkAccount(accountId, rs.getInt("balance"), rs.getLong("lifetime_earned"), rs.getLong("lifetime_spent"));
            }
        }
    }

    private static boolean isDuplicateKey(SQLException e) {
        return "23000".equals(e.getSQLState()) && e.getErrorCode() == 1062;
    }
}

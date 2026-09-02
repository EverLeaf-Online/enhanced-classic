package everleaf.progression;

import javax.sql.DataSource;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.EnumMap;
import java.util.Map;

/** JDBC storage with row locks and idempotent reason keys. */
public final class JdbcRootedMaterialRepository implements RootedMaterialRepository {
    private final DataSource dataSource;

    public JdbcRootedMaterialRepository(DataSource dataSource) {
        if (dataSource == null) throw new IllegalArgumentException("dataSource cannot be null");
        this.dataSource = dataSource;
    }

    @Override
    public Map<RootedMaterial, Integer> balances(int accountId) {
        EnumMap<RootedMaterial, Integer> result = new EnumMap<>(RootedMaterial.class);
        for (RootedMaterial material : RootedMaterial.values()) result.put(material, 0);

        String sql = "SELECT material, balance FROM everleaf_rooted_material_balance WHERE account_id = ?";
        try (Connection connection = dataSource.getConnection(); PreparedStatement ps = connection.prepareStatement(sql)) {
            ps.setInt(1, accountId);
            try (ResultSet rs = ps.executeQuery()) {
                while (rs.next()) {
                    result.put(RootedMaterial.valueOf(rs.getString("material")), rs.getInt("balance"));
                }
            }
            return Map.copyOf(result);
        } catch (SQLException e) {
            throw new IllegalStateException("Failed to load Rooted material balances", e);
        }
    }

    @Override
    public MutationResult credit(int accountId, int characterId, RootedMaterial material, int amount, String reasonKey) {
        if (amount <= 0) throw new IllegalArgumentException("amount must be positive");
        return mutate(accountId, characterId, material, amount, reasonKey, false);
    }

    @Override
    public MutationResult spend(int accountId, int characterId, RootedMaterial material, int amount, String reasonKey) {
        if (amount <= 0) throw new IllegalArgumentException("amount must be positive");
        return mutate(accountId, characterId, material, -amount, reasonKey, true);
    }

    private MutationResult mutate(int accountId, int characterId, RootedMaterial material, int delta, String reasonKey, boolean spending) {
        if (material == null) throw new IllegalArgumentException("material cannot be null");
        if (reasonKey == null || reasonKey.isBlank()) throw new IllegalArgumentException("reasonKey cannot be blank");

        try (Connection connection = dataSource.getConnection()) {
            boolean oldAutoCommit = connection.getAutoCommit();
            connection.setAutoCommit(false);
            try {
                ensureBalanceRow(connection, accountId, material);
                int current = lockBalance(connection, accountId, material);
                if (spending && current < -delta) {
                    connection.rollback();
                    return MutationResult.rejected("insufficient_balance", current);
                }

                int next = Math.addExact(current, delta);
                String update = spending
                        ? "UPDATE everleaf_rooted_material_balance SET balance = ?, lifetime_spent = lifetime_spent + ? WHERE account_id = ? AND material = ?"
                        : "UPDATE everleaf_rooted_material_balance SET balance = ?, lifetime_earned = lifetime_earned + ? WHERE account_id = ? AND material = ?";
                try (PreparedStatement ps = connection.prepareStatement(update)) {
                    ps.setInt(1, next);
                    ps.setInt(2, Math.abs(delta));
                    ps.setInt(3, accountId);
                    ps.setString(4, material.name());
                    ps.executeUpdate();
                }

                try (PreparedStatement ps = connection.prepareStatement(
                        "INSERT INTO everleaf_rooted_material_ledger (account_id, character_id, material, amount, balance_after, reason_key) VALUES (?, ?, ?, ?, ?, ?)")) {
                    ps.setInt(1, accountId);
                    ps.setInt(2, characterId);
                    ps.setString(3, material.name());
                    ps.setInt(4, delta);
                    ps.setInt(5, next);
                    ps.setString(6, reasonKey);
                    ps.executeUpdate();
                }

                connection.commit();
                return MutationResult.success(next);
            } catch (SQLException e) {
                connection.rollback();
                if (isDuplicateKey(e)) {
                    return MutationResult.rejected("duplicate_reason", currentBalance(accountId, material));
                }
                throw e;
            } finally {
                connection.setAutoCommit(oldAutoCommit);
            }
        } catch (SQLException e) {
            throw new IllegalStateException("Failed to mutate Rooted material balance", e);
        }
    }

    private static void ensureBalanceRow(Connection connection, int accountId, RootedMaterial material) throws SQLException {
        try (PreparedStatement ps = connection.prepareStatement(
                "INSERT IGNORE INTO everleaf_rooted_material_balance (account_id, material, balance, lifetime_earned, lifetime_spent) VALUES (?, ?, 0, 0, 0)")) {
            ps.setInt(1, accountId);
            ps.setString(2, material.name());
            ps.executeUpdate();
        }
    }

    private static int lockBalance(Connection connection, int accountId, RootedMaterial material) throws SQLException {
        try (PreparedStatement ps = connection.prepareStatement(
                "SELECT balance FROM everleaf_rooted_material_balance WHERE account_id = ? AND material = ? FOR UPDATE")) {
            ps.setInt(1, accountId);
            ps.setString(2, material.name());
            try (ResultSet rs = ps.executeQuery()) {
                if (!rs.next()) throw new SQLException("Unable to lock Rooted material balance");
                return rs.getInt("balance");
            }
        }
    }

    private int currentBalance(int accountId, RootedMaterial material) {
        return balances(accountId).getOrDefault(material, 0);
    }

    private static boolean isDuplicateKey(SQLException e) {
        return "23000".equals(e.getSQLState()) && e.getErrorCode() == 1062;
    }
}

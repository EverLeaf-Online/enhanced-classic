package everleaf.progression;

import javax.sql.DataSource;
import java.sql.*;
import java.time.Instant;
import java.util.Comparator;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

/**
 * Pays every forge input and creates its fulfillment order in one transaction.
 * The pending order is the recovery source if inventory delivery is interrupted.
 */
public final class JdbcRootedForgeRepository implements RootedForgeRepository {
    private final DataSource dataSource;

    public JdbcRootedForgeRepository(DataSource dataSource) {
        if (dataSource == null) throw new IllegalArgumentException("dataSource cannot be null");
        this.dataSource = dataSource;
    }

    @Override
    public PurchaseResult purchase(int accountId, int characterId, RootedForgeRecipe recipe, RootedForgeTarget target, String requestKey) {
        if (accountId <= 0 || characterId <= 0) throw new IllegalArgumentException("invalid account or character");
        if (recipe == null) throw new IllegalArgumentException("recipe cannot be null");
        if (target == null) throw new IllegalArgumentException("target cannot be null");
        if (requestKey == null || requestKey.isBlank()) throw new IllegalArgumentException("requestKey cannot be blank");

        try (Connection connection = dataSource.getConnection()) {
            boolean oldAutoCommit = connection.getAutoCommit();
            connection.setAutoCommit(false);
            try {
                ensureVerdantRow(connection, accountId);
                int marks = lockVerdantBalance(connection, accountId);
                if (marks < recipe.verdantMarkCost()) {
                    connection.rollback();
                    return PurchaseResult.rejected("insufficient_verdant_marks");
                }

                var costs = recipe.materialCosts().entrySet().stream()
                        .sorted(Comparator.comparing(entry -> entry.getKey().name()))
                        .toList();
                for (var cost : costs) {
                    ensureMaterialRow(connection, accountId, cost.getKey());
                    if (lockMaterialBalance(connection, accountId, cost.getKey()) < cost.getValue()) {
                        connection.rollback();
                        return PurchaseResult.rejected("insufficient_" + cost.getKey().name().toLowerCase());
                    }
                }

                long orderId = insertOrder(connection, accountId, characterId, recipe, target, requestKey);
                debitVerdant(connection, accountId, characterId, recipe, requestKey, marks);
                for (var cost : costs) {
                    debitMaterial(connection, accountId, characterId, cost.getKey(), cost.getValue(), requestKey);
                }
                connection.commit();
                return PurchaseResult.success(new RootedForgeOrder(
                        orderId, accountId, characterId, recipe, target, requestKey,
                        RootedForgeOrder.Status.PENDING, Instant.now()));
            } catch (SQLException e) {
                connection.rollback();
                if (isDuplicateKey(e)) {
                    return findByRequestKey(accountId, requestKey)
                            .map(PurchaseResult::duplicate)
                            .orElseGet(() -> PurchaseResult.rejected("duplicate_request"));
                }
                throw e;
            } finally {
                connection.setAutoCommit(oldAutoCommit);
            }
        } catch (SQLException e) {
            throw new IllegalStateException("Failed to purchase Rooted forge outcome", e);
        }
    }

    @Override
    public Optional<RootedForgeOrder> findByRequestKey(int accountId, String requestKey) {
        String sql = "SELECT id, character_id, recipe, target_item_id, target_inventory_type, target_slot, status, created_at FROM everleaf_rooted_forge_order WHERE account_id = ? AND request_key = ?";
        try (Connection connection = dataSource.getConnection(); PreparedStatement ps = connection.prepareStatement(sql)) {
            ps.setInt(1, accountId);
            ps.setString(2, requestKey);
            try (ResultSet rs = ps.executeQuery()) {
                if (!rs.next()) return Optional.empty();
                return Optional.of(new RootedForgeOrder(
                        rs.getLong("id"), accountId, rs.getInt("character_id"),
                        RootedForgeRecipe.valueOf(rs.getString("recipe")), readTarget(rs), requestKey,
                        RootedForgeOrder.Status.valueOf(rs.getString("status")),
                        rs.getTimestamp("created_at").toInstant()));
            }
        } catch (SQLException e) {
            throw new IllegalStateException("Failed to load Rooted forge order", e);
        }
    }

    @Override
    public Optional<RootedForgeOrder> findById(long orderId) {
        String sql = "SELECT account_id, character_id, recipe, target_item_id, target_inventory_type, target_slot, request_key, status, created_at FROM everleaf_rooted_forge_order WHERE id = ?";
        try (Connection connection = dataSource.getConnection(); PreparedStatement ps = connection.prepareStatement(sql)) {
            ps.setLong(1, orderId);
            try (ResultSet rs = ps.executeQuery()) {
                if (!rs.next()) return Optional.empty();
                return Optional.of(new RootedForgeOrder(
                        orderId, rs.getInt("account_id"), rs.getInt("character_id"),
                        RootedForgeRecipe.valueOf(rs.getString("recipe")), readTarget(rs), rs.getString("request_key"),
                        RootedForgeOrder.Status.valueOf(rs.getString("status")), rs.getTimestamp("created_at").toInstant()));
            }
        } catch (SQLException e) {
            throw new IllegalStateException("Failed to load Rooted forge order", e);
        }
    }

    @Override
    public List<RootedForgeOrder> pendingOrders(int limit) {
        if (limit < 1 || limit > 100) throw new IllegalArgumentException("limit must be 1-100");
        String sql = "SELECT id, account_id, character_id, recipe, target_item_id, target_inventory_type, "
                + "target_slot, request_key, status, created_at FROM everleaf_rooted_forge_order "
                + "WHERE status = 'PENDING' ORDER BY id ASC LIMIT ?";
        try (Connection connection = dataSource.getConnection(); PreparedStatement ps = connection.prepareStatement(sql)) {
            ps.setInt(1, limit);
            List<RootedForgeOrder> orders = new ArrayList<>();
            try (ResultSet rs = ps.executeQuery()) {
                while (rs.next()) {
                    orders.add(new RootedForgeOrder(
                            rs.getLong("id"), rs.getInt("account_id"), rs.getInt("character_id"),
                            RootedForgeRecipe.valueOf(rs.getString("recipe")), readTarget(rs),
                            rs.getString("request_key"), RootedForgeOrder.Status.valueOf(rs.getString("status")),
                            rs.getTimestamp("created_at").toInstant()));
                }
            }
            return List.copyOf(orders);
        } catch (SQLException e) {
            throw new IllegalStateException("Failed to list pending Rooted forge orders", e);
        }
    }

    @Override
    public boolean markFulfilled(long orderId) {
        try (Connection connection = dataSource.getConnection(); PreparedStatement ps = connection.prepareStatement(
                "UPDATE everleaf_rooted_forge_order SET status = 'FULFILLED', fulfilled_at = CURRENT_TIMESTAMP WHERE id = ? AND status = 'PENDING'")) {
            ps.setLong(1, orderId);
            return ps.executeUpdate() == 1;
        } catch (SQLException e) {
            throw new IllegalStateException("Failed to complete Rooted forge order", e);
        }
    }

    private static long insertOrder(Connection c, int accountId, int characterId, RootedForgeRecipe recipe, RootedForgeTarget target, String requestKey) throws SQLException {
        String sql = "INSERT INTO everleaf_rooted_forge_order (account_id, character_id, recipe, target_item_id, target_inventory_type, target_slot, request_key, status) VALUES (?, ?, ?, ?, ?, ?, ?, 'PENDING')";
        try (PreparedStatement ps = c.prepareStatement(sql, Statement.RETURN_GENERATED_KEYS)) {
            ps.setInt(1, accountId); ps.setInt(2, characterId); ps.setString(3, recipe.name());
            ps.setInt(4, target.itemId()); ps.setInt(5, target.inventoryType().getType()); ps.setInt(6, target.slot()); ps.setString(7, requestKey);
            ps.executeUpdate();
            try (ResultSet keys = ps.getGeneratedKeys()) {
                if (!keys.next()) throw new SQLException("Missing Rooted forge order id");
                return keys.getLong(1);
            }
        }
    }

    private static RootedForgeTarget readTarget(ResultSet rs) throws SQLException {
        return new RootedForgeTarget(
                rs.getInt("target_item_id"),
                client.inventory.InventoryType.getByType(rs.getByte("target_inventory_type")),
                rs.getShort("target_slot"));
    }

    private static void ensureVerdantRow(Connection c, int accountId) throws SQLException {
        try (PreparedStatement ps = c.prepareStatement("INSERT IGNORE INTO everleaf_verdant_mark_balance (account_id, balance, lifetime_earned, lifetime_spent) VALUES (?, 0, 0, 0)")) {
            ps.setInt(1, accountId); ps.executeUpdate();
        }
    }

    private static int lockVerdantBalance(Connection c, int accountId) throws SQLException {
        try (PreparedStatement ps = c.prepareStatement("SELECT balance FROM everleaf_verdant_mark_balance WHERE account_id = ? FOR UPDATE")) {
            ps.setInt(1, accountId);
            try (ResultSet rs = ps.executeQuery()) { if (!rs.next()) throw new SQLException("Missing Verdant balance"); return rs.getInt(1); }
        }
    }

    private static void ensureMaterialRow(Connection c, int accountId, RootedMaterial material) throws SQLException {
        try (PreparedStatement ps = c.prepareStatement("INSERT IGNORE INTO everleaf_rooted_material_balance (account_id, material, balance, lifetime_earned, lifetime_spent) VALUES (?, ?, 0, 0, 0)")) {
            ps.setInt(1, accountId); ps.setString(2, material.name()); ps.executeUpdate();
        }
    }

    private static int lockMaterialBalance(Connection c, int accountId, RootedMaterial material) throws SQLException {
        try (PreparedStatement ps = c.prepareStatement("SELECT balance FROM everleaf_rooted_material_balance WHERE account_id = ? AND material = ? FOR UPDATE")) {
            ps.setInt(1, accountId); ps.setString(2, material.name());
            try (ResultSet rs = ps.executeQuery()) { if (!rs.next()) throw new SQLException("Missing Rooted material balance"); return rs.getInt(1); }
        }
    }

    private static void debitVerdant(Connection c, int accountId, int characterId, RootedForgeRecipe recipe, String requestKey, int current) throws SQLException {
        int cost = recipe.verdantMarkCost();
        try (PreparedStatement ps = c.prepareStatement("UPDATE everleaf_verdant_mark_balance SET balance = ?, lifetime_spent = lifetime_spent + ? WHERE account_id = ?")) {
            ps.setInt(1, current - cost); ps.setInt(2, cost); ps.setInt(3, accountId); ps.executeUpdate();
        }
        try (PreparedStatement ps = c.prepareStatement("INSERT INTO everleaf_verdant_mark_ledger (account_id, character_id, amount, balance_after, reason_type, reason_key, metadata) VALUES (?, ?, ?, ?, 'rooted_forge', ?, ?)")) {
            ps.setInt(1, accountId); ps.setInt(2, characterId); ps.setInt(3, -cost); ps.setInt(4, current - cost);
            ps.setString(5, requestKey); ps.setString(6, recipe.name()); ps.executeUpdate();
        }
    }

    private static void debitMaterial(Connection c, int accountId, int characterId, RootedMaterial material, int cost, String requestKey) throws SQLException {
        int current = lockMaterialBalance(c, accountId, material);
        try (PreparedStatement ps = c.prepareStatement("UPDATE everleaf_rooted_material_balance SET balance = ?, lifetime_spent = lifetime_spent + ? WHERE account_id = ? AND material = ?")) {
            ps.setInt(1, current - cost); ps.setInt(2, cost); ps.setInt(3, accountId); ps.setString(4, material.name()); ps.executeUpdate();
        }
        try (PreparedStatement ps = c.prepareStatement("INSERT INTO everleaf_rooted_material_ledger (account_id, character_id, material, amount, balance_after, reason_key) VALUES (?, ?, ?, ?, ?, ?)")) {
            ps.setInt(1, accountId); ps.setInt(2, characterId); ps.setString(3, material.name()); ps.setInt(4, -cost); ps.setInt(5, current - cost);
            ps.setString(6, "forge:" + requestKey); ps.executeUpdate();
        }
    }

    private static boolean isDuplicateKey(SQLException e) {
        return "23000".equals(e.getSQLState()) && e.getErrorCode() == 1062;
    }
}

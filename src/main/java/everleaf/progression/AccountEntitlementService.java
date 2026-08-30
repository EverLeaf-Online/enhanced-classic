package everleaf.progression;

import javax.sql.DataSource;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Timestamp;
import java.time.Duration;
import java.time.Instant;

/**
 * Persistence/service boundary for timed or permanent account QoL entitlements.
 * Timed grants extend from the later of now or the current expiry, preventing a
 * renewal from discarding already-paid time.
 */
public final class AccountEntitlementService {
    public static final String PET_VAC = "PET_VAC";

    private final DataSource dataSource;

    public AccountEntitlementService(DataSource dataSource) {
        if (dataSource == null) throw new IllegalArgumentException("dataSource cannot be null");
        this.dataSource = dataSource;
    }

    public boolean isActive(int accountId, String entitlementKey) {
        validateAccountAndKey(accountId, entitlementKey);
        String sql = "SELECT expires_at FROM everleaf_account_entitlement WHERE account_id = ? AND entitlement_key = ?";
        try (Connection connection = dataSource.getConnection(); PreparedStatement ps = connection.prepareStatement(sql)) {
            ps.setInt(1, accountId);
            ps.setString(2, entitlementKey);
            try (ResultSet rs = ps.executeQuery()) {
                if (!rs.next()) return false;
                Timestamp expiry = rs.getTimestamp("expires_at");
                return expiry == null || expiry.toInstant().isAfter(Instant.now());
            }
        } catch (SQLException e) {
            throw new IllegalStateException("Failed to read account entitlement", e);
        }
    }

    public Instant expiresAt(int accountId, String entitlementKey) {
        validateAccountAndKey(accountId, entitlementKey);
        String sql = "SELECT expires_at FROM everleaf_account_entitlement WHERE account_id = ? AND entitlement_key = ?";
        try (Connection connection = dataSource.getConnection(); PreparedStatement ps = connection.prepareStatement(sql)) {
            ps.setInt(1, accountId);
            ps.setString(2, entitlementKey);
            try (ResultSet rs = ps.executeQuery()) {
                if (!rs.next()) return null;
                Timestamp expiry = rs.getTimestamp("expires_at");
                return expiry == null ? Instant.MAX : expiry.toInstant();
            }
        } catch (SQLException e) {
            throw new IllegalStateException("Failed to read account entitlement expiry", e);
        }
    }

    public GrantResult grantTimed(
            int accountId,
            Integer characterId,
            String entitlementKey,
            Duration duration,
            String sourceType,
            String sourceKey,
            String metadata
    ) {
        validateAccountAndKey(accountId, entitlementKey);
        if (duration == null || duration.isZero() || duration.isNegative()) {
            throw new IllegalArgumentException("duration must be positive");
        }
        if (sourceType == null || sourceType.isBlank()) throw new IllegalArgumentException("sourceType cannot be blank");
        if (sourceKey == null || sourceKey.isBlank()) throw new IllegalArgumentException("sourceKey cannot be blank");

        try (Connection connection = dataSource.getConnection()) {
            boolean oldAutoCommit = connection.getAutoCommit();
            connection.setAutoCommit(false);
            try {
                if (sourceAlreadyApplied(connection, accountId, entitlementKey, sourceType, sourceKey)) {
                    connection.rollback();
                    return GrantResult.duplicate(expiresAt(accountId, entitlementKey));
                }

                // Establish a row that is safely expired rather than accidentally
                // permanent, then lock it for deterministic extension.
                try (PreparedStatement ps = connection.prepareStatement(
                        "INSERT IGNORE INTO everleaf_account_entitlement " +
                                "(account_id, entitlement_key, expires_at, metadata) VALUES (?, ?, CURRENT_TIMESTAMP, NULL)")) {
                    ps.setInt(1, accountId);
                    ps.setString(2, entitlementKey);
                    ps.executeUpdate();
                }

                Instant now = Instant.now();
                Instant oldExpiry = null;
                boolean permanent = false;
                try (PreparedStatement ps = connection.prepareStatement(
                        "SELECT expires_at FROM everleaf_account_entitlement " +
                                "WHERE account_id = ? AND entitlement_key = ? FOR UPDATE")) {
                    ps.setInt(1, accountId);
                    ps.setString(2, entitlementKey);
                    try (ResultSet rs = ps.executeQuery()) {
                        if (!rs.next()) throw new SQLException("Entitlement row missing after INSERT IGNORE");
                        Timestamp ts = rs.getTimestamp("expires_at");
                        if (ts == null) {
                            permanent = true;
                        } else {
                            oldExpiry = ts.toInstant();
                        }
                    }
                }

                if (permanent) {
                    connection.rollback();
                    return GrantResult.permanentResult();
                }

                Instant base = oldExpiry != null && oldExpiry.isAfter(now) ? oldExpiry : now;
                Instant newExpiry = base.plus(duration);

                try (PreparedStatement ps = connection.prepareStatement(
                        "UPDATE everleaf_account_entitlement SET expires_at = ?, metadata = ? " +
                                "WHERE account_id = ? AND entitlement_key = ?")) {
                    ps.setTimestamp(1, Timestamp.from(newExpiry));
                    ps.setString(2, metadata);
                    ps.setInt(3, accountId);
                    ps.setString(4, entitlementKey);
                    ps.executeUpdate();
                }

                try (PreparedStatement ps = connection.prepareStatement(
                        "INSERT INTO everleaf_account_entitlement_ledger " +
                                "(account_id, character_id, entitlement_key, action, source_type, source_key, old_expires_at, new_expires_at, metadata) " +
                                "VALUES (?, ?, ?, 'GRANT_TIMED', ?, ?, ?, ?, ?)")) {
                    ps.setInt(1, accountId);
                    if (characterId == null) ps.setNull(2, java.sql.Types.INTEGER); else ps.setInt(2, characterId);
                    ps.setString(3, entitlementKey);
                    ps.setString(4, sourceType);
                    ps.setString(5, sourceKey);
                    if (oldExpiry == null) ps.setNull(6, java.sql.Types.TIMESTAMP); else ps.setTimestamp(6, Timestamp.from(oldExpiry));
                    ps.setTimestamp(7, Timestamp.from(newExpiry));
                    ps.setString(8, metadata);
                    ps.executeUpdate();
                }

                connection.commit();
                return GrantResult.granted(newExpiry);
            } catch (SQLException e) {
                connection.rollback();
                if (isDuplicateKey(e)) return GrantResult.duplicate(expiresAt(accountId, entitlementKey));
                throw e;
            } finally {
                connection.setAutoCommit(oldAutoCommit);
            }
        } catch (SQLException e) {
            throw new IllegalStateException("Failed to grant account entitlement", e);
        }
    }

    private static boolean sourceAlreadyApplied(
            Connection connection,
            int accountId,
            String entitlementKey,
            String sourceType,
            String sourceKey
    ) throws SQLException {
        try (PreparedStatement ps = connection.prepareStatement(
                "SELECT 1 FROM everleaf_account_entitlement_ledger " +
                        "WHERE account_id = ? AND entitlement_key = ? AND source_type = ? AND source_key = ? LIMIT 1")) {
            ps.setInt(1, accountId);
            ps.setString(2, entitlementKey);
            ps.setString(3, sourceType);
            ps.setString(4, sourceKey);
            try (ResultSet rs = ps.executeQuery()) {
                return rs.next();
            }
        }
    }

    private static void validateAccountAndKey(int accountId, String entitlementKey) {
        if (accountId <= 0) throw new IllegalArgumentException("accountId must be positive");
        if (entitlementKey == null || entitlementKey.isBlank()) {
            throw new IllegalArgumentException("entitlementKey cannot be blank");
        }
    }

    private static boolean isDuplicateKey(SQLException e) {
        return "23000".equals(e.getSQLState()) && e.getErrorCode() == 1062;
    }

    public record GrantResult(boolean granted, boolean duplicate, boolean permanent, Instant expiresAt) {
        public static GrantResult granted(Instant expiresAt) {
            return new GrantResult(true, false, false, expiresAt);
        }

        public static GrantResult duplicate(Instant expiresAt) {
            return new GrantResult(false, true, false, expiresAt);
        }

        public static GrantResult permanentResult() {
            return new GrantResult(false, false, true, Instant.MAX);
        }
    }
}

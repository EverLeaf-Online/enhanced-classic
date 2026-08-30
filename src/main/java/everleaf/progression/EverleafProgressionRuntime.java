package everleaf.progression;

import tools.DatabaseConnection;

/**
 * Lazy access point for Everleaf progression services after the main database
 * pool has been initialized by the server bootstrap.
 */
public final class EverleafProgressionRuntime {
    private EverleafProgressionRuntime() {
    }

    private static final class Holder {
        private static final WeeklyProgressRepository WEEKLY_REPOSITORY =
                new JdbcWeeklyProgressRepository(DatabaseConnection.getDataSource());
        private static final WeeklyProgressionService WEEKLY_SERVICE =
                new WeeklyProgressionService(WEEKLY_REPOSITORY);
        private static final VerdantMarkRepository VERDANT_MARK_REPOSITORY =
                new JdbcVerdantMarkRepository(DatabaseConnection.getDataSource());
        private static final VerdantMarkService VERDANT_MARK_SERVICE =
                new VerdantMarkService(VERDANT_MARK_REPOSITORY);
        private static final PqPointRepository PQ_POINT_REPOSITORY =
                new JdbcPqPointRepository(DatabaseConnection.getDataSource());
        private static final PqPointService PQ_POINT_SERVICE =
                new PqPointService(PQ_POINT_REPOSITORY);
        private static final AccountEntitlementService ACCOUNT_ENTITLEMENT_SERVICE =
                new AccountEntitlementService(DatabaseConnection.getDataSource());
    }

    public static WeeklyProgressionService weeklyService() {
        return Holder.WEEKLY_SERVICE;
    }

    public static WeeklyProgressRepository weeklyRepository() {
        return Holder.WEEKLY_REPOSITORY;
    }

    public static VerdantMarkService verdantMarkService() {
        return Holder.VERDANT_MARK_SERVICE;
    }

    public static VerdantMarkRepository verdantMarkRepository() {
        return Holder.VERDANT_MARK_REPOSITORY;
    }

    public static PqPointService pqPointService() {
        return Holder.PQ_POINT_SERVICE;
    }

    public static PqPointRepository pqPointRepository() {
        return Holder.PQ_POINT_REPOSITORY;
    }

    public static AccountEntitlementService accountEntitlementService() {
        return Holder.ACCOUNT_ENTITLEMENT_SERVICE;
    }
}

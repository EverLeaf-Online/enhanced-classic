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
        private static final EncounterRepository ENCOUNTER_REPOSITORY =
                new JdbcEncounterRepository(DatabaseConnection.getDataSource());
        private static final EncounterService ENCOUNTER_SERVICE =
                new EncounterService(ENCOUNTER_REPOSITORY);
        private static final CygnusEncounterLifecycleService CYGNUS_ENCOUNTER_LIFECYCLE_SERVICE =
                new CygnusEncounterLifecycleService(ENCOUNTER_REPOSITORY);
        private static final RootedMaterialRepository ROOTED_MATERIAL_REPOSITORY =
                new JdbcRootedMaterialRepository(DatabaseConnection.getDataSource());
        private static final RootedForgeRepository ROOTED_FORGE_REPOSITORY =
                new JdbcRootedForgeRepository(DatabaseConnection.getDataSource());
        private static final RootedForgeService ROOTED_FORGE_SERVICE =
                new RootedForgeService(ROOTED_FORGE_REPOSITORY);
        private static final RootedForgeFulfillmentService ROOTED_FORGE_FULFILLMENT_SERVICE =
                new RootedForgeFulfillmentService(ROOTED_FORGE_REPOSITORY);
        private static final RootedZakumLifecycleService ROOTED_ZAKUM_LIFECYCLE_SERVICE =
                new RootedZakumLifecycleService(ENCOUNTER_SERVICE, ENCOUNTER_REPOSITORY,
                        VERDANT_MARK_REPOSITORY, ROOTED_MATERIAL_REPOSITORY);
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

    public static EncounterService encounterService() {
        return Holder.ENCOUNTER_SERVICE;
    }

    public static EncounterRepository encounterRepository() {
        return Holder.ENCOUNTER_REPOSITORY;
    }

    public static CygnusEncounterLifecycleService cygnusEncounterLifecycleService() {
        return Holder.CYGNUS_ENCOUNTER_LIFECYCLE_SERVICE;
    }

    public static RootedMaterialRepository rootedMaterialRepository() {
        return Holder.ROOTED_MATERIAL_REPOSITORY;
    }

    public static RootedForgeRepository rootedForgeRepository() {
        return Holder.ROOTED_FORGE_REPOSITORY;
    }

    public static RootedForgeService rootedForgeService() {
        return Holder.ROOTED_FORGE_SERVICE;
    }

    public static RootedForgeFulfillmentService rootedForgeFulfillmentService() {
        return Holder.ROOTED_FORGE_FULFILLMENT_SERVICE;
    }

    public static RootedZakumLifecycleService rootedZakumLifecycleService() {
        return Holder.ROOTED_ZAKUM_LIFECYCLE_SERVICE;
    }
}

package everleaf.progression;

/**
 * Bridge between Everleaf progression policy and Cosmic's map/event engine.
 * Implementations allocate isolated maps/event instances without leaking engine
 * objects into the progression domain model.
 */
public interface EncounterInstanceAdapter {
    void allocate(DedicatedEncounterInstance instance, EnhancedBossDefinition definition);

    void start(DedicatedEncounterInstance instance);

    void finish(DedicatedEncounterInstance instance);
}

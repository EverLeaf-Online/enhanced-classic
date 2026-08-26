package everleaf.progression;

import scripting.event.EventInstanceManager;
import scripting.event.EventManager;
import tools.exceptions.EventInstanceInProgressException;

import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.Collection;
import java.util.Set;
import java.util.UUID;

/**
 * Allocates isolated EventInstanceManager instances for Everleaf enhanced
 * encounters. Each allocation owns its own MapManager, so loading a verified
 * classic map through the EIM creates a dedicated party copy rather than using
 * the channel's shared world map.
 */
public final class EventInstanceEncounterAdapter {
    private final EventManager eventManager;

    public EventInstanceEncounterAdapter(EventManager eventManager) {
        if (eventManager == null) throw new IllegalArgumentException("eventManager cannot be null");
        this.eventManager = eventManager;
    }

    public Allocation allocate(
            long attemptId,
            String encounterId,
            int leaderCharacterId,
            Collection<Integer> participantCharacterIds,
            boolean practice,
            Instant now
    ) throws EventInstanceInProgressException {
        EnhancedBossDefinition definition = EnhancedBossCatalog.byId(encounterId);
        Set<Integer> participants = DedicatedEncounterPolicy.validateParty(
                definition, leaderCharacterId, participantCharacterIds);

        String instanceId = "Everleaf-" + encounterId + "-" + UUID.randomUUID();
        EventInstanceManager eim = eventManager.newInstance(instanceId);
        eim.setProperty("everleafEncounterId", encounterId);
        eim.setProperty("everleafAttemptId", Long.toString(attemptId));
        eim.setProperty("everleafPractice", practice ? "1" : "0");
        eim.setProperty("everleafLeaderId", Integer.toString(leaderCharacterId));
        eim.setProperty("everleafState", EncounterInstanceState.CREATED.name());

        Instant deadline = now.plus(definition.timeLimitMinutes(), ChronoUnit.MINUTES);
        DedicatedEncounterInstance snapshot = new DedicatedEncounterInstance(
                instanceId,
                attemptId,
                encounterId,
                leaderCharacterId,
                participants,
                practice,
                EncounterInstanceState.CREATED,
                now,
                null,
                deadline,
                null
        );
        return new Allocation(snapshot, eim);
    }

    /**
     * Loads and resets the encounter's verified classic map inside the EIM and
     * starts the encounter-specific clock. Player warps are intentionally a
     * separate step so a failed registration cannot strand a party in-map.
     */
    public Allocation activate(Allocation allocation, Instant now) {
        if (allocation == null) throw new IllegalArgumentException("allocation cannot be null");
        DedicatedEncounterInstance before = allocation.snapshot();
        if (before.state() != EncounterInstanceState.CREATED) {
            throw new IllegalStateException("instance_not_created");
        }

        EncounterMapBinding binding = EncounterMapBindings.byEncounterId(before.encounterId());
        EnhancedBossDefinition definition = EnhancedBossCatalog.byId(before.encounterId());
        EventInstanceManager eim = allocation.eventInstance();

        eim.getInstanceMap(binding.entryMapId()).resetPQ(1);
        eim.startEventTimer(definition.timeLimitMinutes() * 60_000L);
        eim.setProperty("everleafState", EncounterInstanceState.ACTIVE.name());

        DedicatedEncounterInstance active = new DedicatedEncounterInstance(
                before.instanceId(),
                before.attemptId(),
                before.encounterId(),
                before.leaderCharacterId(),
                before.participantCharacterIds(),
                before.practice(),
                EncounterInstanceState.ACTIVE,
                before.createdAt(),
                now,
                now.plus(definition.timeLimitMinutes(), ChronoUnit.MINUTES),
                null
        );
        return new Allocation(active, eim);
    }

    public void dispose(Allocation allocation) {
        if (allocation != null && allocation.eventInstance() != null) {
            allocation.eventInstance().dispose();
        }
    }

    public record Allocation(DedicatedEncounterInstance snapshot, EventInstanceManager eventInstance) {}
}

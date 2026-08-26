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
 * Allocates isolated Cosmic/HeavenMS EventInstanceManager instances for
 * Everleaf enhanced encounters. Player registration and map warps stay in the
 * event script / entry adapter so allocation is testable independently.
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

    public record Allocation(DedicatedEncounterInstance snapshot, EventInstanceManager eventInstance) {}
}

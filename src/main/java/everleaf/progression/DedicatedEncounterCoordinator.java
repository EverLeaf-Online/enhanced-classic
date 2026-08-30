package everleaf.progression;

import java.time.Instant;
import java.util.Collection;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;

/**
 * In-memory lifecycle coordinator for dedicated enhanced-boss party instances.
 * Engine-specific map/event allocation is intentionally delegated to an adapter.
 */
public final class DedicatedEncounterCoordinator {
    private final EncounterService encounterService;
    private final EncounterInstancePolicy policy;
    private final EncounterInstanceAdapter adapter;
    private final ConcurrentHashMap<String, DedicatedEncounterInstance> active = new ConcurrentHashMap<>();

    public DedicatedEncounterCoordinator(
            EncounterService encounterService,
            EncounterInstancePolicy policy,
            EncounterInstanceAdapter adapter
    ) {
        if (encounterService == null) throw new IllegalArgumentException("encounterService cannot be null");
        if (policy == null) throw new IllegalArgumentException("policy cannot be null");
        if (adapter == null) throw new IllegalArgumentException("adapter cannot be null");
        this.encounterService = encounterService;
        this.policy = policy;
        this.adapter = adapter;
    }

    public DedicatedEncounterInstance create(
            int accountId,
            int leaderCharacterId,
            int leaderLevel,
            Collection<Integer> participantCharacterIds,
            String encounterId,
            Instant now,
            boolean practice
    ) {
        EnhancedBossDefinition definition = EnhancedBossCatalog.byId(encounterId);
        Set<Integer> participants = DedicatedEncounterPolicy.validateParty(
                definition, leaderCharacterId, participantCharacterIds);

        boolean weeklyEligible = encounterService.isWeeklyRewardEligible(accountId, encounterId, now);
        boolean practiceOnly = practice || (!weeklyEligible && policy.allowPracticeAfterWeeklyClear());
        if (!weeklyEligible && !practiceOnly) throw new IllegalStateException("weekly_reward_already_cleared");

        EncounterAttempt attempt = encounterService.start(
                accountId, leaderCharacterId, leaderLevel, encounterId, now);
        String instanceId = encounterId + "-" + UUID.randomUUID();
        Instant deadline = now.plusSeconds(definition.timeLimitMinutes() * 60L);

        DedicatedEncounterInstance instance = new DedicatedEncounterInstance(
                instanceId, attempt.id(), encounterId, leaderCharacterId, participants,
                practiceOnly, EncounterInstanceState.CREATED, now, null, deadline, null);
        adapter.allocate(instance, definition);
        active.put(instanceId, instance);
        return instance;
    }

    public DedicatedEncounterInstance start(String instanceId, Instant now) {
        DedicatedEncounterInstance current = requireActive(instanceId);
        if (current.state() != EncounterInstanceState.CREATED) throw new IllegalStateException("instance_not_created");
        if (!now.isBefore(current.deadline())) return expire(instanceId, now);

        DedicatedEncounterInstance started = new DedicatedEncounterInstance(
                current.instanceId(), current.attemptId(), current.encounterId(), current.leaderCharacterId(),
                current.participantCharacterIds(), current.practice(), EncounterInstanceState.ACTIVE,
                current.createdAt(), now, current.deadline(), null);
        adapter.start(started);
        active.put(instanceId, started);
        return started;
    }

    public DedicatedEncounterInstance clear(String instanceId, Instant now) {
        DedicatedEncounterInstance current = requireActive(instanceId);
        if (current.state() != EncounterInstanceState.ACTIVE) throw new IllegalStateException("instance_not_active");
        if (!now.isBefore(current.deadline())) return expire(instanceId, now);

        encounterService.clear(current.attemptId(), now);
        DedicatedEncounterInstance cleared = terminal(current, EncounterInstanceState.CLEARED, now);
        adapter.finish(cleared);
        active.remove(instanceId);
        return cleared;
    }

    public DedicatedEncounterInstance fail(String instanceId, Instant now) {
        DedicatedEncounterInstance current = requireActive(instanceId);
        if (current.state() != EncounterInstanceState.ACTIVE) throw new IllegalStateException("instance_not_active");
        encounterService.fail(current.attemptId(), now);
        DedicatedEncounterInstance failed = terminal(current, EncounterInstanceState.FAILED, now);
        adapter.finish(failed);
        active.remove(instanceId);
        return failed;
    }

    public DedicatedEncounterInstance expire(String instanceId, Instant now) {
        DedicatedEncounterInstance current = requireActive(instanceId);
        if (current.terminal()) throw new IllegalStateException("instance_already_terminal");
        encounterService.fail(current.attemptId(), now);
        DedicatedEncounterInstance expired = terminal(current, EncounterInstanceState.EXPIRED, now);
        adapter.finish(expired);
        active.remove(instanceId);
        return expired;
    }

    /** Expires all instances whose deadline has elapsed. Returns number cleaned up. */
    public int expireDue(Instant now) {
        int expired = 0;
        for (DedicatedEncounterInstance instance : active.values()) {
            if (!now.isBefore(instance.deadline())) {
                try {
                    expire(instance.instanceId(), now);
                    expired++;
                } catch (IllegalArgumentException ignored) {
                    // Another thread completed/removed the instance first.
                }
            }
        }
        return expired;
    }

    public DedicatedEncounterInstance requireActive(String instanceId) {
        DedicatedEncounterInstance instance = active.get(instanceId);
        if (instance == null) throw new IllegalArgumentException("unknown active instance");
        return instance;
    }

    public int activeCount() {
        return active.size();
    }

    private static DedicatedEncounterInstance terminal(
            DedicatedEncounterInstance current, EncounterInstanceState state, Instant now) {
        return new DedicatedEncounterInstance(
                current.instanceId(), current.attemptId(), current.encounterId(), current.leaderCharacterId(),
                current.participantCharacterIds(), current.practice(), state,
                current.createdAt(), current.startedAt(), current.deadline(), now);
    }
}

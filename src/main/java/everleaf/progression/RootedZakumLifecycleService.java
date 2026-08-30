package everleaf.progression;

import java.time.Instant;
import java.util.Map;

/**
 * Connects a Rooted Zakum attempt to its account-scoped, retry-safe reward
 * fulfillment. The encounter claim is persisted before currency delivery;
 * deterministic ledger keys make every subsequent delivery retry idempotent.
 */
public final class RootedZakumLifecycleService {
    public static final String ENCOUNTER_ID = "rooted_zakum";

    private final EncounterService encounterService;
    private final EncounterRepository encounterRepository;
    private final VerdantMarkRepository verdantMarkRepository;
    private final RootedMaterialRepository materialRepository;

    public RootedZakumLifecycleService(
            EncounterService encounterService,
            EncounterRepository encounterRepository,
            VerdantMarkRepository verdantMarkRepository,
            RootedMaterialRepository materialRepository
    ) {
        if (encounterService == null || encounterRepository == null
                || verdantMarkRepository == null || materialRepository == null) {
            throw new IllegalArgumentException("dependencies cannot be null");
        }
        this.encounterService = encounterService;
        this.encounterRepository = encounterRepository;
        this.verdantMarkRepository = verdantMarkRepository;
        this.materialRepository = materialRepository;
    }

    public StartedAttempt begin(int accountId, int characterId, int level, Instant now) {
        EnhancedBossRewardMode mode = encounterService.isWeeklyRewardEligible(accountId, ENCOUNTER_ID, now)
                ? EnhancedBossRewardMode.WEEKLY_REWARD
                : EnhancedBossRewardMode.PRACTICE;
        EncounterAttempt attempt = encounterService.start(accountId, characterId, level, ENCOUNTER_ID, now);
        return new StartedAttempt(attempt.id(), mode);
    }

    public Completion complete(long attemptId, EnhancedBossRewardMode mode, Instant now) {
        if (mode == null) throw new IllegalArgumentException("mode cannot be null");
        EncounterAttempt attempt = encounterRepository.findAttempt(attemptId)
                .orElseThrow(() -> new IllegalArgumentException("unknown attempt"));
        if (attempt.result() == EncounterResult.IN_PROGRESS) {
            attempt = encounterService.clear(attemptId, now);
        }
        if (!attempt.cleared()) return Completion.rejected("attempt_not_cleared");
        if (!mode.grantsValuableRewards()) return Completion.practice();

        if (!attempt.weeklyRewardClaimed()) {
            encounterService.claimWeeklyReward(attemptId, now);
            attempt = encounterRepository.findAttempt(attemptId).orElseThrow();
        }
        // Another character on this account may have won the weekly claim race.
        if (!attempt.weeklyRewardClaimed()) return Completion.practice();

        RootedZakumRewardPolicy.RewardBundle reward =
                RootedZakumRewardPolicy.forMode(EnhancedBossRewardMode.WEEKLY_REWARD);
        String reasonKey = "rooted_zakum_attempt:" + attemptId;
        VerdantMarkRepository.MutationResult marks = verdantMarkRepository.credit(
                attempt.accountId(), attempt.characterId(), reward.verdantMarks(),
                "ENCOUNTER_CLEAR", reasonKey, "encounter=" + ENCOUNTER_ID);
        if (!marks.success() && !"duplicate_reason".equals(marks.reason())) {
            return Completion.rejected("marks_" + marks.reason());
        }

        for (Map.Entry<RootedMaterial, Integer> entry : reward.materials().entrySet()) {
            RootedMaterialRepository.MutationResult material = materialRepository.credit(
                    attempt.accountId(), attempt.characterId(), entry.getKey(), entry.getValue(), reasonKey);
            if (!material.applied() && !"duplicate_reason".equals(material.reason())) {
                return Completion.rejected("material_" + entry.getKey().name().toLowerCase()
                        + "_" + material.reason());
            }
        }
        return Completion.rewarded(reward);
    }

    /** Marks an abandoned or timed-out attempt failed; terminal attempts are left unchanged. */
    public void fail(long attemptId, Instant now) {
        EncounterAttempt attempt = encounterRepository.findAttempt(attemptId)
                .orElseThrow(() -> new IllegalArgumentException("unknown attempt"));
        if (!attempt.finished()) encounterService.fail(attemptId, now);
    }

    public record StartedAttempt(long attemptId, EnhancedBossRewardMode mode) {}

    public record Completion(boolean completed, boolean rewarded, String reason,
                             int verdantMarks, Map<RootedMaterial, Integer> materials) {
        private static Completion rewarded(RootedZakumRewardPolicy.RewardBundle reward) {
            return new Completion(true, true, "rewarded", reward.verdantMarks(), reward.materials());
        }

        private static Completion practice() {
            return new Completion(true, false, "practice", 0, Map.of());
        }

        private static Completion rejected(String reason) {
            return new Completion(false, false, reason, 0, Map.of());
        }
    }
}

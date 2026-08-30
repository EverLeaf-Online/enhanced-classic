package everleaf.progression;

import org.junit.jupiter.api.Test;

import java.time.Instant;
import java.time.LocalDate;
import java.util.*;

import static org.junit.jupiter.api.Assertions.*;

class EncounterServiceTest {
    @Test
    void enforcesLevelGateAndLifecycle() {
        MemoryRepo repo = new MemoryRepo();
        EncounterService service = new EncounterService(repo);
        Instant now = Instant.parse("2026-08-26T07:00:00Z");

        assertThrows(IllegalStateException.class,
                () -> service.start(1, 10, 199, "rooted_zakum", now));

        EncounterAttempt attempt = service.start(1, 10, 200, "rooted_zakum", now);
        EncounterAttempt cleared = service.clear(attempt.id(), now.plusSeconds(600));
        assertTrue(cleared.cleared());
        assertThrows(IllegalStateException.class,
                () -> service.fail(attempt.id(), now.plusSeconds(700)));
    }

    @Test
    void weeklyRewardIsAccountScopedAcrossCharacters() {
        MemoryRepo repo = new MemoryRepo();
        EncounterService service = new EncounterService(repo);
        Instant now = Instant.parse("2026-08-26T07:00:00Z");

        EncounterAttempt first = service.start(7, 101, 200, "rooted_zakum", now);
        service.clear(first.id(), now.plusSeconds(100));
        assertTrue(service.claimWeeklyReward(first.id(), now.plusSeconds(110)));
        assertFalse(service.isWeeklyRewardEligible(7, "rooted_zakum", now.plusSeconds(120)));

        EncounterAttempt alt = service.start(7, 202, 200, "rooted_zakum", now.plusSeconds(200));
        service.clear(alt.id(), now.plusSeconds(300));
        assertFalse(service.claimWeeklyReward(alt.id(), now.plusSeconds(310)));
    }

    private static final class MemoryRepo implements EncounterRepository {
        private final Map<Long, EncounterAttempt> attempts = new HashMap<>();
        private final Set<String> weeklyClaims = new HashSet<>();
        private long sequence = 1;

        public EncounterAttempt createAttempt(int accountId, int characterId, String encounterId, Instant startedAt) {
            EncounterAttempt attempt = new EncounterAttempt(sequence++, accountId, characterId, encounterId,
                    startedAt, null, EncounterResult.IN_PROGRESS, false);
            attempts.put(attempt.id(), attempt);
            return attempt;
        }

        public Optional<EncounterAttempt> findAttempt(long attemptId) {
            return Optional.ofNullable(attempts.get(attemptId));
        }

        public EncounterAttempt finishAttempt(long attemptId, EncounterResult result, Instant finishedAt) {
            EncounterAttempt old = attempts.get(attemptId);
            EncounterAttempt next = new EncounterAttempt(old.id(), old.accountId(), old.characterId(), old.encounterId(),
                    old.startedAt(), finishedAt, result, old.weeklyRewardClaimed());
            attempts.put(attemptId, next);
            return next;
        }

        public boolean hasWeeklyRewardClaim(int accountId, String encounterId, LocalDate weekStartUtc) {
            return weeklyClaims.contains(accountId + ":" + encounterId + ":" + weekStartUtc);
        }

        public boolean markWeeklyRewardClaimed(long attemptId, LocalDate weekStartUtc, Instant claimedAt) {
            EncounterAttempt old = attempts.get(attemptId);
            String key = old.accountId() + ":" + old.encounterId() + ":" + weekStartUtc;
            if (!weeklyClaims.add(key)) return false;
            attempts.put(attemptId, new EncounterAttempt(old.id(), old.accountId(), old.characterId(), old.encounterId(),
                    old.startedAt(), old.finishedAt(), old.result(), true));
            return true;
        }

        public List<EncounterAttempt> recentAttempts(int characterId, int limit) {
            return attempts.values().stream().filter(a -> a.characterId() == characterId).limit(limit).toList();
        }
    }
}

package everleaf.progression;

import org.junit.jupiter.api.Test;

import java.time.Instant;
import java.time.LocalDate;
import java.util.*;

import static org.junit.jupiter.api.Assertions.*;

class RootedZakumLifecycleServiceTest {
    @Test
    void weeklyClearPaysExactlyOnceAndRetryIsSafe() {
        Fixture fixture = new Fixture();
        Instant now = Instant.parse("2026-08-26T12:00:00Z");
        var started = fixture.service.begin(7, 70, 200, now);

        assertEquals(EnhancedBossRewardMode.WEEKLY_REWARD, started.mode());
        var first = fixture.service.complete(started.attemptId(), started.mode(), now.plusSeconds(60));
        var retry = fixture.service.complete(started.attemptId(), started.mode(), now.plusSeconds(90));

        assertTrue(first.rewarded());
        assertTrue(retry.rewarded());
        assertEquals(20, fixture.marks.balance);
        assertEquals(2, fixture.materials.balances(7).get(RootedMaterial.EMBER_CORE));
        assertEquals(1, fixture.materials.balances(7).get(RootedMaterial.ANCIENT_BARK));
    }

    @Test
    void subsequentAccountClearIsPracticeOnly() {
        Fixture fixture = new Fixture();
        Instant now = Instant.parse("2026-08-26T12:00:00Z");
        var first = fixture.service.begin(7, 70, 200, now);
        fixture.service.complete(first.attemptId(), first.mode(), now.plusSeconds(60));

        var alt = fixture.service.begin(7, 71, 200, now.plusSeconds(120));
        var completion = fixture.service.complete(alt.attemptId(), alt.mode(), now.plusSeconds(180));

        assertEquals(EnhancedBossRewardMode.PRACTICE, alt.mode());
        assertTrue(completion.completed());
        assertFalse(completion.rewarded());
        assertEquals(20, fixture.marks.balance);
    }

    @Test
    void abandonedAttemptIsFailedIdempotently() {
        Fixture fixture = new Fixture();
        Instant now = Instant.parse("2026-08-26T12:00:00Z");
        var started = fixture.service.begin(7, 70, 200, now);

        fixture.service.fail(started.attemptId(), now.plusSeconds(30));
        fixture.service.fail(started.attemptId(), now.plusSeconds(60));

        assertEquals(EncounterResult.FAILED,
                fixture.encounters.findAttempt(started.attemptId()).orElseThrow().result());
    }

    private static final class Fixture {
        final EncounterMemory encounters = new EncounterMemory();
        final MarkMemory marks = new MarkMemory();
        final MaterialMemory materials = new MaterialMemory();
        final EncounterService encounterService = new EncounterService(encounters);
        final RootedZakumLifecycleService service = new RootedZakumLifecycleService(
                encounterService, encounters, marks, materials);
    }

    private static final class EncounterMemory implements EncounterRepository {
        final Map<Long, EncounterAttempt> attempts = new HashMap<>();
        final Set<String> claims = new HashSet<>();
        long sequence = 1;

        public EncounterAttempt createAttempt(int accountId, int characterId, String encounterId, Instant startedAt) {
            var attempt = new EncounterAttempt(sequence++, accountId, characterId, encounterId,
                    startedAt, null, EncounterResult.IN_PROGRESS, false);
            attempts.put(attempt.id(), attempt);
            return attempt;
        }
        public Optional<EncounterAttempt> findAttempt(long id) { return Optional.ofNullable(attempts.get(id)); }
        public EncounterAttempt finishAttempt(long id, EncounterResult result, Instant at) {
            var old = attempts.get(id);
            var next = new EncounterAttempt(id, old.accountId(), old.characterId(), old.encounterId(),
                    old.startedAt(), at, result, old.weeklyRewardClaimed());
            attempts.put(id, next);
            return next;
        }
        public boolean hasWeeklyRewardClaim(int accountId, String encounterId, LocalDate week) {
            return claims.contains(accountId + ":" + encounterId + ":" + week);
        }
        public boolean markWeeklyRewardClaimed(long id, LocalDate week, Instant at) {
            var old = attempts.get(id);
            if (!claims.add(old.accountId() + ":" + old.encounterId() + ":" + week)) return false;
            attempts.put(id, new EncounterAttempt(id, old.accountId(), old.characterId(), old.encounterId(),
                    old.startedAt(), old.finishedAt(), old.result(), true));
            return true;
        }
        public List<EncounterAttempt> recentAttempts(int characterId, int limit) { return List.of(); }
    }

    private static final class MarkMemory implements VerdantMarkRepository {
        int balance;
        final Set<String> keys = new HashSet<>();
        public VerdantMarkAccount getAccount(int accountId) { return new VerdantMarkAccount(accountId, balance, balance, 0); }
        public MutationResult credit(int accountId, Integer characterId, int amount, String type, String key, String metadata) {
            if (!keys.add(type + ":" + key)) return MutationResult.rejected("duplicate_reason", balance);
            balance += amount;
            return MutationResult.success(amount, balance);
        }
        public MutationResult spend(int a, Integer c, int amount, String type, String key, String metadata) {
            throw new UnsupportedOperationException();
        }
        public List<VerdantMarkLedgerEntry> recentLedger(int accountId, int limit) { return List.of(); }
    }

    private static final class MaterialMemory implements RootedMaterialRepository {
        final EnumMap<RootedMaterial, Integer> amounts = new EnumMap<>(RootedMaterial.class);
        final Set<String> keys = new HashSet<>();
        public Map<RootedMaterial, Integer> balances(int accountId) {
            var result = new EnumMap<RootedMaterial, Integer>(RootedMaterial.class);
            for (var material : RootedMaterial.values()) result.put(material, amounts.getOrDefault(material, 0));
            return result;
        }
        public MutationResult credit(int accountId, int characterId, RootedMaterial material, int amount, String key) {
            if (!keys.add(material + ":" + key)) return MutationResult.rejected("duplicate_reason", amounts.getOrDefault(material, 0));
            int next = amounts.merge(material, amount, Integer::sum);
            return MutationResult.success(next);
        }
        public MutationResult spend(int a, int c, RootedMaterial m, int amount, String key) {
            throw new UnsupportedOperationException();
        }
    }
}

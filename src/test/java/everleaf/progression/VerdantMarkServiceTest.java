package everleaf.progression;

import org.junit.jupiter.api.Test;

import java.time.Instant;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;

class VerdantMarkServiceTest {

    @Test
    void weeklyAwardsShareOneAccountBalanceAcrossCharacters() {
        MemoryRepository repository = new MemoryRepository();
        VerdantMarkService service = new VerdantMarkService(repository);

        assertTrue(service.awardWeekly(1, 101, 40, "2026-08-24", "rooted_boss_hunt").success());
        assertTrue(service.awardWeekly(1, 102, 35, "2026-08-24", "rooted_party_clear").success());

        assertEquals(75, service.account(1).balance());
        assertEquals(75, service.account(1).lifetimeEarned());
    }

    @Test
    void sameObjectiveCanAwardDifferentCharactersButNotSameCharacterTwice() {
        MemoryRepository repository = new MemoryRepository();
        VerdantMarkService service = new VerdantMarkService(repository);

        assertTrue(service.awardWeekly(2, 201, 25, "2026-08-24", "rooted_collection").success());
        assertTrue(service.awardWeekly(2, 202, 25, "2026-08-24", "rooted_collection").success());
        assertFalse(service.awardWeekly(2, 201, 25, "2026-08-24", "rooted_collection").success());
        assertEquals(50, service.account(2).balance());
    }

    @Test
    void spendingCannotOverdrawAndTracksLifetimeSpend() {
        MemoryRepository repository = new MemoryRepository();
        VerdantMarkService service = new VerdantMarkService(repository);
        service.awardWeekly(3, 301, 40, "2026-08-24", "rooted_boss_hunt");

        assertFalse(service.spend(3, 301, 50, "purchase-1", "reward=test").success());
        assertTrue(service.spend(3, 301, 15, "purchase-2", "reward=test").success());
        assertEquals(25, service.account(3).balance());
        assertEquals(15, service.account(3).lifetimeSpent());
    }

    @Test
    void ledgerLimitIsValidated() {
        VerdantMarkService service = new VerdantMarkService(new MemoryRepository());
        assertThrows(IllegalArgumentException.class, () -> service.recentLedger(1, 0));
        assertThrows(IllegalArgumentException.class, () -> service.recentLedger(1, 101));
    }

    private static final class MemoryRepository implements VerdantMarkRepository {
        private final Map<Integer, VerdantMarkAccount> accounts = new HashMap<>();
        private final Map<String, VerdantMarkLedgerEntry> uniqueReasons = new HashMap<>();
        private final List<VerdantMarkLedgerEntry> ledger = new ArrayList<>();
        private long nextId = 1;

        @Override
        public VerdantMarkAccount getAccount(int accountId) {
            return accounts.getOrDefault(accountId, new VerdantMarkAccount(accountId, 0, 0, 0));
        }

        @Override
        public MutationResult credit(int accountId, Integer characterId, int amount, String reasonType, String reasonKey, String metadata) {
            String unique = accountId + ":" + reasonType + ":" + reasonKey;
            if (uniqueReasons.containsKey(unique)) return MutationResult.rejected("duplicate_reason", getAccount(accountId).balance());
            VerdantMarkAccount current = getAccount(accountId);
            int next = current.balance() + amount;
            accounts.put(accountId, new VerdantMarkAccount(accountId, next, current.lifetimeEarned() + amount, current.lifetimeSpent()));
            addLedger(unique, accountId, characterId, amount, next, reasonType, reasonKey, metadata);
            return MutationResult.success(amount, next);
        }

        @Override
        public MutationResult spend(int accountId, Integer characterId, int amount, String reasonType, String reasonKey, String metadata) {
            String unique = accountId + ":" + reasonType + ":" + reasonKey;
            if (uniqueReasons.containsKey(unique)) return MutationResult.rejected("duplicate_reason", getAccount(accountId).balance());
            VerdantMarkAccount current = getAccount(accountId);
            if (current.balance() < amount) return MutationResult.rejected("insufficient_balance", current.balance());
            int next = current.balance() - amount;
            accounts.put(accountId, new VerdantMarkAccount(accountId, next, current.lifetimeEarned(), current.lifetimeSpent() + amount));
            addLedger(unique, accountId, characterId, -amount, next, reasonType, reasonKey, metadata);
            return MutationResult.success(amount, next);
        }

        private void addLedger(String unique, int accountId, Integer characterId, int amount, int balanceAfter,
                               String reasonType, String reasonKey, String metadata) {
            VerdantMarkLedgerEntry entry = new VerdantMarkLedgerEntry(nextId++, accountId, characterId, amount,
                    balanceAfter, reasonType, reasonKey, metadata, Instant.now());
            uniqueReasons.put(unique, entry);
            ledger.add(entry);
        }

        @Override
        public List<VerdantMarkLedgerEntry> recentLedger(int accountId, int limit) {
            return ledger.stream().filter(entry -> entry.accountId() == accountId).limit(limit).toList();
        }
    }
}

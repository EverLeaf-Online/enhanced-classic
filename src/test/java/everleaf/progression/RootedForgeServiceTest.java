package everleaf.progression;

import org.junit.jupiter.api.Test;

import java.time.Instant;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;

class RootedForgeServiceTest {
    @Test
    void rejectsPlayersBelowRootedWithoutChargingRepository() {
        FakeRepository repository = new FakeRepository();
        var result = new RootedForgeService(repository).purchase(
                1, 2, 199, RootedForgeRecipe.ROOTED_WEAPON_REFINEMENT, "request-1");
        assertFalse(result.applied());
        assertEquals("rooted_milestone_required", result.reason());
        assertEquals(0, repository.calls);
    }

    @Test
    void delegatesEligibleDeterministicPurchaseOnce() {
        FakeRepository repository = new FakeRepository();
        var result = new RootedForgeService(repository).purchase(
                1, 2, 200, RootedForgeRecipe.ROOTED_ARMOR_REFINEMENT, "request-2");
        assertTrue(result.applied());
        assertNotNull(result.order());
        assertEquals(RootedForgeOrder.Status.PENDING, result.order().status());
        assertEquals(1, repository.calls);
    }

    private static final class FakeRepository implements RootedForgeRepository {
        int calls;

        @Override
        public PurchaseResult purchase(int accountId, int characterId, RootedForgeRecipe recipe, String requestKey) {
            calls++;
            return PurchaseResult.success(new RootedForgeOrder(
                    1, accountId, characterId, recipe, requestKey,
                    RootedForgeOrder.Status.PENDING, Instant.EPOCH));
        }

        @Override
        public Optional<RootedForgeOrder> findByRequestKey(int accountId, String requestKey) {
            return Optional.empty();
        }
    }
}

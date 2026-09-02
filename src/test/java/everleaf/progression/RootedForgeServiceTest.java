package everleaf.progression;

import org.junit.jupiter.api.Test;

import java.time.Instant;
import java.util.Optional;
import client.inventory.InventoryType;

import static org.junit.jupiter.api.Assertions.*;

class RootedForgeServiceTest {
    @Test
    void rejectsPlayersBelowRootedWithoutChargingRepository() {
        FakeRepository repository = new FakeRepository();
        var result = new RootedForgeService(repository).purchase(
                1, 2, 199, RootedForgeRecipe.ROOTED_WEAPON_REFINEMENT,
                new RootedForgeTarget(1302000, InventoryType.EQUIP, (short) 1), "request-1");
        assertFalse(result.applied());
        assertEquals("rooted_milestone_required", result.reason());
        assertEquals(0, repository.calls);
    }

    @Test
    void delegatesEligibleDeterministicPurchaseOnce() {
        FakeRepository repository = new FakeRepository();
        var result = new RootedForgeService(repository).purchase(
                1, 2, 200, RootedForgeRecipe.ROOTED_ARMOR_REFINEMENT,
                new RootedForgeTarget(1002001, InventoryType.EQUIP, (short) 1), "request-2");
        assertTrue(result.applied());
        assertNotNull(result.order());
        assertEquals(RootedForgeOrder.Status.PENDING, result.order().status());
        assertEquals(1, repository.calls);
    }

    private static final class FakeRepository implements RootedForgeRepository {
        int calls;

        @Override
        public PurchaseResult purchase(int accountId, int characterId, RootedForgeRecipe recipe, RootedForgeTarget target, String requestKey) {
            calls++;
            return PurchaseResult.success(new RootedForgeOrder(
                    1, accountId, characterId, recipe, target, requestKey,
                    RootedForgeOrder.Status.PENDING, Instant.EPOCH));
        }

        @Override
        public Optional<RootedForgeOrder> findByRequestKey(int accountId, String requestKey) {
            return Optional.empty();
        }

        @Override
        public Optional<RootedForgeOrder> findById(long orderId) { return Optional.empty(); }

        @Override
        public boolean markFulfilled(long orderId) { return false; }
    }
}

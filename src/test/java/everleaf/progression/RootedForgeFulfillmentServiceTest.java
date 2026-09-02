package everleaf.progression;

import client.Character;
import client.inventory.Equip;
import client.inventory.Inventory;
import client.inventory.InventoryType;
import org.junit.jupiter.api.Test;

import java.time.Instant;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

class RootedForgeFulfillmentServiceTest {
    @Test
    void appliesSavesAndCompletesOwnedPendingOrder() {
        FakeRepository repository = new FakeRepository(order());
        Character character = mock(Character.class);
        Inventory inventory = mock(Inventory.class);
        Equip equip = mock(Equip.class);
        when(character.getAccountID()).thenReturn(10);
        when(character.getId()).thenReturn(20);
        when(character.getInventory(InventoryType.EQUIP)).thenReturn(inventory);
        when(inventory.getItem((short) 1)).thenReturn(equip);
        when(equip.getItemId()).thenReturn(1302000);

        var result = new RootedForgeFulfillmentService(repository).fulfill(character, 1);

        assertTrue(result.fulfilled());
        assertEquals("ok", result.reason());
        assertTrue(repository.marked);
        verify(character).forceUpdateItem(equip);
        verify(character).saveCharToDB(true);
    }

    @Test
    void rejectsACharacterThatDoesNotOwnTheOrder() {
        FakeRepository repository = new FakeRepository(order());
        Character character = mock(Character.class);
        when(character.getAccountID()).thenReturn(99);
        when(character.getId()).thenReturn(20);

        var result = new RootedForgeFulfillmentService(repository).fulfill(character, 1);

        assertFalse(result.fulfilled());
        assertEquals("order_owner_mismatch", result.reason());
        assertFalse(repository.marked);
        verify(character, never()).saveCharToDB(true);
    }

    private static RootedForgeOrder order() {
        return new RootedForgeOrder(
                1, 10, 20, RootedForgeRecipe.ROOTED_WEAPON_REFINEMENT,
                new RootedForgeTarget(1302000, InventoryType.EQUIP, (short) 1),
                "request", RootedForgeOrder.Status.PENDING, Instant.EPOCH);
    }

    private static final class FakeRepository implements RootedForgeRepository {
        private RootedForgeOrder order;
        private boolean marked;

        private FakeRepository(RootedForgeOrder order) { this.order = order; }

        @Override
        public PurchaseResult purchase(int accountId, int characterId, RootedForgeRecipe recipe, RootedForgeTarget target, String requestKey) {
            throw new UnsupportedOperationException();
        }

        @Override
        public Optional<RootedForgeOrder> findByRequestKey(int accountId, String requestKey) { return Optional.ofNullable(order); }

        @Override
        public Optional<RootedForgeOrder> findById(long orderId) { return Optional.ofNullable(order); }

        @Override
        public boolean markFulfilled(long orderId) {
            marked = true;
            order = new RootedForgeOrder(
                    order.id(), order.accountId(), order.characterId(), order.recipe(), order.target(), order.requestKey(),
                    RootedForgeOrder.Status.FULFILLED, order.createdAt());
            return true;
        }
    }
}

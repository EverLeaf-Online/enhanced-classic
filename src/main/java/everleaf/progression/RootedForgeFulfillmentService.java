package everleaf.progression;

import client.Character;
import client.inventory.Equip;
import client.inventory.Item;

/** Synchronous, crash-recoverable delivery of a paid Rooted forge order. */
public final class RootedForgeFulfillmentService {
    private final RootedForgeRepository repository;

    public RootedForgeFulfillmentService(RootedForgeRepository repository) {
        if (repository == null) throw new IllegalArgumentException("repository cannot be null");
        this.repository = repository;
    }

    public Result fulfill(Character character, long orderId) {
        if (character == null) return Result.rejected("character_required");
        RootedForgeOrder order = repository.findById(orderId).orElse(null);
        if (order == null) return Result.rejected("order_not_found");
        if (order.accountId() != character.getAccountID() || order.characterId() != character.getId()) {
            return Result.rejected("order_owner_mismatch");
        }
        if (order.status() == RootedForgeOrder.Status.FULFILLED) return Result.complete("already_fulfilled");

        RootedForgeTarget target = order.target();
        Item item = character.getInventory(target.inventoryType()).getItem(target.slot());
        if (!(item instanceof Equip equip) || item.getItemId() != target.itemId()) {
            return Result.rejected("target_moved_or_missing");
        }

        var outcome = RootedForgeOutcomeCatalog.byRecipe(order.recipe());
        var applied = RootedForgeStatApplier.apply(equip, outcome);
        if (!applied.applied() && !"stage_already_applied".equals(applied.reason())) {
            return Result.rejected(applied.reason());
        }

        character.forceUpdateItem(equip);
        if (target.inventoryType() == client.inventory.InventoryType.EQUIPPED) character.equipChanged();
        character.saveCharToDB(true);
        if (!repository.markFulfilled(orderId)) {
            RootedForgeOrder latest = repository.findById(orderId).orElse(null);
            if (latest == null || latest.status() != RootedForgeOrder.Status.FULFILLED) {
                return Result.rejected("fulfillment_state_conflict");
            }
        }
        return Result.complete(applied.applied() ? "ok" : "recovered");
    }

    public record Result(boolean fulfilled, String reason) {
        public static Result complete(String reason) { return new Result(true, reason); }
        public static Result rejected(String reason) { return new Result(false, reason); }
    }
}

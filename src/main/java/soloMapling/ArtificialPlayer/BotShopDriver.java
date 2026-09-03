package soloMapling.ArtificialPlayer;

import client.Character;
import client.inventory.InventoryType;
import client.inventory.Item;
import constants.inventory.ItemConstants;
import server.ItemInformationProvider;
import server.Shop;
import server.ShopFactory;
import server.ShopItem;
import server.StatEffect;
import server.life.NPC;
import soloMapling.ArtificialPlayer.GCMoveSystem.GCMovement;

import java.util.Comparator;

/** Uses ordinary EverLeaf NPC-shop transactions for QA buying, selling, recharging and restocking. */
public final class BotShopDriver {
    private static final int INTERACT_RANGE = 220;
    private static final int POTION_LOW_WATER = 10;
    private static final int POTION_TARGET = 50;

    private BotShopDriver() {}

    public static ShopResult openNearest(Character bot) {
        NPC npc = BotNpcDriver.nearestNpc(bot, true);
        if (npc == null) return ShopResult.fail("no-shop-npc");
        return open(bot, npc.getId());
    }

    public static ShopResult open(Character bot, int npcId) {
        if (!eligible(bot)) return ShopResult.fail("not-eligible");
        NPC npc = BotNpcDriver.findNpc(bot, npcId);
        if (npc == null || !npc.hasShop()) return ShopResult.fail("shop-npc-not-on-map");
        if (bot.getPosition().distanceSq(npc.getPosition()) > (double) INTERACT_RANGE * INTERACT_RANGE) return ShopResult.fail("shop-too-far");
        npc.sendShop(bot.getClient());
        Shop shop = ShopFactory.getInstance().getShopForNPC(npc.getId());
        return new ShopResult(true, npc.getId(), shop == null ? 0 : shop.getId(), 0, 0, 0, "opened");
    }

    public static ShopResult buy(Character bot, int npcId, int itemId, short quantity) {
        if (!eligible(bot) || quantity <= 0) return ShopResult.fail("not-eligible");
        NPC npc = BotNpcDriver.findNpc(bot, npcId);
        if (npc == null || !npc.hasShop()) return ShopResult.fail("shop-npc-not-on-map");
        if (bot.getPosition().distanceSq(npc.getPosition()) > (double) INTERACT_RANGE * INTERACT_RANGE) return ShopResult.fail("shop-too-far");

        Shop shop = ShopFactory.getInstance().getShopForNPC(npcId);
        short slot = shop.findSlotByItemId(itemId);
        if (slot < 0) return ShopResult.fail("item-not-sold");
        InventoryType type = ItemConstants.getInventoryType(itemId);
        int before = bot.getInventory(type).countById(itemId);
        int mesosBefore = bot.getMeso();
        shop.sendShop(bot.getClient());
        shop.buy(bot.getClient(), slot, itemId, quantity);
        int after = bot.getInventory(type).countById(itemId);
        return new ShopResult(after > before, npcId, shop.getId(), itemId, after - before,
                mesosBefore - bot.getMeso(), after > before ? "bought" : "buy-rejected");
    }

    public static ShopResult sell(Character bot, int npcId, InventoryType type, short slot, short quantity) {
        if (!eligible(bot) || type == null || quantity <= 0) return ShopResult.fail("not-eligible");
        NPC npc = BotNpcDriver.findNpc(bot, npcId);
        if (npc == null || !npc.hasShop()) return ShopResult.fail("shop-npc-not-on-map");
        if (bot.getPosition().distanceSq(npc.getPosition()) > (double) INTERACT_RANGE * INTERACT_RANGE) return ShopResult.fail("shop-too-far");
        Item item = bot.getInventory(type).getItem(slot);
        if (item == null) return ShopResult.fail("empty-slot");

        Shop shop = ShopFactory.getInstance().getShopForNPC(npcId);
        int itemId = item.getItemId();
        int before = bot.getInventory(type).countById(itemId);
        int mesosBefore = bot.getMeso();
        shop.sendShop(bot.getClient());
        shop.sell(bot.getClient(), type, slot, quantity);
        int after = bot.getInventory(type).countById(itemId);
        return new ShopResult(after < before, npcId, shop.getId(), itemId, before - after,
                bot.getMeso() - mesosBefore, after < before ? "sold" : "sell-rejected");
    }

    public static ShopResult recharge(Character bot, int npcId, short useSlot) {
        if (!eligible(bot)) return ShopResult.fail("not-eligible");
        NPC npc = BotNpcDriver.findNpc(bot, npcId);
        if (npc == null || !npc.hasShop()) return ShopResult.fail("shop-npc-not-on-map");
        if (bot.getPosition().distanceSq(npc.getPosition()) > (double) INTERACT_RANGE * INTERACT_RANGE) return ShopResult.fail("shop-too-far");
        Item item = bot.getInventory(InventoryType.USE).getItem(useSlot);
        if (item == null || !ItemConstants.isRechargeable(item.getItemId())) return ShopResult.fail("not-rechargeable");

        Shop shop = ShopFactory.getInstance().getShopForNPC(npcId);
        int before = item.getQuantity();
        int mesosBefore = bot.getMeso();
        shop.sendShop(bot.getClient());
        shop.recharge(bot.getClient(), useSlot);
        Item afterItem = bot.getInventory(InventoryType.USE).getItem(useSlot);
        int after = afterItem == null ? 0 : afterItem.getQuantity();
        return new ShopResult(after > before, npcId, shop.getId(), item.getItemId(), after - before,
                mesosBefore - bot.getMeso(), after > before ? "recharged" : "recharge-rejected");
    }

    public static RestockResult tickRestock(Character bot) {
        if (!eligible(bot)) return RestockResult.none("not-eligible");
        Supply supply = supply(bot);
        if (!supply.needsAnything()) return RestockResult.none("stocked");

        NPC npc = BotNpcDriver.nearestNpc(bot, true);
        if (npc == null) return RestockResult.none("no-shop-on-map");
        if (bot.getPosition().distanceSq(npc.getPosition()) > (double) INTERACT_RANGE * INTERACT_RANGE) {
            GCMovement.move(bot, npc.getPosition().x, npc.getPosition().y);
            return new RestockResult(true, true, false, npc.getId(), 0, 0, "moving-to-shop");
        }

        GCMovement.stop(bot);
        Shop shop = ShopFactory.getInstance().getShopForNPC(npc.getId());
        if (shop == null) return RestockResult.none("shop-unavailable");
        shop.sendShop(bot.getClient());

        int bought = 0;
        int recharged = 0;
        if (supply.hpCount < POTION_LOW_WATER) bought += buyBestPotion(bot, shop, true, false, POTION_TARGET - supply.hpCount);
        if (supply.mpCount < POTION_LOW_WATER) bought += buyBestPotion(bot, shop, false, true, POTION_TARGET - supply.mpCount);

        for (Item item : bot.getInventory(InventoryType.USE).list()) {
            if (item == null || !ItemConstants.isRechargeable(item.getItemId())) continue;
            int before = item.getQuantity();
            shop.recharge(bot.getClient(), item.getPosition());
            if (item.getQuantity() > before) recharged++;
        }

        if (supply.needsAmmo && !hasRechargeable(bot)) {
            ShopItem ammo = shop.getItems().stream()
                    .filter(i -> i.getPrice() > 0 && ItemConstants.isRechargeable(i.getItemId()))
                    .min(Comparator.comparingInt(ShopItem::getPrice))
                    .orElse(null);
            if (ammo != null) {
                short slot = shop.findSlotByItemId(ammo.getItemId());
                int before = bot.getInventory(InventoryType.USE).countById(ammo.getItemId());
                shop.buy(bot.getClient(), slot, ammo.getItemId(), (short) 1);
                if (bot.getInventory(InventoryType.USE).countById(ammo.getItemId()) > before) bought++;
            }
        }

        boolean changed = bought > 0 || recharged > 0;
        return new RestockResult(changed, false, true, npc.getId(), bought, recharged,
                changed ? "restocked" : "shop-could-not-restock");
    }

    private static int buyBestPotion(Character bot, Shop shop, boolean hp, boolean mp, int wanted) {
        if (wanted <= 0) return 0;
        ItemInformationProvider ii = ItemInformationProvider.getInstance();
        ShopItem best = shop.getItems().stream()
                .filter(item -> item.getPrice() > 0 && !ItemConstants.isRechargeable(item.getItemId()))
                .filter(item -> {
                    StatEffect effect = ii.getItemEffect(item.getItemId());
                    if (effect == null) return false;
                    boolean healsHp = effect.getHp() > 0 || effect.getHpRate() > 0.0;
                    boolean healsMp = effect.getMp() > 0 || effect.getMpRate() > 0.0;
                    return (!hp || healsHp) && (!mp || healsMp);
                })
                .min(Comparator.comparingInt(ShopItem::getPrice))
                .orElse(null);
        if (best == null) return 0;
        int affordable = best.getPrice() <= 0 ? 0 : bot.getMeso() / best.getPrice();
        int qty = Math.min(wanted, Math.min(affordable, Short.MAX_VALUE));
        if (qty <= 0) return 0;
        InventoryType type = ItemConstants.getInventoryType(best.getItemId());
        int before = bot.getInventory(type).countById(best.getItemId());
        shop.buy(bot.getClient(), shop.findSlotByItemId(best.getItemId()), best.getItemId(), (short) qty);
        return Math.max(0, bot.getInventory(type).countById(best.getItemId()) - before);
    }

    private static Supply supply(Character bot) {
        int hp = 0;
        int mp = 0;
        ItemInformationProvider ii = ItemInformationProvider.getInstance();
        for (Item item : bot.getInventory(InventoryType.USE).list()) {
            if (item == null || item.getQuantity() <= 0) continue;
            StatEffect effect = ii.getItemEffect(item.getItemId());
            if (effect != null) {
                if (effect.getHp() > 0 || effect.getHpRate() > 0.0) hp += item.getQuantity();
                if (effect.getMp() > 0 || effect.getMpRate() > 0.0) mp += item.getQuantity();
            }
        }
        boolean needsAmmo = needsRechargeableForJob(bot.getJob().getId());
        return new Supply(hp, mp, needsAmmo && !hasRechargeable(bot));
    }

    private static boolean hasRechargeable(Character bot) {
        for (Item item : bot.getInventory(InventoryType.USE).list()) {
            if (item != null && item.getQuantity() > 0 && ItemConstants.isRechargeable(item.getItemId())) return true;
        }
        return false;
    }

    private static boolean needsRechargeableForJob(int jobId) {
        return (jobId >= 410 && jobId <= 412)
                || (jobId >= 520 && jobId <= 522)
                || (jobId >= 1400 && jobId <= 1412);
    }

    private static boolean eligible(Character bot) {
        return bot != null && BotHelpers.isBot(bot) && bot.getClient() != null && bot.getMap() != null && bot.getPosition() != null;
    }

    private record Supply(int hpCount, int mpCount, boolean needsAmmo) {
        boolean needsAnything() {
            return hpCount < POTION_LOW_WATER || mpCount < POTION_LOW_WATER || needsAmmo;
        }
    }

    public record ShopResult(boolean success, int npcId, int shopId, int itemId, int quantity, int mesos, String reason) {
        static ShopResult fail(String reason) { return new ShopResult(false, 0, 0, 0, 0, 0, reason); }
    }

    public record RestockResult(boolean active, boolean moving, boolean attempted, int npcId, int bought, int recharged, String reason) {
        static RestockResult none(String reason) { return new RestockResult(false, false, false, 0, 0, 0, reason); }
    }
}

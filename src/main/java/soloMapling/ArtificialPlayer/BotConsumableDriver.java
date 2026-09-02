package soloMapling.ArtificialPlayer;

import client.Character;
import client.inventory.Inventory;
import client.inventory.InventoryType;
import client.inventory.Item;
import server.ItemInformationProvider;
import server.StatEffect;

/** Uses ordinary EverLeaf USE-inventory items for headless QA survival. */
public final class BotConsumableDriver {
    private static final double HP_THRESHOLD = 0.50;
    private static final double MP_THRESHOLD = 0.35;
    private static final long USE_COOLDOWN_MS = 750L;

    private static long lastUseAt;

    private BotConsumableDriver() {}

    public static UseResult tick(Character bot) {
        if (bot == null || !BotHelpers.isBot(bot) || !bot.isAlive()) {
            return UseResult.none("not-eligible");
        }
        long now = System.currentTimeMillis();
        if (now - lastUseAt < USE_COOLDOWN_MS) {
            return UseResult.none("cooldown");
        }

        double hpRatio = bot.getMaxHp() <= 0 ? 1.0 : (double) bot.getHp() / bot.getMaxHp();
        double mpRatio = bot.getMaxMp() <= 0 ? 1.0 : (double) bot.getMp() / bot.getMaxMp();
        boolean wantsHp = hpRatio <= HP_THRESHOLD;
        boolean wantsMp = mpRatio <= MP_THRESHOLD;
        if (!wantsHp && !wantsMp) {
            return UseResult.none("healthy");
        }

        Inventory use = bot.getInventory(InventoryType.USE);
        ItemInformationProvider ii = ItemInformationProvider.getInstance();
        for (Item item : use.list()) {
            if (item == null || item.getQuantity() <= 0) continue;
            StatEffect effect = ii.getItemEffect(item.getItemId());
            if (effect == null) continue;

            boolean restoresHp = effect.getHp() > 0 || effect.getHpRate() > 0.0;
            boolean restoresMp = effect.getMp() > 0 || effect.getMpRate() > 0.0;
            if (!((wantsHp && restoresHp) || (wantsMp && restoresMp))) continue;

            // Apply the same server-authoritative item effect used by UseItemHandler, then
            // consume exactly one item from the bot's real USE inventory on success.
            if (!effect.applyTo(bot)) continue;
            use.removeItem(item.getPosition(), (short) 1, false);
            lastUseAt = now;
            return new UseResult(true, item.getItemId(), wantsHp && restoresHp, wantsMp && restoresMp, "used");
        }

        return UseResult.none("out-of-potions");
    }

    public static record UseResult(boolean used, int itemId, boolean healedHp, boolean restoredMp, String reason) {
        static UseResult none(String reason) {
            return new UseResult(false, 0, false, false, reason);
        }
    }
}

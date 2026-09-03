package soloMapling.ArtificialPlayer;

import client.Character;
import client.inventory.Inventory;
import client.inventory.InventoryType;
import client.inventory.Item;
import client.inventory.manipulator.InventoryManipulator;
import constants.inventory.ItemConstants;
import server.ItemInformationProvider;
import server.Trade;

/** Uses EverLeaf's real Trade container/handshake for controlled player/bot and bot/bot QA. */
public final class BotTradeDriver {
    private BotTradeDriver() {}

    public static TradeResult open(Character initiator, Character partner) {
        if (!eligible(initiator) || !eligible(partner)) return TradeResult.fail("not-eligible");
        if (initiator == partner) return TradeResult.fail("same-character");
        if (initiator.getMap() != partner.getMap()) return TradeResult.fail("different-map");
        if (initiator.getTrade() != null || partner.getTrade() != null) return TradeResult.fail("already-trading");

        Trade.startTrade(initiator);
        Trade.inviteTrade(initiator, partner);
        if (initiator.getTrade() == null || partner.getTrade() == null) {
            cancelQuietly(initiator);
            cancelQuietly(partner);
            return TradeResult.fail("invite-rejected");
        }
        Trade.visitTrade(partner, initiator);
        return active(initiator, partner)
                ? status(initiator, partner, "opened")
                : TradeResult.fail("accept-rejected");
    }

    /** Accepts a normal pending trade invitation when the bot did not initiate it. */
    public static TradeResult accept(Character bot, Character partner) {
        if (!eligible(bot) || !eligible(partner)) return TradeResult.fail("not-eligible");
        if (bot.getTrade() == null || partner.getTrade() == null) return TradeResult.fail("no-pending-trade");
        if (bot.getTrade().getPartner() != partner.getTrade()) return TradeResult.fail("wrong-partner");
        if (!bot.getTrade().isFullTrade() && !partner.getTrade().isFullTrade()) {
            Trade.visitTrade(bot, partner);
        }
        return active(bot, partner) ? status(bot, partner, "accepted") : TradeResult.fail("accept-rejected");
    }

    public static TradeResult offerMesos(Character bot, int mesos) {
        if (!eligible(bot) || bot.getTrade() == null || !bot.getTrade().isFullTrade()) return TradeResult.fail("no-active-trade");
        if (mesos < 0 || bot.getMeso() < mesos) return TradeResult.fail("insufficient-mesos");
        int before = bot.getMeso();
        bot.getTrade().setMeso(mesos);
        int reserved = before - bot.getMeso();
        return new TradeResult(reserved == mesos, partnerId(bot), 0, reserved,
                reserved == mesos ? "mesos-offered" : "mesos-rejected");
    }

    public static TradeResult offerItem(Character bot, InventoryType type, short slot, short quantity) {
        if (!eligible(bot) || bot.getTrade() == null || !bot.getTrade().isFullTrade()) return TradeResult.fail("no-active-trade");
        if (type == null || type == InventoryType.UNDEFINED || type == InventoryType.EQUIPPED || quantity <= 0) {
            return TradeResult.fail("invalid-item-request");
        }

        Inventory inventory = bot.getInventory(type);
        inventory.lockInventory();
        try {
            Item item = inventory.getItem(slot);
            if (item == null || item.getQuantity() < quantity) return TradeResult.fail("item-not-present");
            if (item.isUntradeable() || ItemInformationProvider.getInstance().isUnmerchable(item.getItemId())) {
                return TradeResult.fail("item-not-tradeable");
            }

            if (ItemConstants.isRechargeable(item.getItemId())) quantity = item.getQuantity();
            Item tradeItem = item.copy();
            tradeItem.setQuantity(quantity);
            tradeItem.setPosition((short) (bot.getTrade().getItems().size() + 1));
            if (!bot.getTrade().addItem(tradeItem)) return TradeResult.fail("trade-container-rejected");

            InventoryManipulator.removeFromSlot(bot.getClient(), type, slot, quantity, true);
            return new TradeResult(true, partnerId(bot), item.getItemId(), quantity, "item-offered");
        } finally {
            inventory.unlockInventory();
        }
    }

    public static TradeResult confirm(Character bot) {
        if (!eligible(bot) || bot.getTrade() == null || !bot.getTrade().isFullTrade()) return TradeResult.fail("no-active-trade");
        int partnerId = partnerId(bot);
        Trade.completeTrade(bot);
        return new TradeResult(true, partnerId, 0, 0, bot.getTrade() == null ? "completed" : "confirmed");
    }

    /** Confirms both sides, exercising the normal two-party Trade handshake and settlement. */
    public static TradeResult confirmBoth(Character first, Character second) {
        if (!active(first, second)) return TradeResult.fail("no-active-trade");
        int secondId = second.getId();
        Trade.completeTrade(first);
        if (first.getTrade() != null && second.getTrade() != null) Trade.completeTrade(second);
        boolean complete = first.getTrade() == null && second.getTrade() == null;
        return new TradeResult(complete, secondId, 0, 0, complete ? "completed" : "settlement-rejected");
    }

    public static TradeResult cancel(Character bot) {
        if (!eligible(bot) || bot.getTrade() == null) return TradeResult.fail("no-active-trade");
        int partner = partnerId(bot);
        Trade.cancelTrade(bot, Trade.TradeResult.PARTNER_CANCEL);
        return new TradeResult(bot.getTrade() == null, partner, 0, 0,
                bot.getTrade() == null ? "cancelled" : "cancel-rejected");
    }

    private static void cancelQuietly(Character bot) {
        if (bot != null && bot.getTrade() != null) {
            try { Trade.cancelTrade(bot, Trade.TradeResult.UNSUCCESSFUL); }
            catch (RuntimeException ignored) { }
        }
    }

    private static boolean active(Character first, Character second) {
        return eligible(first) && eligible(second)
                && first.getTrade() != null && second.getTrade() != null
                && first.getTrade().getPartner() == second.getTrade()
                && second.getTrade().getPartner() == first.getTrade()
                && first.getTrade().isFullTrade() && second.getTrade().isFullTrade();
    }

    private static int partnerId(Character bot) {
        return bot != null && bot.getTrade() != null && bot.getTrade().getPartner() != null
                ? bot.getTrade().getPartner().getChr().getId() : -1;
    }

    private static TradeResult status(Character first, Character second, String reason) {
        return new TradeResult(true, second.getId(), 0, 0, reason);
    }

    private static boolean eligible(Character chr) {
        return chr != null && chr.getClient() != null && chr.isLoggedinWorld() && chr.getMap() != null && chr.isAlive();
    }

    public record TradeResult(boolean success, int partnerId, int itemId, int amount, String reason) {
        static TradeResult fail(String reason) { return new TradeResult(false, -1, 0, 0, reason); }
    }
}

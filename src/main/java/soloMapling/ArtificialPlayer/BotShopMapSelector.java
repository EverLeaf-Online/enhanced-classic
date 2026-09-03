package soloMapling.ArtificialPlayer;

import client.Character;

import java.util.Map;

/**
 * Safe v83 restock destinations for autonomous QA bots.
 *
 * <p>These are ordinary town shop maps from the same v83 world the player can reach.
 * GCTravel still owns the actual route and portal/taxi/scripted-warp behavior. Keeping
 * selection separate from travel makes failed routes visible and prevents the hunter
 * from pretending the town return map itself necessarily contains a shop NPC.</p>
 */
public final class BotShopMapSelector {
    private static final Map<Integer, Integer> POTION_SHOPS = Map.ofEntries(
            Map.entry(100000000, 100000102), // Henesys Market / potion shop
            Map.entry(101000000, 101000002), // Ellinia
            Map.entry(102000000, 102000002), // Perion
            Map.entry(103000000, 103000002), // Kerning City
            Map.entry(104000000, 104000002), // Lith Harbor
            Map.entry(200000000, 200000002), // Orbis
            Map.entry(211000000, 211000102), // El Nath
            Map.entry(220000000, 220000002), // Ludibrium
            // Sleepywood has no normal potion/equipment shop. Route its QA restock trip
            // to Kerning rather than silently giving the bot inventory.
            Map.entry(105040300, 103000002)
    );

    private BotShopMapSelector() {}

    public static int select(Character bot) {
        if (bot == null || bot.getMap() == null) return -1;
        int currentMapId = bot.getMapId();
        Integer direct = POTION_SHOPS.get(currentMapId);
        if (direct != null) return direct;

        int returnMapId = bot.getMap().getReturnMapId();
        Integer fromReturn = POTION_SHOPS.get(returnMapId);
        if (fromReturn != null) return fromReturn;

        // Some maps return directly to a shop/interior or a town that actually has a
        // merchant on-map. Let BotShopDriver verify it instead of inventing a warp.
        return returnMapId > 0 ? returnMapId : -1;
    }
}

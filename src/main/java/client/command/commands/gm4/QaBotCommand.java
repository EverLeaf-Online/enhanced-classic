package client.command.commands.gm4;

import client.Character;
import client.Client;
import client.command.Command;
import client.inventory.InventoryType;
import soloMapling.ArtificialPlayer.BareBotAutopilot;
import soloMapling.ArtificialPlayer.BareBotCombat;
import soloMapling.ArtificialPlayer.BareBotFactory;
import soloMapling.ArtificialPlayer.BareBotHunter;
import soloMapling.ArtificialPlayer.BareBotMovement;
import soloMapling.ArtificialPlayer.BareBotPortal;
import soloMapling.ArtificialPlayer.BotLootDriver;
import soloMapling.ArtificialPlayer.BotNpcDriver;
import soloMapling.ArtificialPlayer.BotQaFleet;
import soloMapling.ArtificialPlayer.BotQaProfile;
import soloMapling.ArtificialPlayer.BotQaSoak;
import soloMapling.ArtificialPlayer.BotShopDriver;
import soloMapling.ArtificialPlayer.BotAttackSystem.BotAttackDriver;
import soloMapling.ArtificialPlayer.GCMoveSystem.GCMovement;
import soloMapling.ArtificialPlayer.GCMoveSystem.GCMovementDiagnostics;
import tools.exceptions.EmptyMovementException;

import java.awt.Point;
import java.sql.SQLException;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/** GM-only control surface for isolated SoloMapling QA bots. */
public class QaBotCommand extends Command {
    private static final int QA_WORLD = 0;
    private static final int QA_CHANNEL = 1;
    private static final Map<Integer, Character> spawnedByGm = new ConcurrentHashMap<>();

    {
        setDescription("Control SoloMapling QA: !qabot spawn|remove|status|job|npc|shop|nudge|move|gcmove|gcstop|strike|attack|hunt|patrol|portal|fleet|soak");
    }

    @Override
    public void execute(Client c, String[] params) {
        if (params.length < 1) {
            usage(c);
            return;
        }

        String action = params[0].toLowerCase();
        boolean cleanupAction = action.equals("remove")
                || (action.equals("fleet") && params.length >= 2 && !params[1].equalsIgnoreCase("spawn"))
                || (action.equals("soak") && params.length >= 2 && !params[1].equalsIgnoreCase("start"));
        if (!cleanupAction && !onQaChannel(c)) {
            c.getPlayer().yellowMessage("SoloMapling QA bots currently run only on world 0, channel 1.");
            return;
        }

        switch (action) {
            case "spawn" -> spawn(c);
            case "remove" -> remove(c);
            case "status" -> status(c);
            case "job", "profile" -> profile(c, params);
            case "npc" -> npc(c, params);
            case "shop" -> shop(c, params);
            case "nudge" -> nudge(c, params);
            case "move" -> move(c, params);
            case "gcmove" -> gcMove(c, params);
            case "gcstop" -> gcStop(c);
            case "strike" -> strike(c, params);
            case "attack" -> attack(c, params);
            case "hunt" -> hunt(c, params);
            case "patrol" -> patrol(c, params);
            case "portal" -> portal(c, params);
            case "fleet" -> fleet(c, params);
            case "soak" -> soak(c, params);
            default -> usage(c);
        }
    }

    private static void spawn(Client c) {
        int gmId = c.getPlayer().getId();
        Character previous = spawnedByGm.remove(gmId);
        if (previous != null) {
            stopAll(previous);
            BareBotFactory.removeBareBot(previous);
        }
        try {
            Character bot = BareBotFactory.createBareBot(gmId, c.getPlayer().getPosition(), c.getPlayer().getMap());
            spawnedByGm.put(gmId, bot);
            c.getPlayer().yellowMessage("Spawned SoloMapling QA bot " + bot.getName() + " (" + bot.getId() + ").");
        } catch (SQLException | RuntimeException e) {
            c.getPlayer().yellowMessage("QA bot spawn failed: " + e.getMessage());
        }
    }

    private static void remove(Client c) {
        Character bot = spawnedByGm.remove(c.getPlayer().getId());
        if (bot == null) {
            c.getPlayer().yellowMessage("No QA bot is registered to you.");
            return;
        }
        stopAll(bot);
        BotAttackDriver.clearBot(bot.getId());
        BareBotFactory.removeBareBot(bot);
        c.getPlayer().yellowMessage("Removed SoloMapling QA bot " + bot.getName() + ".");
    }

    private static void status(Client c) {
        Character bot = getBot(c);
        if (bot == null) return;
        Point position = bot.getPosition();
        BotLootDriver.RewardStats rewards = BotLootDriver.rewardStats(bot);
        c.getPlayer().yellowMessage(
                "QA bot " + bot.getName() + " (" + bot.getId() + ") job=" + bot.getJob().getId()
                        + " map=" + bot.getMapId() + " pos=" + position.x + "," + position.y
                        + " HP=" + bot.getHp() + "/" + bot.getMaxHp()
                        + " MP=" + bot.getMp() + "/" + bot.getMaxMp()
                        + " GCMove=" + (GCMovement.isEnabled(bot) ? "ON" : "OFF")
                        + " hunt=" + (BareBotHunter.isHunting(bot) ? "ON" : "OFF")
                        + " patrol=" + (BareBotAutopilot.isPatrolling(bot) ? "ON" : "OFF") + ".");
        c.getPlayer().yellowMessage(
                "QA rewards: level=" + bot.getLevel()
                        + " exp=" + bot.getExp()
                        + " mesos=" + bot.getMeso()
                        + " ownedDrops=" + rewards.ownedDrops()
                        + " observedDrops=" + rewards.observedDrops()
                        + " pickedDrops=" + rewards.pickedDrops() + ".");
        c.getPlayer().yellowMessage(GCMovementDiagnostics.describe(bot));
    }

    private static void profile(Client c, String[] params) {
        if (params.length != 2) { usage(c); return; }
        Character bot = getBot(c);
        if (bot == null) return;
        int jobId;
        try {
            jobId = Integer.parseInt(params[1]);
        } catch (NumberFormatException e) {
            c.getPlayer().yellowMessage("job requires a MapleStory job id, e.g. 512, 1212, 2112, or 2218.");
            return;
        }
        stopAll(bot);
        BotQaProfile.ProfileResult result = BotQaProfile.apply(bot, jobId);
        if (!result.applied()) {
            c.getPlayer().yellowMessage("QA bot class profile failed: " + result.reason());
            return;
        }
        c.getPlayer().yellowMessage("QA bot profile set to job " + result.job().getId()
                + " with " + result.learnedSkills() + " QA combat/support skills maxed.");
    }

    private static void npc(Client c, String[] params) {
        if (params.length < 2 || params.length > 3) { usage(c); return; }
        Character bot = getBot(c);
        if (bot == null) return;
        String mode = params[1].toLowerCase();
        BotNpcDriver.InteractionResult result;
        if (mode.equals("nearest")) {
            stopAll(bot);
            result = BotNpcDriver.startNearest(bot);
        } else if (mode.equals("next")) {
            int selection = 0;
            if (params.length == 3) {
                try { selection = Integer.parseInt(params[2]); }
                catch (NumberFormatException e) { c.getPlayer().yellowMessage("npc next selection must be an integer."); return; }
            }
            result = BotNpcDriver.next(bot, selection);
        } else if (mode.equals("cancel")) {
            BotNpcDriver.cancel(bot);
            c.getPlayer().yellowMessage("QA bot NPC dialogue cancelled.");
            return;
        } else {
            if (params.length != 2) { usage(c); return; }
            int npcId;
            try { npcId = Integer.parseInt(params[1]); }
            catch (NumberFormatException e) { c.getPlayer().yellowMessage("npc requires nearest, next [selection], cancel, or an NPC id."); return; }
            stopAll(bot);
            result = BotNpcDriver.start(bot, npcId);
        }
        if (result.success()) {
            c.getPlayer().yellowMessage("QA bot NPC interaction " + result.reason() + " npc=" + result.npcId()
                    + (result.npcName().isEmpty() ? "." : " (" + result.npcName() + ")."));
        } else {
            c.getPlayer().yellowMessage("QA bot NPC interaction failed: " + result.reason() + ".");
        }
    }

    private static void shop(Client c, String[] params) {
        if (params.length < 2) { usage(c); return; }
        Character bot = getBot(c);
        if (bot == null) return;
        String mode = params[1].toLowerCase();
        try {
            switch (mode) {
                case "nearest", "open" -> {
                    stopAll(bot);
                    BotShopDriver.ShopResult result = params.length == 3
                            ? BotShopDriver.open(bot, Integer.parseInt(params[2]))
                            : BotShopDriver.openNearest(bot);
                    reportShop(c, result);
                }
                case "buy" -> {
                    if (params.length != 5) { usage(c); return; }
                    BotShopDriver.ShopResult result = BotShopDriver.buy(bot,
                            Integer.parseInt(params[2]), Integer.parseInt(params[3]), Short.parseShort(params[4]));
                    reportShop(c, result);
                }
                case "sell" -> {
                    if (params.length != 6) { usage(c); return; }
                    InventoryType type = InventoryType.getByType(Byte.parseByte(params[3]));
                    if (type == null || type == InventoryType.UNDEFINED || type == InventoryType.EQUIPPED) {
                        c.getPlayer().yellowMessage("shop sell inventory type must be 1=EQUIP, 2=USE, 3=SETUP, 4=ETC, or 5=CASH.");
                        return;
                    }
                    BotShopDriver.ShopResult result = BotShopDriver.sell(bot, Integer.parseInt(params[2]), type,
                            Short.parseShort(params[4]), Short.parseShort(params[5]));
                    reportShop(c, result);
                }
                case "recharge" -> {
                    if (params.length != 4) { usage(c); return; }
                    BotShopDriver.ShopResult result = BotShopDriver.recharge(bot,
                            Integer.parseInt(params[2]), Short.parseShort(params[3]));
                    reportShop(c, result);
                }
                case "restock" -> {
                    if (params.length != 2) { usage(c); return; }
                    BotShopDriver.RestockResult result = BotShopDriver.tickRestock(bot);
                    c.getPlayer().yellowMessage("QA restock: " + result.reason()
                            + " npc=" + result.npcId() + " bought=" + result.bought() + " recharged=" + result.recharged() + ".");
                }
                default -> usage(c);
            }
        } catch (NumberFormatException e) {
            c.getPlayer().yellowMessage("QA shop command contains an invalid numeric value.");
        }
    }

    private static void reportShop(Client c, BotShopDriver.ShopResult result) {
        if (!result.success()) {
            c.getPlayer().yellowMessage("QA shop action failed: " + result.reason() + ".");
            return;
        }
        c.getPlayer().yellowMessage("QA shop " + result.reason() + ": npc=" + result.npcId()
                + " shop=" + result.shopId() + " item=" + result.itemId()
                + " qty=" + result.quantity() + " mesos=" + result.mesos() + ".");
    }

    private static void nudge(Client c, String[] params) {
        if (params.length != 2) { usage(c); return; }
        Character bot = getBot(c);
        if (bot == null) return;
        try {
            int deltaX = Integer.parseInt(params[1]);
            stopAll(bot);
            BareBotMovement.nudge(bot, deltaX);
            c.getPlayer().yellowMessage("Moved QA bot by " + deltaX + " X.");
        } catch (NumberFormatException e) {
            c.getPlayer().yellowMessage("nudge requires an integer X offset.");
        } catch (EmptyMovementException | RuntimeException e) {
            c.getPlayer().yellowMessage("QA bot movement failed: " + e.getMessage());
        }
    }

    private static void move(Client c, String[] params) {
        if (params.length != 3) { usage(c); return; }
        Character bot = getBot(c);
        if (bot == null) return;
        try {
            int x = Integer.parseInt(params[1]);
            int y = Integer.parseInt(params[2]);
            stopAll(bot);
            BareBotMovement.moveTo(bot, new Point(x, y));
            c.getPlayer().yellowMessage("Moved QA bot to " + x + ", " + y + ".");
        } catch (NumberFormatException e) {
            c.getPlayer().yellowMessage("move requires integer X and Y coordinates.");
        } catch (EmptyMovementException | RuntimeException e) {
            c.getPlayer().yellowMessage("QA bot movement failed: " + e.getMessage());
        }
    }

    private static void gcMove(Client c, String[] params) {
        if (params.length != 3) { usage(c); return; }
        Character bot = getBot(c);
        if (bot == null) return;
        try {
            int x = Integer.parseInt(params[1]);
            int y = Integer.parseInt(params[2]);
            BareBotHunter.stop(bot);
            BareBotAutopilot.stop(bot);
            GCMovement.move(bot, x, y);
            c.getPlayer().yellowMessage("GCMove target set for QA bot: " + x + ", " + y + ".");
        } catch (NumberFormatException e) {
            c.getPlayer().yellowMessage("gcmove requires integer X and Y coordinates.");
        } catch (RuntimeException e) {
            GCMovement.disable(bot);
            c.getPlayer().yellowMessage("GCMove failed: " + e.getMessage());
        }
    }

    private static void gcStop(Client c) {
        Character bot = getBot(c);
        if (bot == null) return;
        BareBotHunter.stop(bot);
        GCMovement.disable(bot);
        c.getPlayer().yellowMessage("GCMove disabled for QA bot.");
    }

    private static void strike(Client c, String[] params) {
        if (params.length > 2) { usage(c); return; }
        Character bot = getBot(c);
        if (bot == null) return;
        int damage = 1;
        if (params.length == 2) {
            try { damage = Integer.parseInt(params[1]); }
            catch (NumberFormatException e) { c.getPlayer().yellowMessage("strike damage must be an integer."); return; }
        }
        BareBotCombat.StrikeResult result = BareBotCombat.strikeNearest(bot, damage);
        if (!result.hit()) {
            c.getPlayer().yellowMessage("QA bot strike skipped: " + result.reason());
            return;
        }
        c.getPlayer().yellowMessage("QA bot server-struck " + result.monsterName() + " (" + result.monsterId() + ") for "
                + result.damage() + (result.killed() ? " and killed it." : "; HP left " + result.remainingHp() + "."));
    }

    private static void attack(Client c, String[] params) {
        if (params.length > 2) { usage(c); return; }
        Character bot = getBot(c);
        if (bot == null) return;
        BotAttackDriver.AttackResult result;
        String mode = params.length == 2 ? params[1].toLowerCase() : "single";
        switch (mode) {
            case "single" -> result = BotAttackDriver.forceSingle(bot);
            case "aoe" -> result = BotAttackDriver.forceAoe(bot);
            case "ult", "ultimate" -> result = BotAttackDriver.forceUltimate(bot);
            default -> { c.getPlayer().yellowMessage("attack mode must be single, aoe, or ult."); return; }
        }
        if (!result.hit()) {
            c.getPlayer().yellowMessage("QA bot attack skipped: " + result.reason());
            return;
        }
        c.getPlayer().yellowMessage("QA bot visible attack hit " + result.monsterName() + " for " + result.damage()
                + (result.killed() ? " and killed at least one target." : "."));
    }

    private static void hunt(Client c, String[] params) {
        if (params.length != 2) { usage(c); return; }
        Character bot = getBot(c);
        if (bot == null) return;
        switch (params[1].toLowerCase()) {
            case "start" -> {
                if (BareBotHunter.start(bot)) c.getPlayer().yellowMessage("QA bot autonomous SoloMapling hunt started.");
                else c.getPlayer().yellowMessage("QA bot hunt could not start.");
            }
            case "stop" -> {
                BareBotHunter.stop(bot);
                c.getPlayer().yellowMessage("QA bot autonomous hunt stopped.");
            }
            default -> usage(c);
        }
    }

    private static void patrol(Client c, String[] params) {
        if (params.length != 2) { usage(c); return; }
        Character bot = getBot(c);
        if (bot == null) return;
        switch (params[1].toLowerCase()) {
            case "start" -> {
                BareBotHunter.stop(bot);
                GCMovement.disable(bot);
                if (BareBotAutopilot.startPatrol(bot)) c.getPlayer().yellowMessage("QA bot autonomous foothold patrol started.");
                else c.getPlayer().yellowMessage("QA bot patrol could not start.");
            }
            case "stop" -> {
                BareBotAutopilot.stop(bot);
                c.getPlayer().yellowMessage("QA bot autonomous foothold patrol stopped.");
            }
            default -> usage(c);
        }
    }

    private static void portal(Client c, String[] params) {
        if (params.length != 2) { usage(c); return; }
        Character bot = getBot(c);
        if (bot == null) return;
        int portalId;
        try { portalId = Integer.parseInt(params[1]); }
        catch (NumberFormatException e) { c.getPlayer().yellowMessage("portal requires an integer portal id."); return; }
        stopAll(bot);
        BareBotPortal.PortalResult result = BareBotPortal.enter(bot, portalId);
        if (result.success()) c.getPlayer().yellowMessage("QA bot traversed portal " + portalId + ": " + result.fromMapId() + " -> " + result.toMapId() + ".");
        else c.getPlayer().yellowMessage("QA bot portal traversal failed: " + result.reason());
    }

    private static void fleet(Client c, String[] params) {
        if (params.length < 2 || params.length > 4) { usage(c); return; }
        int ownerId = c.getPlayer().getId();
        switch (params[1].toLowerCase()) {
            case "spawn" -> {
                if (params.length < 3 || params.length > 4) { usage(c); return; }
                try {
                    int count = Integer.parseInt(params[2]);
                    int mapId = params.length == 4 ? Integer.parseInt(params[3]) : c.getPlayer().getMapId();
                    if (BotQaSoak.isRunning(ownerId)) BotQaSoak.stop(ownerId);
                    BotQaFleet.FleetResult result = BotQaFleet.spawn(ownerId, ownerId, count, QA_WORLD, QA_CHANNEL, mapId);
                    reportFleet(c, result);
                } catch (NumberFormatException e) {
                    c.getPlayer().yellowMessage("fleet spawn requires an integer count and optional map id.");
                }
            }
            case "status" -> reportFleet(c, BotQaFleet.status(ownerId));
            case "remove" -> {
                if (BotQaSoak.isRunning(ownerId)) {
                    reportSoak(c, BotQaSoak.stop(ownerId));
                } else {
                    reportFleet(c, BotQaFleet.remove(ownerId));
                }
            }
            default -> usage(c);
        }
    }

    private static void soak(Client c, String[] params) {
        if (params.length < 2 || params.length > 3) { usage(c); return; }
        int ownerId = c.getPlayer().getId();
        switch (params[1].toLowerCase()) {
            case "start" -> {
                if (params.length != 3) { usage(c); return; }
                try {
                    reportSoak(c, BotQaSoak.start(ownerId, Integer.parseInt(params[2])));
                } catch (NumberFormatException e) {
                    c.getPlayer().yellowMessage("soak start requires an integer duration in minutes.");
                }
            }
            case "status" -> reportSoak(c, BotQaSoak.status(ownerId));
            case "stop" -> reportSoak(c, BotQaSoak.stop(ownerId));
            default -> usage(c);
        }
    }

    private static void reportFleet(Client c, BotQaFleet.FleetResult result) {
        if (!result.success()) {
            c.getPlayer().yellowMessage("QA fleet: " + result.reason() + ".");
            return;
        }
        c.getPlayer().yellowMessage("QA fleet " + result.reason()
                + ": bots=" + result.bots()
                + " alive=" + result.alive()
                + " logged=" + result.loggedInWorld()
                + " autonomous=" + result.autonomous()
                + " map=" + result.mapId()
                + " factoryBots=" + result.globalFactoryBots()
                + " clients=" + result.headlessClients() + ".");
    }

    private static void reportSoak(Client c, BotQaSoak.Report report) {
        if (!report.accepted()) {
            c.getPlayer().yellowMessage("QA soak rejected: " + report.reason() + ".");
            return;
        }
        c.getPlayer().yellowMessage("QA soak " + report.reason()
                + ": running=" + report.running()
                + " bots=" + report.bots()
                + " elapsed=" + (report.elapsedMs() / 1000L) + "s"
                + " checks=" + report.checks()
                + " restarts=" + report.restarts()
                + " violations=" + report.violations()
                + " cleaned=" + report.cleanedUp() + ".");
        if (!"none".equals(report.details())) c.getPlayer().yellowMessage("QA soak details: " + report.details());
    }

    private static void stopAll(Character bot) {
        BareBotHunter.stop(bot);
        BareBotAutopilot.stop(bot);
        GCMovement.disable(bot);
        BotAttackDriver.clearBot(bot.getId());
        BotNpcDriver.cancel(bot);
    }

    private static boolean onQaChannel(Client c) {
        return c.getChannelServer() != null
                && c.getChannelServer().getWorld() == QA_WORLD
                && c.getChannelServer().getId() == QA_CHANNEL;
    }

    private static Character getBot(Client c) {
        Character bot = spawnedByGm.get(c.getPlayer().getId());
        if (bot == null) c.getPlayer().yellowMessage("Spawn a QA bot first with !qabot spawn.");
        return bot;
    }

    private static void usage(Client c) {
        c.getPlayer().yellowMessage("Usage: !qabot spawn|remove|status|job <jobId>|npc nearest|<npcId>|next [selection]|cancel|shop nearest|open [npcId]|buy <npcId> <itemId> <qty>|sell <npcId> <invType> <slot> <qty>|recharge <npcId> <useSlot>|restock|nudge <dx>|move <x> <y>|gcmove <x> <y>|gcstop|strike [damage]|attack [single|aoe|ult]|hunt start|stop|patrol start|stop|portal <id>|fleet spawn <1-12> [mapId]|status|remove|soak start <1-720 minutes>|status|stop");
    }
}

package client.command.commands.gm4;

import client.Character;
import client.Client;
import client.command.Command;
import client.inventory.InventoryType;
import soloMapling.ArtificialPlayer.BareBotHunter;
import soloMapling.ArtificialPlayer.BotBossDriver;
import soloMapling.ArtificialPlayer.BotPartyDriver;
import soloMapling.ArtificialPlayer.BotPqDriver;
import soloMapling.ArtificialPlayer.BotQaFleet;
import soloMapling.ArtificialPlayer.BotQaSoakRunner;
import soloMapling.ArtificialPlayer.BotQaSuiteRunner;
import soloMapling.ArtificialPlayer.BotQuestDriver;
import soloMapling.ArtificialPlayer.BotStorageDriver;
import soloMapling.ArtificialPlayer.BotTradeDriver;
import soloMapling.ArtificialPlayer.GCMoveSystem.GCMovement;

import java.util.List;

/**
 * GM-only advanced control surface for SoloMapling Batches 4-7 and Phase-2 hardening.
 *
 * <p>The existing !qabot command remains the single-bot movement/combat smoke surface. This command
 * controls the bounded multi-bot fleet and invokes the real EverLeaf party, trade, isolated QA
 * storage, quest, boss and PQ drivers plus explicit recovery/travel/soak/full-suite scenarios.</p>
 */
public class QaBotOpsCommand extends Command {
    private static final int QA_WORLD = 0;
    private static final int QA_CHANNEL = 1;

    {
        setDescription("Advanced SoloMapling QA: !qabotops fleet|travel|die|huntall|party|trade|storage|quest|boss|pq|soak|suite");
    }

    @Override
    public void execute(Client c, String[] params) {
        if (params.length < 1) {
            usage(c);
            return;
        }
        if (!onQaChannel(c) && !isCleanup(params)) {
            c.getPlayer().yellowMessage("SoloMapling advanced QA runs only on world 0, channel 1; cleanup commands remain available everywhere.");
            return;
        }

        try {
            switch (params[0].toLowerCase()) {
                case "fleet" -> fleet(c, params);
                case "travel" -> travel(c, params);
                case "die", "death" -> die(c, params);
                case "huntall" -> huntAll(c, params);
                case "party" -> party(c, params);
                case "trade" -> trade(c, params);
                case "storage" -> storage(c, params);
                case "quest" -> quest(c, params);
                case "boss" -> boss(c, params);
                case "pq" -> pq(c, params);
                case "soak" -> soak(c, params);
                case "suite" -> suite(c, params);
                default -> usage(c);
            }
        } catch (NumberFormatException e) {
            c.getPlayer().yellowMessage("SoloMapling QA command contains an invalid numeric value.");
        } catch (RuntimeException e) {
            c.getPlayer().yellowMessage("SoloMapling QA action failed: " + e.getMessage());
        }
    }

    private static void fleet(Client c, String[] p) {
        if (p.length < 2) { usage(c); return; }
        int owner = c.getPlayer().getId();
        switch (p[1].toLowerCase()) {
            case "spawn" -> {
                if (p.length != 3) { usage(c); return; }
                BotQaSuiteRunner.stop(owner);
                BotQaSoakRunner.stop(owner);
                BotQaFleet.FleetResult r = BotQaFleet.spawn(owner, owner, Integer.parseInt(p[2]), QA_WORLD,
                        QA_CHANNEL, c.getPlayer().getMapId());
                reportFleet(c, r);
            }
            case "status" -> reportFleet(c, BotQaFleet.status(owner));
            case "remove", "clear" -> {
                BotQaSuiteRunner.stop(owner);
                BotQaSoakRunner.stop(owner);
                reportFleet(c, BotQaFleet.remove(owner));
            }
            default -> usage(c);
        }
    }

    private static void travel(Client c, String[] p) {
        if (p.length != 3 && p.length != 5) { usage(c); return; }
        Character bot = bot(c, Integer.parseInt(p[1]));
        if (bot == null) return;
        int mapId = Integer.parseInt(p[2]);
        BareBotHunter.stop(bot);
        if (p.length == 5) {
            int x = Integer.parseInt(p[3]);
            int y = Integer.parseInt(p[4]);
            GCMovement.travelTo(bot, mapId, x, y,
                    ok -> { if (!ok) c.getPlayer().yellowMessage("QA bot travel failed for map " + mapId + "."); });
        } else {
            GCMovement.travel(bot, mapId);
        }
        c.getPlayer().yellowMessage("QA bot #" + p[1] + " travel armed: " + bot.getMapId() + " -> " + mapId + ".");
    }

    private static void die(Client c, String[] p) {
        if (p.length != 2) { usage(c); return; }
        Character bot = bot(c, Integer.parseInt(p[1]));
        if (bot == null) return;
        if (!BareBotHunter.isHunting(bot) && !BareBotHunter.start(bot)) {
            c.getPlayer().yellowMessage("Could not arm hunter recovery before death test.");
            return;
        }
        bot.updateHp(0);
        c.getPlayer().yellowMessage("QA bot #" + p[1] + " forced to 0 HP; autonomous death recovery is now under test.");
    }

    private static void huntAll(Client c, String[] p) {
        if (p.length != 2) { usage(c); return; }
        List<Character> bots = fleetBots(c);
        if (bots == null) return;
        int changed = 0;
        switch (p[1].toLowerCase()) {
            case "start" -> {
                for (Character bot : bots) if (BareBotHunter.start(bot)) changed++;
                c.getPlayer().yellowMessage("Started autonomous hunt on " + changed + "/" + bots.size() + " QA bots.");
            }
            case "stop" -> {
                for (Character bot : bots) { BareBotHunter.stop(bot); changed++; }
                c.getPlayer().yellowMessage("Stopped autonomous hunt on " + changed + " QA bots.");
            }
            default -> usage(c);
        }
    }

    private static void party(Client c, String[] p) {
        if (p.length < 3) { usage(c); return; }
        Character a = bot(c, Integer.parseInt(p[2]));
        if (a == null) return;
        BotPartyDriver.PartyResult r;
        switch (p[1].toLowerCase()) {
            case "create" -> r = BotPartyDriver.create(a);
            case "leave" -> r = BotPartyDriver.leave(a);
            case "status" -> r = BotPartyDriver.status(a);
            case "join" -> {
                if (p.length != 4) { usage(c); return; }
                Character leader = bot(c, Integer.parseInt(p[3]));
                if (leader == null) return;
                r = BotPartyDriver.join(a, leader);
            }
            case "leader" -> {
                if (p.length != 4) { usage(c); return; }
                Character b = bot(c, Integer.parseInt(p[3]));
                if (b == null) return;
                r = BotPartyDriver.transferLeader(a, b);
            }
            default -> { usage(c); return; }
        }
        c.getPlayer().yellowMessage("QA party: " + r.reason() + " success=" + r.success()
                + " party=" + r.partyId() + " leader=" + r.leaderId() + " members=" + r.members() + ".");
    }

    private static void trade(Client c, String[] p) {
        if (p.length < 3) { usage(c); return; }
        String mode = p[1].toLowerCase();
        Character a = bot(c, Integer.parseInt(p[2]));
        if (a == null) return;
        BotTradeDriver.TradeResult r;
        switch (mode) {
            case "open" -> {
                if (p.length != 4) { usage(c); return; }
                Character b = bot(c, Integer.parseInt(p[3]));
                if (b == null) return;
                r = BotTradeDriver.open(a, b);
            }
            case "mesos" -> {
                if (p.length != 4) { usage(c); return; }
                r = BotTradeDriver.offerMesos(a, Integer.parseInt(p[3]));
            }
            case "item" -> {
                if (p.length != 6) { usage(c); return; }
                InventoryType type = inventoryType(p[3]);
                if (type == null) { c.getPlayer().yellowMessage("Inventory type must be 1-5."); return; }
                r = BotTradeDriver.offerItem(a, type, Short.parseShort(p[4]), Short.parseShort(p[5]));
            }
            case "confirm" -> {
                if (p.length != 4) { usage(c); return; }
                Character b = bot(c, Integer.parseInt(p[3]));
                if (b == null) return;
                r = BotTradeDriver.confirmBoth(a, b);
            }
            case "cancel" -> r = BotTradeDriver.cancel(a);
            default -> { usage(c); return; }
        }
        c.getPlayer().yellowMessage("QA trade: " + r.reason() + " success=" + r.success()
                + " partner=" + r.partnerId() + " item=" + r.itemId() + " amount=" + r.amount() + ".");
    }

    private static void storage(Client c, String[] p) {
        if (p.length < 3) { usage(c); return; }
        Character bot = bot(c, Integer.parseInt(p[2]));
        if (bot == null) return;
        BotStorageDriver.StorageResult r;
        switch (p[1].toLowerCase()) {
            case "open" -> {
                if (p.length != 4) { usage(c); return; }
                r = BotStorageDriver.open(bot, Integer.parseInt(p[3]));
            }
            case "close" -> r = BotStorageDriver.close(bot);
            case "status" -> r = BotStorageDriver.status(bot);
            case "deposit" -> {
                if (p.length != 6) { usage(c); return; }
                InventoryType type = inventoryType(p[3]);
                if (type == null) { c.getPlayer().yellowMessage("Inventory type must be 1-5."); return; }
                r = BotStorageDriver.deposit(bot, type, Short.parseShort(p[4]), Short.parseShort(p[5]));
            }
            case "withdraw" -> {
                if (p.length != 4) { usage(c); return; }
                r = BotStorageDriver.withdraw(bot, Integer.parseInt(p[3]));
            }
            case "depositmesos" -> {
                if (p.length != 4) { usage(c); return; }
                r = BotStorageDriver.depositMesos(bot, Integer.parseInt(p[3]));
            }
            case "withdrawmesos" -> {
                if (p.length != 4) { usage(c); return; }
                r = BotStorageDriver.withdrawMesos(bot, Integer.parseInt(p[3]));
            }
            default -> { usage(c); return; }
        }
        c.getPlayer().yellowMessage("QA storage: " + r.reason() + " success=" + r.success()
                + " open=" + r.open() + " items=" + r.itemCount() + "/" + r.slots()
                + " storageMesos=" + r.storageMesos() + " playerMesos=" + r.playerMesos()
                + " item=" + r.itemId() + " amount=" + r.amount() + ".");
    }

    private static void quest(Client c, String[] p) {
        if (p.length != 4 && p.length != 5) { usage(c); return; }
        Character bot = bot(c, Integer.parseInt(p[2]));
        if (bot == null) return;
        int questId = Integer.parseInt(p[3]);
        BotQuestDriver.QuestResult r;
        switch (p[1].toLowerCase()) {
            case "status" -> r = BotQuestDriver.status(bot, questId);
            case "start" -> r = p.length == 5
                    ? BotQuestDriver.start(bot, questId, Integer.parseInt(p[4]))
                    : BotQuestDriver.start(bot, questId);
            case "complete" -> r = p.length == 5
                    ? BotQuestDriver.complete(bot, questId, Integer.parseInt(p[4]))
                    : BotQuestDriver.complete(bot, questId);
            case "forfeit" -> r = BotQuestDriver.forfeit(bot, questId);
            default -> { usage(c); return; }
        }
        c.getPlayer().yellowMessage("QA quest " + questId + ": " + r.reason() + " success=" + r.success()
                + " status=" + r.status() + " startNpc=" + r.startNpcId() + " endNpc=" + r.completeNpcId()
                + " completable=" + r.completable() + " mobs=" + r.relevantMobs() + ".");
    }

    private static void boss(Client c, String[] p) {
        if (p.length != 3) { usage(c); return; }
        Character bot = bot(c, Integer.parseInt(p[2]));
        if (bot == null) return;
        BotBossDriver.BossResult r = switch (p[1].toLowerCase()) {
            case "start" -> BotBossDriver.start(bot);
            case "stop" -> BotBossDriver.stop(bot);
            case "status" -> BotBossDriver.status(bot);
            default -> null;
        };
        if (r == null) { usage(c); return; }
        c.getPlayer().yellowMessage("QA boss: " + r.reason() + " success=" + r.success() + " phase=" + r.phase()
                + " mob=" + r.bossMobId() + " map=" + r.bossMapId() + " hp=" + r.bossHp()
                + " attacks=" + r.attacks() + " hits=" + r.hits() + " deaths=" + r.deaths()
                + " reentries=" + r.reentries() + ".");
    }

    private static void pq(Client c, String[] p) {
        if (p.length < 3 || p.length > 4) { usage(c); return; }
        Character bot = bot(c, Integer.parseInt(p[2]));
        if (bot == null) return;
        BotPqDriver.PqResult r;
        switch (p[1].toLowerCase()) {
            case "start" -> {
                if (p.length != 4) { usage(c); return; }
                r = BotPqDriver.start(bot, Integer.parseInt(p[3]));
            }
            case "stop" -> r = BotPqDriver.stop(bot);
            case "status" -> r = BotPqDriver.status(bot);
            default -> { usage(c); return; }
        }
        c.getPlayer().yellowMessage("QA PQ: " + r.reason() + " success=" + r.success() + " phase=" + r.phase()
                + " event=" + r.eventName() + " bots=" + r.participants() + " eventPlayers=" + r.eventPlayers()
                + " maps=" + r.mapChanges() + " attacks=" + r.attacks() + " hits=" + r.combatHits()
                + " reactors=" + r.reactorHits() + " npcs=" + r.npcActions() + " portals=" + r.portalUses()
                + " deaths=" + r.deaths() + ".");
    }

    private static void soak(Client c, String[] p) {
        if (p.length < 2 || p.length > 4) { usage(c); return; }
        int owner = c.getPlayer().getId();
        BotQaSoakRunner.SoakResult r;
        switch (p[1].toLowerCase()) {
            case "start" -> {
                if (p.length != 4) { usage(c); return; }
                if (BotQaSuiteRunner.isRunning(owner)) {
                    c.getPlayer().yellowMessage("A full QA suite owns this fleet; stop the suite before starting a separate soak.");
                    return;
                }
                r = BotQaSoakRunner.start(owner, Integer.parseInt(p[2]), p[3]);
            }
            case "stop" -> r = BotQaSoakRunner.stop(owner);
            case "status" -> r = BotQaSoakRunner.status(owner);
            default -> { usage(c); return; }
        }
        c.getPlayer().yellowMessage("QA soak: " + r.reason() + " success=" + r.success() + " phase=" + r.phase()
                + " bots=" + r.bots() + " alive=" + r.alive() + " logged=" + r.loggedInWorld()
                + " hunting=" + r.hunting() + " traveling=" + r.traveling() + " maxTraveling=" + r.maxTraveling()
                + " deaths=" + r.deaths() + " recoveries=" + r.recoveries()
                + " invariantFailures=" + r.invariantFailures() + " exceptions=" + r.exceptions()
                + " elapsed=" + r.elapsedMs() + "/" + r.durationMs() + "ms levelGain=" + r.levelGain()
                + " mesoDelta=" + r.mesoDelta() + " heapDelta=" + r.heapDeltaBytes()
                + " threadDelta=" + r.threadDelta() + " factoryBots=" + r.globalFactoryBots()
                + " clients=" + r.headlessClients() + " storages=" + r.activeQaStorages() + ".");
    }

    private static void suite(Client c, String[] p) {
        int owner = c.getPlayer().getId();
        BotQaSuiteRunner.SuiteResult r;
        if (p.length == 2 && "ARM".equalsIgnoreCase(p[1])) {
            r = BotQaSuiteRunner.start(owner, owner, c.getPlayer().getMapId(), 3, p[1]);
        } else if (p.length >= 2 && "start".equalsIgnoreCase(p[1])) {
            if (p.length == 3) {
                r = BotQaSuiteRunner.start(owner, owner, c.getPlayer().getMapId(), 3, p[2]);
            } else if (p.length == 4) {
                r = BotQaSuiteRunner.start(owner, owner, c.getPlayer().getMapId(), Integer.parseInt(p[2]), p[3]);
            } else {
                usage(c);
                return;
            }
        } else if (p.length == 2 && "status".equalsIgnoreCase(p[1])) {
            r = BotQaSuiteRunner.status(owner);
        } else if (p.length == 2 && "stop".equalsIgnoreCase(p[1])) {
            r = BotQaSuiteRunner.stop(owner);
        } else {
            usage(c);
            return;
        }
        c.getPlayer().yellowMessage("QA suite: " + r.reason() + " success=" + r.success() + " phase=" + r.phase()
                + " passed=" + r.passed() + " failed=" + r.failed() + " skipped=" + r.skipped()
                + " elapsed=" + r.elapsedMs() + "ms stages=" + r.stageSummary() + ".");
    }

    private static Character bot(Client c, int oneBasedIndex) {
        List<Character> bots = BotQaFleet.bots(c.getPlayer().getId());
        if (bots.isEmpty()) {
            c.getPlayer().yellowMessage("Create a QA fleet first: !qabotops fleet spawn <1-12>.");
            return null;
        }
        if (oneBasedIndex < 1 || oneBasedIndex > bots.size()) {
            c.getPlayer().yellowMessage("Bot index must be 1-" + bots.size() + ".");
            return null;
        }
        return bots.get(oneBasedIndex - 1);
    }

    private static List<Character> fleetBots(Client c) {
        List<Character> bots = BotQaFleet.bots(c.getPlayer().getId());
        if (bots.isEmpty()) {
            c.getPlayer().yellowMessage("Create a QA fleet first: !qabotops fleet spawn <1-12>.");
            return null;
        }
        return bots;
    }

    private static InventoryType inventoryType(String value) {
        InventoryType type = InventoryType.getByType(Byte.parseByte(value));
        return type == null || type == InventoryType.UNDEFINED || type == InventoryType.EQUIPPED ? null : type;
    }

    private static void reportFleet(Client c, BotQaFleet.FleetResult r) {
        c.getPlayer().yellowMessage("QA fleet: " + r.reason() + " success=" + r.success() + " bots=" + r.bots()
                + " alive=" + r.alive() + " logged=" + r.loggedInWorld() + " autonomous=" + r.autonomous()
                + " world=" + r.worldId() + " channel=" + r.channelId() + " map=" + r.mapId()
                + " factoryBots=" + r.globalFactoryBots() + " clients=" + r.headlessClients() + ".");
    }

    private static boolean onQaChannel(Client c) {
        return c.getChannelServer() != null
                && c.getChannelServer().getWorld() == QA_WORLD
                && c.getChannelServer().getId() == QA_CHANNEL;
    }

    private static boolean isCleanup(String[] p) {
        if (p.length < 2) return false;
        String action = p[0].toLowerCase();
        String mode = p[1].toLowerCase();
        return switch (action) {
            case "fleet" -> mode.equals("remove") || mode.equals("clear");
            case "huntall", "boss", "pq", "soak", "suite" -> mode.equals("stop");
            case "trade" -> mode.equals("cancel");
            case "storage" -> mode.equals("close");
            case "party" -> mode.equals("leave");
            default -> false;
        };
    }

    private static void usage(Client c) {
        c.getPlayer().yellowMessage("Usage: !qabotops fleet spawn <1-12>|status|remove; travel <bot#> <mapId> [x y]; die <bot#>; huntall start|stop; party create|leave|status <bot#>|join|leader <bot#> <bot#>; trade open <bot#> <bot#>|mesos <bot#> <amount>|item <bot#> <invType> <slot> <qty>|confirm <bot#> <bot#>|cancel <bot#>; storage open <bot#> <npcId>|close|status <bot#>|deposit <bot#> <invType> <slot> <qty>|withdraw <bot#> <index>|depositmesos|withdrawmesos <bot#> <amount>; quest start|complete|status|forfeit <bot#> <questId> [npcId]; boss start|stop|status <bot#>; pq start <bot#> <entryNpcId>|stop|status <bot#>; soak start <minutes> ARM|status|stop; suite ARM|start [2-12] ARM|status|stop");
    }
}

package soloMapling.ArtificialPlayer;

import client.Character;
import client.inventory.InventoryType;
import client.inventory.Item;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import server.TimerManager;
import soloMapling.ArtificialPlayer.GCMoveSystem.GCMovement;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ScheduledFuture;

/**
 * One-command, explicitly armed Batch 1-7 server-runtime QA suite.
 *
 * <p>The suite uses only bounded synthetic players. It never enables ambient SoloMapling population,
 * never starts at bootstrap, cleans up its fleet on every terminal path, and marks content-specific
 * boss/PQ semantic scenarios as skipped rather than fabricating encounter completion.</p>
 */
public final class BotQaSuiteRunner {
    private static final Logger log = LoggerFactory.getLogger(BotQaSuiteRunner.class);
    private static final String ARM_TOKEN = "ARM";
    private static final long TICK_MS = 500L;
    private static final long TRAVEL_TIMEOUT_MS = 120_000L;
    private static final long HUNT_OBSERVE_MS = 15_000L;
    private static final long DEATH_RECOVERY_TIMEOUT_MS = 60_000L;

    private static final int HENESYS_PARK = 100000200;
    private static final int HENESYS_STORAGE_NPC = 1012009;
    private static final int HENESYS_STORAGE_X = 1039;
    private static final int HENESYS_STORAGE_Y = 84;
    private static final int HENESYS_DEPARTMENT_STORE = 100000102;
    private static final int HENESYS_SHOP_NPC = 1011100;
    private static final int HENESYS_SHOP_X = -258;
    private static final int HENESYS_SHOP_Y = 84;
    private static final int HENESYS_HUNTING_GROUND_1 = 104040000;
    private static final int RED_POTION = 2000000;
    private static final int QUEST_STATUS_SMOKE = 1046;

    private static final Map<Integer, Run> runsByOwner = new ConcurrentHashMap<>();
    private static final Map<Integer, SuiteResult> lastResultsByOwner = new ConcurrentHashMap<>();

    private BotQaSuiteRunner() {}

    public static SuiteResult start(int ownerId, int templateCharacterId, int startMapId, int count) {
        return SuiteResult.fail("explicit-arm-token-required");
    }

    public static synchronized SuiteResult start(int ownerId, int templateCharacterId, int startMapId,
                                                 int count, String armToken) {
        if (armToken == null || !ARM_TOKEN.equalsIgnoreCase(armToken)) return SuiteResult.fail("explicit-arm-token-required");
        if (ownerId <= 0 || templateCharacterId <= 0) return SuiteResult.fail("invalid-owner-or-template");
        if (count < 2 || count > BotQaFleet.MAX_BOTS_PER_FLEET) return SuiteResult.fail("count-must-be-2-to-12");
        if (runsByOwner.containsKey(ownerId)) return SuiteResult.fail("suite-already-running");

        BotQaSoakRunner.stop(ownerId);
        BotQaFleet.remove(ownerId);
        lastResultsByOwner.remove(ownerId);

        int baselineFactoryBots = BareBotFactory.activeBotCount();
        int baselineClients = BotClientHandler.activeClientCount();
        BotQaFleet.FleetResult fleet = BotQaFleet.spawn(ownerId, templateCharacterId, count, 0, 1, startMapId);
        if (!fleet.success()) return SuiteResult.fail("fleet-spawn-failed:" + fleet.reason());

        Run run = new Run(ownerId, baselineFactoryBots, baselineClients, BotQaFleet.bots(ownerId));
        run.task = TimerManager.getInstance().register(run, TICK_MS, TICK_MS);
        runsByOwner.put(ownerId, run);
        return run.snapshot("started");
    }

    public static synchronized SuiteResult stop(int ownerId) {
        Run run = runsByOwner.get(ownerId);
        if (run == null) return SuiteResult.fail("no-suite-run");
        run.stop("stopped-by-gm");
        return lastResultsByOwner.getOrDefault(ownerId, run.snapshot("stopped-by-gm"));
    }

    public static SuiteResult status(int ownerId) {
        Run run = runsByOwner.get(ownerId);
        if (run != null) return run.snapshot("status");
        return lastResultsByOwner.getOrDefault(ownerId, SuiteResult.fail("no-suite-run"));
    }

    public static boolean isRunning(int ownerId) {
        return runsByOwner.containsKey(ownerId);
    }

    private enum Stage {
        PARTY,
        TRADE,
        TRADE_CANCEL,
        STORAGE_TRAVEL,
        STORAGE,
        SHOP_TRAVEL,
        SHOP,
        HUNT_TRAVEL,
        HUNT_OBSERVE,
        DEATH_RECOVERY,
        CONTENT_CONTRACTS,
        SOAK,
        CLEANUP,
        COMPLETE,
        FAILED,
        STOPPED
    }

    private static final class Run implements Runnable {
        private final int ownerId;
        private final int baselineFactoryBots;
        private final int baselineClients;
        private final List<Character> bots;
        private final long startedAt = System.currentTimeMillis();
        private final List<StageResult> results = new ArrayList<>();
        private volatile ScheduledFuture<?> task;
        private volatile Stage stage = Stage.PARTY;
        private volatile long stageStartedAt = System.currentTimeMillis();
        private volatile String terminalReason = "";
        private int passed;
        private int failed;
        private int skipped;
        private long huntBaselineExp;
        private int deathBotId = -1;

        private Run(int ownerId, int baselineFactoryBots, int baselineClients, List<Character> bots) {
            this.ownerId = ownerId;
            this.baselineFactoryBots = baselineFactoryBots;
            this.baselineClients = baselineClients;
            this.bots = List.copyOf(bots);
        }

        @Override
        public void run() {
            try {
                tick();
            } catch (Throwable t) {
                failSuite("suite-exception:" + t.getClass().getSimpleName());
                log.error("SoloMapling QA suite failed owner={} stage={}", ownerId, stage, t);
            }
        }

        private void tick() {
            switch (stage) {
                case PARTY -> testParty();
                case TRADE -> testTrade();
                case TRADE_CANCEL -> testTradeCancel();
                case STORAGE_TRAVEL -> waitForStorageTravel();
                case STORAGE -> testStorage();
                case SHOP_TRAVEL -> waitForShopTravel();
                case SHOP -> testShop();
                case HUNT_TRAVEL -> waitForHuntTravel();
                case HUNT_OBSERVE -> observeHunt();
                case DEATH_RECOVERY -> observeDeathRecovery();
                case CONTENT_CONTRACTS -> testContentContracts();
                case SOAK -> observeSoak();
                case CLEANUP -> cleanupAndComplete();
                case COMPLETE, FAILED, STOPPED -> { }
            }
        }

        private void testParty() {
            Character a = bots.get(0);
            Character b = bots.get(1);
            BotPartyDriver.PartyResult create = BotPartyDriver.create(a);
            BotPartyDriver.PartyResult join = create.success() ? BotPartyDriver.join(b, a) : create;
            BotPartyDriver.PartyResult status = join.success() ? BotPartyDriver.status(a) : join;
            boolean ok = create.success() && join.success() && status.success() && status.members() >= 2;
            try { BotPartyDriver.leave(b); } catch (RuntimeException ignored) { }
            try { BotPartyDriver.leave(a); } catch (RuntimeException ignored) { }
            if (!ok) { failStage("party", "create=" + create.reason() + ";join=" + join.reason()); return; }
            pass("party", "create/join/status/leave");
            advance(Stage.TRADE);
        }

        private void testTrade() {
            Character a = bots.get(0);
            Character b = bots.get(1);
            BotQaLedger.Snapshot pairBefore = BotQaLedger.capture(a, b);
            int aBefore = a.getMeso();
            int bBefore = b.getMeso();
            BotTradeDriver.TradeResult open = BotTradeDriver.open(a, b);
            BotTradeDriver.TradeResult offer = open.success() ? BotTradeDriver.offerMesos(a, 1_000) : open;
            BotTradeDriver.TradeResult confirm = offer.success() ? BotTradeDriver.confirmBoth(a, b) : offer;
            BotQaLedger.Snapshot pairAfter = BotQaLedger.capture(a, b);
            BotQaLedger.Conservation conservation = BotQaLedger.compare(pairBefore, pairAfter);
            boolean exact = a.getMeso() == aBefore - 1_000 && b.getMeso() == bBefore + 1_000;
            if (!open.success() || !offer.success() || !confirm.success() || !conservation.fullyConserved() || !exact) {
                try { BotTradeDriver.cancel(a); } catch (RuntimeException ignored) { }
                try { BotTradeDriver.cancel(b); } catch (RuntimeException ignored) { }
                failStage("trade", "open=" + open.reason() + ";offer=" + offer.reason()
                        + ";confirm=" + confirm.reason() + ";ledger=" + conservation.reason());
                return;
            }
            pass("trade", "1000-meso exact conservation");
            advance(Stage.TRADE_CANCEL);
        }

        private void testTradeCancel() {
            Character a = bots.get(0);
            Character b = bots.get(1);
            Item potion = a.getInventory(InventoryType.USE).findById(RED_POTION);
            if (potion == null) { failStage("trade-cancel", "red-potion-missing"); return; }
            BotQaLedger.Snapshot before = BotQaLedger.capture(a, b);
            BotTradeDriver.TradeResult open = BotTradeDriver.open(a, b);
            BotTradeDriver.TradeResult offer = open.success()
                    ? BotTradeDriver.offerItem(a, InventoryType.USE, potion.getPosition(), (short) 1) : open;
            BotTradeDriver.TradeResult cancel = offer.success() ? BotTradeDriver.cancel(a) : offer;
            BotQaLedger.Conservation conservation = BotQaLedger.compare(before, BotQaLedger.capture(a, b));
            try { BotTradeDriver.cancel(b); } catch (RuntimeException ignored) { }
            if (!open.success() || !offer.success() || !cancel.success() || !conservation.fullyConserved()) {
                failStage("trade-cancel", "open=" + open.reason() + ";offer=" + offer.reason()
                        + ";cancel=" + cancel.reason() + ";ledger=" + conservation.reason());
                return;
            }
            pass("trade-cancel", "offered item restored exactly");
            Character bot = bots.get(0);
            GCMovement.travelTo(bot, HENESYS_PARK, HENESYS_STORAGE_X, HENESYS_STORAGE_Y,
                    ok -> { if (!ok && stage == Stage.STORAGE_TRAVEL) failSuite("storage-travel-callback-failed"); });
            advance(Stage.STORAGE_TRAVEL);
        }

        private void waitForStorageTravel() {
            Character bot = bots.get(0);
            if (bot.getMapId() == HENESYS_PARK && near(bot, HENESYS_STORAGE_X, HENESYS_STORAGE_Y, 260)) {
                pass("cross-map-storage-travel", "arrived=" + HENESYS_PARK);
                advance(Stage.STORAGE);
            } else if (stageElapsed() > TRAVEL_TIMEOUT_MS) {
                failStage("cross-map-storage-travel", "timeout map=" + bot.getMapId());
            }
        }

        private void testStorage() {
            Character bot = bots.get(0);
            Item potion = bot.getInventory(InventoryType.USE).findById(RED_POTION);
            if (potion == null) { failStage("storage", "red-potion-missing"); return; }
            BotQaLedger.Snapshot before = BotQaLedger.capture(bot);
            BotStorageDriver.StorageResult open = BotStorageDriver.open(bot, HENESYS_STORAGE_NPC);
            BotStorageDriver.StorageResult deposit = open.success()
                    ? BotStorageDriver.deposit(bot, InventoryType.USE, potion.getPosition(), (short) 1) : open;
            BotStorageDriver.StorageResult withdraw = deposit.success()
                    ? BotStorageDriver.withdraw(bot, 0) : deposit;
            BotStorageDriver.StorageResult mesoIn = withdraw.success()
                    ? BotStorageDriver.depositMesos(bot, 1_000) : withdraw;
            BotStorageDriver.StorageResult mesoOut = mesoIn.success()
                    ? BotStorageDriver.withdrawMesos(bot, 1_000) : mesoIn;
            BotStorageDriver.StorageResult close = BotStorageDriver.close(bot);
            BotQaLedger.Snapshot after = BotQaLedger.capture(bot);
            boolean noDupe = BotQaLedger.noItemCreation(before, after)
                    && BotQaLedger.quantity(before, RED_POTION) == BotQaLedger.quantity(after, RED_POTION)
                    && BotQaLedger.noMesoCreation(before, after);
            if (!open.success() || !deposit.success() || !withdraw.success() || !mesoIn.success()
                    || !mesoOut.success() || !close.success() || !noDupe) {
                failStage("storage", "open=" + open.reason() + ";deposit=" + deposit.reason()
                        + ";withdraw=" + withdraw.reason() + ";mesoIn=" + mesoIn.reason()
                        + ";mesoOut=" + mesoOut.reason() + ";noDupe=" + noDupe);
                return;
            }
            pass("storage", "transient trunk item/meso round-trip no creation");
            GCMovement.travelTo(bot, HENESYS_DEPARTMENT_STORE, HENESYS_SHOP_X, HENESYS_SHOP_Y,
                    ok -> { if (!ok && stage == Stage.SHOP_TRAVEL) failSuite("shop-travel-callback-failed"); });
            advance(Stage.SHOP_TRAVEL);
        }

        private void waitForShopTravel() {
            Character bot = bots.get(0);
            if (bot.getMapId() == HENESYS_DEPARTMENT_STORE && near(bot, HENESYS_SHOP_X, HENESYS_SHOP_Y, 240)) {
                pass("cross-map-shop-travel", "arrived=" + HENESYS_DEPARTMENT_STORE);
                advance(Stage.SHOP);
            } else if (stageElapsed() > TRAVEL_TIMEOUT_MS) {
                failStage("cross-map-shop-travel", "timeout map=" + bot.getMapId());
            }
        }

        private void testShop() {
            Character bot = bots.get(0);
            int before = bot.getInventory(InventoryType.USE).countById(RED_POTION);
            BotShopDriver.ShopResult opened = BotShopDriver.open(bot, HENESYS_SHOP_NPC);
            BotShopDriver.ShopResult bought = opened.success()
                    ? BotShopDriver.buy(bot, HENESYS_SHOP_NPC, RED_POTION, (short) 1) : opened;
            int after = bot.getInventory(InventoryType.USE).countById(RED_POTION);
            if (!opened.success() || !bought.success() || after <= before) {
                failStage("npc-shop", "open=" + opened.reason() + ";buy=" + bought.reason()
                        + ";red=" + before + "->" + after);
                return;
            }
            pass("npc-shop", "real shop open/buy inventory+meso path");
            for (Character qa : bots) {
                GCMovement.travel(qa, HENESYS_HUNTING_GROUND_1,
                        ok -> { if (!ok && stage == Stage.HUNT_TRAVEL) failSuite("hunt-travel-callback-failed"); });
            }
            advance(Stage.HUNT_TRAVEL);
        }

        private void waitForHuntTravel() {
            boolean allThere = true;
            for (Character bot : bots) {
                if (bot.getMapId() != HENESYS_HUNTING_GROUND_1) { allThere = false; break; }
            }
            if (allThere) {
                pass("multi-bot-cross-map-travel", "all-arrived=" + HENESYS_HUNTING_GROUND_1);
                huntBaselineExp = expSum(bots);
                int started = 0;
                for (Character bot : bots) if (BareBotHunter.start(bot)) started++;
                if (started != bots.size()) { failStage("hunt", "hunters-started=" + started + "/" + bots.size()); return; }
                advance(Stage.HUNT_OBSERVE);
            } else if (stageElapsed() > TRAVEL_TIMEOUT_MS) {
                failStage("multi-bot-cross-map-travel", "timeout");
            }
        }

        private void observeHunt() {
            for (Character bot : bots) {
                String failure = BareBotHunter.failureReason(bot);
                if (failure != null) { failStage("hunt", "bot=" + bot.getId() + ";" + failure); return; }
            }
            if (stageElapsed() < HUNT_OBSERVE_MS) return;
            long expAfter = expSum(bots);
            boolean allHunting = bots.stream().allMatch(BareBotHunter::isHunting);
            if (!allHunting || expAfter <= huntBaselineExp) {
                failStage("hunt", "allHunting=" + allHunting + ";exp=" + huntBaselineExp + "->" + expAfter);
                return;
            }
            pass("hunt-combat-loot", "server-authoritative hunt gainedExp=" + (expAfter - huntBaselineExp));
            Character victim = bots.get(0);
            deathBotId = victim.getId();
            victim.updateHp(0);
            advance(Stage.DEATH_RECOVERY);
        }

        private void observeDeathRecovery() {
            Character bot = bots.get(0);
            String failure = BareBotHunter.failureReason(bot);
            if (failure != null) { failStage("death-recovery", failure); return; }
            if (bot.getId() == deathBotId && bot.isAlive() && BareBotHunter.isHunting(bot)
                    && bot.getMapId() == HENESYS_HUNTING_GROUND_1 && stageElapsed() > 1_000L) {
                pass("death-recovery", "respawned-returned-resumed");
                advance(Stage.CONTENT_CONTRACTS);
            } else if (stageElapsed() > DEATH_RECOVERY_TIMEOUT_MS) {
                failStage("death-recovery", "timeout map=" + bot.getMapId() + ";alive=" + bot.isAlive()
                        + ";hunting=" + BareBotHunter.isHunting(bot));
            }
        }

        private void testContentContracts() {
            Character bot = bots.get(0);
            BotQuestDriver.QuestResult quest = BotQuestDriver.status(bot, QUEST_STATUS_SMOKE);
            if (!quest.success()) { failStage("quest-driver", quest.reason()); return; }
            pass("quest-driver", "real quest status id=" + QUEST_STATUS_SMOKE + " status=" + quest.status());

            // Boss/PQ drivers intentionally require a real encounter already present / a real configured entry NPC.
            // The suite must not spawn rewards or fake stage completion simply to turn these checks green.
            skip("boss-semantic", "requires real boss encounter context; driver remains fail-closed");
            skip("pq-semantic", "requires real PQ entry/event context; no fake stage completion");

            BotQaSoakRunner.SoakResult soak = BotQaSoakRunner.start(ownerId, 1, ARM_TOKEN);
            if (!soak.success()) { failStage("soak", soak.reason()); return; }
            advance(Stage.SOAK);
        }

        private void observeSoak() {
            BotQaSoakRunner.SoakResult soak = BotQaSoakRunner.status(ownerId);
            if ("failed".equals(soak.phase())) { failStage("soak", soak.reason()); return; }
            if ("complete".equals(soak.phase())) {
                pass("soak", "1-minute bounded soak invariants=" + soak.invariantFailures()
                        + ";exceptions=" + soak.exceptions() + ";heapDelta=" + soak.heapDeltaBytes());
                advance(Stage.CLEANUP);
            }
        }

        private void cleanupAndComplete() {
            BotQaSoakRunner.stop(ownerId);
            BotQaFleet.FleetResult removed = BotQaFleet.remove(ownerId);
            boolean clean = BareBotFactory.activeBotCount() == baselineFactoryBots
                    && BotClientHandler.activeClientCount() == baselineClients
                    && BotStorageDriver.activeQaStorageCount() == 0;
            if (!removed.success() || !clean) {
                failStage("cleanup", "remove=" + removed.reason() + ";factory=" + BareBotFactory.activeBotCount()
                        + "/" + baselineFactoryBots + ";clients=" + BotClientHandler.activeClientCount()
                        + "/" + baselineClients + ";storages=" + BotStorageDriver.activeQaStorageCount());
                return;
            }
            pass("cleanup", "synthetic runtime returned to baseline");
            stage = Stage.COMPLETE;
            terminalReason = "suite-complete";
            finish(false);
        }

        private void pass(String name, String detail) {
            results.add(new StageResult(name, "PASS", detail, stageElapsed()));
            passed++;
        }

        private void skip(String name, String detail) {
            results.add(new StageResult(name, "SKIP", detail, stageElapsed()));
            skipped++;
        }

        private void failStage(String name, String detail) {
            results.add(new StageResult(name, "FAIL", detail, stageElapsed()));
            failed++;
            failSuite(name + ":" + detail);
        }

        private void failSuite(String reason) {
            if (stage == Stage.COMPLETE || stage == Stage.FAILED || stage == Stage.STOPPED) return;
            stage = Stage.FAILED;
            terminalReason = reason;
            finish(true);
        }

        private void stop(String reason) {
            if (stage == Stage.COMPLETE || stage == Stage.FAILED || stage == Stage.STOPPED) return;
            stage = Stage.STOPPED;
            terminalReason = reason;
            finish(true);
        }

        private void finish(boolean cleanupFleet) {
            ScheduledFuture<?> current = task;
            if (current != null) current.cancel(false);
            if (cleanupFleet) {
                try { BotQaSoakRunner.stop(ownerId); } catch (RuntimeException ignored) { }
                try { BotQaFleet.remove(ownerId); } catch (RuntimeException ignored) { }
            }
            SuiteResult terminal = snapshot(terminalReason);
            runsByOwner.remove(ownerId, this);
            lastResultsByOwner.put(ownerId, terminal);

            Map<String, Object> report = new LinkedHashMap<>();
            report.put("ownerId", ownerId);
            report.put("phase", terminal.phase());
            report.put("success", terminal.success());
            report.put("passed", terminal.passed());
            report.put("failed", terminal.failed());
            report.put("skipped", terminal.skipped());
            report.put("elapsedMs", terminal.elapsedMs());
            report.put("reason", terminal.reason());
            report.put("stages", terminal.stageSummary());
            BotQaReport.emit("suite", report);
        }

        private SuiteResult snapshot(String reason) {
            String detail = terminalReason.isEmpty() ? reason : terminalReason;
            return new SuiteResult(stage != Stage.FAILED, stage.name().toLowerCase(), passed, failed, skipped,
                    System.currentTimeMillis() - startedAt, detail, stageSummary());
        }

        private String stageSummary() {
            StringBuilder out = new StringBuilder();
            for (StageResult result : results) {
                if (out.length() > 0) out.append('|');
                out.append(result.name()).append('=').append(result.outcome());
            }
            return out.toString();
        }

        private void advance(Stage next) {
            stage = next;
            stageStartedAt = System.currentTimeMillis();
        }

        private long stageElapsed() {
            return System.currentTimeMillis() - stageStartedAt;
        }
    }

    private static boolean near(Character bot, int x, int y, int radius) {
        if (bot == null || bot.getPosition() == null) return false;
        long dx = (long) bot.getPosition().x - x;
        long dy = (long) bot.getPosition().y - y;
        return dx * dx + dy * dy <= (long) radius * radius;
    }

    private static long expSum(List<Character> bots) {
        long total = 0L;
        for (Character bot : bots) if (bot != null) total += bot.getExp();
        return total;
    }

    private record StageResult(String name, String outcome, String detail, long elapsedMs) {}

    public record SuiteResult(boolean success, String phase, int passed, int failed, int skipped,
                              long elapsedMs, String reason, String stageSummary) {
        static SuiteResult fail(String reason) {
            return new SuiteResult(false, "stopped", 0, 0, 0, 0L, reason, "");
        }
    }
}

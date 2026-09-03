package soloMapling.ArtificialPlayer;

import client.Character;
import net.server.Server;
import net.server.channel.Channel;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import server.TimerManager;
import server.life.LifeFactory;
import server.life.Monster;
import server.maps.Foothold;
import server.maps.MapleMap;
import server.maps.Portal;
import soloMapling.ArtificialPlayer.BotAttackSystem.BotAttackDriver;
import soloMapling.ArtificialPlayer.GCMoveSystem.GCMovement;
import soloMapling.ArtificialPlayer.GCMoveSystem.GCMovementDiagnostics;
import tools.DatabaseConnection;

import java.awt.Point;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.util.concurrent.atomic.AtomicBoolean;

/**
 * Explicitly gated runtime smoke for the disposable EverLeaf QA Docker stack.
 *
 * <p>This class is inert in every normal server start. It requires both the exact
 * staging arming token and the Docker-only qa-db hostname before it will create
 * a single synthetic bot. It never enables SoloMapling's automatic population.</p>
 */
public final class DisposableQaSmokeRunner {
    private static final Logger log = LoggerFactory.getLogger(DisposableQaSmokeRunner.class);
    private static final String ARM_ENV = "EVERLEAF_SOLOMAPLING_SMOKE";
    private static final String ARM_TOKEN = "I_UNDERSTAND_DISPOSABLE_QA_ONLY";
    private static final String QA_DB_HOST = "qa-db";
    private static final int COMBAT_SMOKE_MONSTER_ID = 100100; // Snail: harmless disposable QA target.
    private static final AtomicBoolean started = new AtomicBoolean(false);

    private DisposableQaSmokeRunner() {
    }

    public static void startIfRequested() {
        if (!ARM_TOKEN.equals(System.getenv(ARM_ENV))) {
            return;
        }
        if (!QA_DB_HOST.equals(System.getenv("EVERLEAF_DB_HOST"))) {
            log.error("SOLOMAPLING_QA_SMOKE_RESULT FAIL safety=db-host host={}", System.getenv("EVERLEAF_DB_HOST"));
            return;
        }
        if (!started.compareAndSet(false, true)) {
            return;
        }

        log.info("SOLOMAPLING_QA_SMOKE armed against disposable qa-db only");
        TimerManager.getInstance().schedule(DisposableQaSmokeRunner::runSmoke, 2_000L);
    }

    private static void runSmoke() {
        Character bot = null;
        try {
            Template template = findQaTemplate();
            Channel channel = Server.getInstance().getChannel(0, 1);
            if (channel == null) {
                throw new IllegalStateException("world 0 channel 1 unavailable");
            }

            MapleMap map = channel.getMapFactory().getMap(template.mapId());
            if (map == null) {
                throw new IllegalStateException("template map unavailable: " + template.mapId());
            }

            Portal portal = map.getPortal(template.spawnPoint());
            if (portal == null) {
                portal = map.getPortal(0);
            }
            if (portal == null) {
                throw new IllegalStateException("template map has no usable spawn portal");
            }

            Point portalPos = portal.getPosition();
            Foothold foothold = map.getFootholds().findBelow(new Point(portalPos.x, portalPos.y - 1));
            if (foothold == null) {
                foothold = map.getFootholds().findBelow(portalPos);
            }
            if (foothold == null) {
                throw new IllegalStateException("no foothold below template spawn " + portalPos);
            }

            Point start = pointOnFoothold(foothold, clamp(portalPos.x, Math.min(foothold.getX1(), foothold.getX2()), Math.max(foothold.getX1(), foothold.getX2())));
            Point target = chooseTarget(foothold, start);
            if (start.distance(target) < 25.0) {
                throw new IllegalStateException("spawn foothold too short for movement smoke");
            }

            bot = BareBotFactory.createBareBot(template.characterId(), start, map);
            Character smokeBot = bot;
            Point initial = new Point(bot.getPosition());
            log.info("SOLOMAPLING_QA_SMOKE_START template={} map={} start={} target={}",
                    template.characterId(), map.getId(), point(initial), point(target));

            GCMovement.move(bot, target.x, target.y);
            TimerManager.getInstance().schedule(
                    () -> log.info("SOLOMAPLING_QA_SMOKE_DIAG t=2s {}", GCMovementDiagnostics.describe(smokeBot)),
                    2_000L);
            TimerManager.getInstance().schedule(
                    () -> log.info("SOLOMAPLING_QA_SMOKE_DIAG t=5s {}", GCMovementDiagnostics.describe(smokeBot)),
                    5_000L);
            TimerManager.getInstance().schedule(() -> finish(smokeBot, initial, target), 8_000L);
        } catch (Throwable t) {
            if (bot != null) {
                GCMovement.disable(bot);
                BotAttackDriver.clearBot(bot.getId());
                BareBotFactory.removeBareBot(bot);
            }
            log.error("SOLOMAPLING_QA_SMOKE_RESULT FAIL error={}", t.toString(), t);
        }
    }

    private static void finish(Character bot, Point initial, Point target) {
        Monster combatTarget = null;
        try {
            Point end = bot.getPosition() == null ? null : new Point(bot.getPosition());
            GCMovementDiagnostics.Snapshot snapshot = GCMovementDiagnostics.snapshot(bot);
            double moved = end == null ? 0.0 : initial.distance(end);
            double initialDistance = initial.distance(target);
            double finalDistance = end == null ? Double.POSITIVE_INFINITY : end.distance(target);
            boolean progressed = moved >= 20.0 && finalDistance < initialDistance;

            log.info("SOLOMAPLING_QA_SMOKE_FINAL {} moved={} initialDistance={} finalDistance={}",
                    GCMovementDiagnostics.describe(bot), Math.round(moved), Math.round(initialDistance), Math.round(finalDistance));

            if (!progressed) {
                log.error("SOLOMAPLING_QA_SMOKE_RESULT FAIL reason=no-progress map={} start={} end={} target={} mode={} stuckMs={} decision={} block={}",
                        bot.getMapId(), point(initial), point(end), point(target), snapshot.mode(), snapshot.stuckMs(),
                        snapshot.lastDecision(), snapshot.blockReason());
                return;
            }

            if (end == null || bot.getMap() == null) {
                log.error("SOLOMAPLING_QA_SMOKE_RESULT FAIL reason=combat-no-bot-position");
                return;
            }

            combatTarget = LifeFactory.getMonster(COMBAT_SMOKE_MONSTER_ID);
            if (combatTarget == null) {
                log.error("SOLOMAPLING_QA_SMOKE_RESULT FAIL reason=combat-monster-template-missing id={}", COMBAT_SMOKE_MONSTER_ID);
                return;
            }

            Point combatSpawn = new Point(end.x + 35, end.y);
            bot.getMap().spawnMonsterOnGroundBelow(combatTarget, combatSpawn);
            long hpBefore = combatTarget.getHp();
            BotAttackDriver.AttackResult attack = BotAttackDriver.forceSingle(bot);
            long hpAfter = combatTarget.getHp();
            boolean combatPassed = attack.hit() && (hpAfter < hpBefore || !combatTarget.isAlive());

            log.info("SOLOMAPLING_QA_SMOKE_COMBAT hit={} monster={} damage={} killed={} hpBefore={} hpAfter={} reason={}",
                    attack.hit(), attack.monsterName(), attack.damage(), attack.killed(), hpBefore, hpAfter, attack.reason());

            if (!combatPassed) {
                log.error("SOLOMAPLING_QA_SMOKE_RESULT FAIL reason=combat-no-damage hit={} hpBefore={} hpAfter={} attackReason={}",
                        attack.hit(), hpBefore, hpAfter, attack.reason());
                return;
            }

            log.info("SOLOMAPLING_QA_SMOKE_RESULT PASS map={} start={} end={} target={} combatHit=true combatDamage={}",
                    bot.getMapId(), point(initial), point(end), point(target), attack.damage());
        } catch (Throwable t) {
            log.error("SOLOMAPLING_QA_SMOKE_RESULT FAIL error={}", t.toString(), t);
        } finally {
            if (combatTarget != null && combatTarget.isAlive() && bot.getMap() != null) {
                bot.getMap().killMonster(combatTarget, null, false, 1, (short) 0);
            }
            GCMovement.disable(bot);
            BotAttackDriver.clearBot(bot.getId());
            BareBotFactory.removeBareBot(bot);
            log.info("SOLOMAPLING_QA_SMOKE_CLEANUP botRemoved=true gcMoveEnabled={}", GCMovement.isEnabled(bot));
        }
    }

    private static Template findQaTemplate() throws Exception {
        String explicit = System.getenv("EVERLEAF_SOLOMAPLING_TEMPLATE_CHARACTER_ID");
        if (explicit != null && !explicit.isBlank()) {
            int characterId = Integer.parseInt(explicit.trim());
            try (Connection con = DatabaseConnection.getConnection();
                 PreparedStatement ps = con.prepareStatement(
                         "SELECT c.id, c.map, c.spawnpoint FROM characters c " +
                                 "JOIN accounts a ON a.id=c.accountid WHERE c.id=? AND a.name LIKE 'qa\\_%' ESCAPE '\\\\' LIMIT 1")) {
                ps.setInt(1, characterId);
                try (ResultSet rs = ps.executeQuery()) {
                    if (rs.next()) {
                        return new Template(rs.getInt("id"), rs.getInt("map"), rs.getInt("spawnpoint"));
                    }
                }
            }
            throw new IllegalStateException("explicit template is not owned by a qa_ account: " + characterId);
        }

        try (Connection con = DatabaseConnection.getConnection();
             PreparedStatement ps = con.prepareStatement(
                     "SELECT c.id, c.map, c.spawnpoint FROM characters c " +
                             "JOIN accounts a ON a.id=c.accountid WHERE a.name LIKE 'qa\\_%' ESCAPE '\\\\' ORDER BY c.id LIMIT 1");
             ResultSet rs = ps.executeQuery()) {
            if (!rs.next()) {
                throw new IllegalStateException("disposable QA DB has no qa_ character template");
            }
            return new Template(rs.getInt("id"), rs.getInt("map"), rs.getInt("spawnpoint"));
        }
    }

    private static Point chooseTarget(Foothold foothold, Point start) {
        int minX = Math.min(foothold.getX1(), foothold.getX2());
        int maxX = Math.max(foothold.getX1(), foothold.getX2());
        int left = minX + Math.min(20, Math.max(0, (maxX - minX) / 4));
        int right = maxX - Math.min(20, Math.max(0, (maxX - minX) / 4));
        int targetX = Math.abs(start.x - left) > Math.abs(start.x - right) ? left : right;
        return pointOnFoothold(foothold, targetX);
    }

    private static Point pointOnFoothold(Foothold foothold, int x) {
        int x1 = foothold.getX1();
        int x2 = foothold.getX2();
        int clamped = clamp(x, Math.min(x1, x2), Math.max(x1, x2));
        if (x1 == x2) {
            return new Point(clamped, Math.min(foothold.getY1(), foothold.getY2()));
        }
        double ratio = (clamped - x1) / (double) (x2 - x1);
        int y = (int) Math.round(foothold.getY1() + (foothold.getY2() - foothold.getY1()) * ratio);
        return new Point(clamped, y);
    }

    private static int clamp(int value, int min, int max) {
        return Math.max(min, Math.min(max, value));
    }

    private static String point(Point point) {
        return point == null ? "-" : point.x + "," + point.y;
    }

    private record Template(int characterId, int mapId, int spawnPoint) {
    }
}

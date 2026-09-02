package client.command.commands.gm4;

import client.Character;
import client.Client;
import client.command.Command;
import soloMapling.ArtificialPlayer.BareBotAutopilot;
import soloMapling.ArtificialPlayer.BareBotCombat;
import soloMapling.ArtificialPlayer.BareBotFactory;
import soloMapling.ArtificialPlayer.BareBotMovement;
import soloMapling.ArtificialPlayer.BareBotPortal;
import soloMapling.ArtificialPlayer.GCMoveSystem.GCMovement;
import soloMapling.ArtificialPlayer.GCMoveSystem.GCMovementDiagnostics;
import tools.exceptions.EmptyMovementException;

import java.awt.Point;
import java.sql.SQLException;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/** GM-only control surface for the first isolated SoloMapling smoke bot. */
public class QaBotCommand extends Command {
    private static final int QA_WORLD = 0;
    private static final int QA_CHANNEL = 1;
    private static final Map<Integer, Character> spawnedByGm = new ConcurrentHashMap<>();

    {
        setDescription("Control one isolated SoloMapling QA bot: !qabot spawn|remove|status|nudge|move|gcmove|gcstop|strike|patrol|portal");
    }

    @Override
    public void execute(Client c, String[] params) {
        if (params.length < 1) {
            usage(c);
            return;
        }

        String action = params[0].toLowerCase();
        if (!action.equals("remove") && !onQaChannel(c)) {
            c.getPlayer().yellowMessage("SoloMapling QA smoke bots currently run only on world 0, channel 1.");
            return;
        }

        switch (action) {
            case "spawn" -> spawn(c);
            case "remove" -> remove(c);
            case "status" -> status(c, params);
            case "nudge" -> nudge(c, params);
            case "move" -> move(c, params);
            case "gcmove" -> gcMove(c, params);
            case "gcstop" -> gcStop(c, params);
            case "strike" -> strike(c, params);
            case "patrol" -> patrol(c, params);
            case "portal" -> portal(c, params);
            default -> usage(c);
        }
    }

    private static void spawn(Client c) {
        int gmId = c.getPlayer().getId();
        Character previous = spawnedByGm.remove(gmId);
        if (previous != null) {
            stopAllMovement(previous);
            BareBotFactory.removeBareBot(previous);
        }

        try {
            // Clone the invoking GM's persisted character as the visual/stat template.
            // This avoids SoloMapling upstream's hard-coded database character id 2.
            Character bot = BareBotFactory.createBareBot(
                    gmId,
                    c.getPlayer().getPosition(),
                    c.getPlayer().getMap());
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

        stopAllMovement(bot);
        BareBotFactory.removeBareBot(bot);
        c.getPlayer().yellowMessage("Removed SoloMapling QA bot " + bot.getName() + ".");
    }

    private static void status(Client c, String[] params) {
        if (params.length != 1) {
            usage(c);
            return;
        }
        Character bot = getBot(c);
        if (bot == null) {
            return;
        }

        Point position = bot.getPosition();
        c.getPlayer().yellowMessage(
                "QA bot " + bot.getName() + " (" + bot.getId() + ") map=" + bot.getMapId()
                        + " pos=" + position.x + "," + position.y
                        + " GCMove=" + (GCMovement.isEnabled(bot) ? "ON" : "OFF")
                        + " patrol=" + (BareBotAutopilot.isPatrolling(bot) ? "ON" : "OFF") + ".");
        c.getPlayer().yellowMessage(GCMovementDiagnostics.describe(bot));
    }

    private static void nudge(Client c, String[] params) {
        if (params.length != 2) {
            usage(c);
            return;
        }
        Character bot = getBot(c);
        if (bot == null) {
            return;
        }
        try {
            int deltaX = Integer.parseInt(params[1]);
            // Never allow the packet-path harness and GCMove to drive the same bot concurrently.
            GCMovement.disable(bot);
            BareBotMovement.nudge(bot, deltaX);
            c.getPlayer().yellowMessage("Moved QA bot by " + deltaX + " X.");
        } catch (NumberFormatException e) {
            c.getPlayer().yellowMessage("nudge requires an integer X offset.");
        } catch (EmptyMovementException | RuntimeException e) {
            c.getPlayer().yellowMessage("QA bot movement failed: " + e.getMessage());
        }
    }

    private static void move(Client c, String[] params) {
        if (params.length != 3) {
            usage(c);
            return;
        }
        Character bot = getBot(c);
        if (bot == null) {
            return;
        }
        try {
            int x = Integer.parseInt(params[1]);
            int y = Integer.parseInt(params[2]);
            GCMovement.disable(bot);
            BareBotMovement.moveTo(bot, new Point(x, y));
            c.getPlayer().yellowMessage("Moved QA bot to " + x + ", " + y + ".");
        } catch (NumberFormatException e) {
            c.getPlayer().yellowMessage("move requires integer X and Y coordinates.");
        } catch (EmptyMovementException | RuntimeException e) {
            c.getPlayer().yellowMessage("QA bot movement failed: " + e.getMessage());
        }
    }

    private static void gcMove(Client c, String[] params) {
        if (params.length != 3) {
            usage(c);
            return;
        }
        Character bot = getBot(c);
        if (bot == null) {
            return;
        }

        try {
            int x = Integer.parseInt(params[1]);
            int y = Integer.parseInt(params[2]);
            // GCMove owns the movement lock for its whole dynamic session; stop the
            // simpler scheduled patrol before handing control over.
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

    private static void gcStop(Client c, String[] params) {
        if (params.length != 1) {
            usage(c);
            return;
        }
        Character bot = getBot(c);
        if (bot == null) {
            return;
        }

        GCMovement.disable(bot);
        c.getPlayer().yellowMessage("GCMove disabled for QA bot.");
    }

    private static void strike(Client c, String[] params) {
        if (params.length > 2) {
            usage(c);
            return;
        }
        Character bot = getBot(c);
        if (bot == null) {
            return;
        }

        int damage = 1;
        if (params.length == 2) {
            try {
                damage = Integer.parseInt(params[1]);
            } catch (NumberFormatException e) {
                c.getPlayer().yellowMessage("strike damage must be an integer.");
                return;
            }
        }

        BareBotCombat.StrikeResult result = BareBotCombat.strikeNearest(bot, damage);
        if (!result.hit()) {
            c.getPlayer().yellowMessage("QA bot strike skipped: " + result.reason());
            return;
        }
        c.getPlayer().yellowMessage(
                "QA bot hit " + result.monsterName() + " (" + result.monsterId() + ") for "
                        + result.damage() + (result.killed() ? " and killed it." : "; HP left " + result.remainingHp() + "."));
    }

    private static void patrol(Client c, String[] params) {
        if (params.length != 2) {
            usage(c);
            return;
        }
        Character bot = getBot(c);
        if (bot == null) {
            return;
        }

        switch (params[1].toLowerCase()) {
            case "start" -> {
                GCMovement.disable(bot);
                if (BareBotAutopilot.startPatrol(bot)) {
                    c.getPlayer().yellowMessage("QA bot autonomous foothold patrol started.");
                } else {
                    c.getPlayer().yellowMessage("QA bot patrol could not start.");
                }
            }
            case "stop" -> {
                BareBotAutopilot.stop(bot);
                c.getPlayer().yellowMessage("QA bot autonomous foothold patrol stopped.");
            }
            default -> usage(c);
        }
    }

    private static void portal(Client c, String[] params) {
        if (params.length != 2) {
            usage(c);
            return;
        }
        Character bot = getBot(c);
        if (bot == null) {
            return;
        }

        int portalId;
        try {
            portalId = Integer.parseInt(params[1]);
        } catch (NumberFormatException e) {
            c.getPlayer().yellowMessage("portal requires an integer portal id.");
            return;
        }

        // Neither movement engine may race a map transition.
        stopAllMovement(bot);
        BareBotPortal.PortalResult result = BareBotPortal.enter(bot, portalId);
        if (result.success()) {
            c.getPlayer().yellowMessage("QA bot traversed portal " + portalId + ": "
                    + result.fromMapId() + " -> " + result.toMapId() + ".");
        } else {
            c.getPlayer().yellowMessage("QA bot portal traversal failed: " + result.reason());
        }
    }

    private static void stopAllMovement(Character bot) {
        BareBotAutopilot.stop(bot);
        GCMovement.disable(bot);
    }

    private static boolean onQaChannel(Client c) {
        return c.getChannelServer() != null
                && c.getChannelServer().getWorld() == QA_WORLD
                && c.getChannelServer().getId() == QA_CHANNEL;
    }

    private static Character getBot(Client c) {
        Character bot = spawnedByGm.get(c.getPlayer().getId());
        if (bot == null) {
            c.getPlayer().yellowMessage("Spawn a QA bot first with !qabot spawn.");
        }
        return bot;
    }

    private static void usage(Client c) {
        c.getPlayer().yellowMessage("Usage: !qabot spawn|remove|status|nudge <dx>|move <x> <y>|gcmove <x> <y>|gcstop|strike [damage]|patrol start|stop|portal <id>");
    }
}

package client.command.commands.gm4;

import client.Character;
import client.Client;
import client.command.Command;
import soloMapling.ArtificialPlayer.BareBotAutopilot;
import soloMapling.ArtificialPlayer.BareBotCombat;
import soloMapling.ArtificialPlayer.BareBotFactory;
import soloMapling.ArtificialPlayer.BareBotMovement;
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
        setDescription("Control one isolated SoloMapling QA bot: !qabot spawn|remove|nudge|move|strike|patrol");
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
            case "nudge" -> nudge(c, params);
            case "move" -> move(c, params);
            case "strike" -> strike(c, params);
            case "patrol" -> patrol(c, params);
            default -> usage(c);
        }
    }

    private static void spawn(Client c) {
        int gmId = c.getPlayer().getId();
        Character previous = spawnedByGm.remove(gmId);
        if (previous != null) {
            BareBotAutopilot.stop(previous);
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

        BareBotAutopilot.stop(bot);
        BareBotFactory.removeBareBot(bot);
        c.getPlayer().yellowMessage("Removed SoloMapling QA bot " + bot.getName() + ".");
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
            BareBotMovement.moveTo(bot, new Point(x, y));
            c.getPlayer().yellowMessage("Moved QA bot to " + x + ", " + y + ".");
        } catch (NumberFormatException e) {
            c.getPlayer().yellowMessage("move requires integer X and Y coordinates.");
        } catch (EmptyMovementException | RuntimeException e) {
            c.getPlayer().yellowMessage("QA bot movement failed: " + e.getMessage());
        }
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
        c.getPlayer().yellowMessage("Usage: !qabot spawn|remove|nudge <dx>|move <x> <y>|strike [damage]|patrol start|stop");
    }
}

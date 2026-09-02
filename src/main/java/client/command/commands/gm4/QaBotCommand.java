package client.command.commands.gm4;

import client.Character;
import client.Client;
import client.command.Command;
import soloMapling.ArtificialPlayer.BareBotFactory;

import java.sql.SQLException;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/** GM-only control surface for the first isolated SoloMapling smoke bot. */
public class QaBotCommand extends Command {
    private static final Map<Integer, Character> spawnedByGm = new ConcurrentHashMap<>();

    {
        setDescription("Spawn/remove one isolated SoloMapling QA bot: !qabot spawn|remove");
    }

    @Override
    public void execute(Client c, String[] params) {
        if (params.length != 1) {
            c.getPlayer().yellowMessage("Usage: !qabot spawn|remove");
            return;
        }

        String action = params[0].toLowerCase();
        if ("spawn".equals(action)) {
            spawn(c);
            return;
        }
        if ("remove".equals(action)) {
            remove(c);
            return;
        }

        c.getPlayer().yellowMessage("Usage: !qabot spawn|remove");
    }

    private static void spawn(Client c) {
        int gmId = c.getPlayer().getId();
        Character previous = spawnedByGm.remove(gmId);
        if (previous != null) {
            BareBotFactory.removeBareBot(previous);
        }

        try {
            Character bot = BareBotFactory.createBareBot(
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

        BareBotFactory.removeBareBot(bot);
        c.getPlayer().yellowMessage("Removed SoloMapling QA bot " + bot.getName() + ".");
    }
}

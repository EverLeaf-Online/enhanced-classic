package client.command.commands.gm4;

import client.Client;
import client.command.Command;
import soloMapling.ArtificialPlayer.BotQaFleet;
import soloMapling.ArtificialPlayer.BotQaSoak;

/** GM-only control surface for the bounded multi-bot SoloMapling QA fleet. */
public class QaFleetCommand extends Command {
    private static final int QA_WORLD = 0;
    private static final int QA_CHANNEL = 1;

    {
        setDescription("Control a bounded SoloMapling QA fleet: !qafleet spawn <1-12> [mapId]|status|remove");
    }

    @Override
    public void execute(Client c, String[] params) {
        if (params.length < 1) {
            usage(c);
            return;
        }
        String action = params[0].toLowerCase();
        if (action.equals("spawn") && !onQaChannel(c)) {
            c.getPlayer().yellowMessage("SoloMapling QA fleets can only be spawned on world 0, channel 1.");
            return;
        }

        switch (action) {
            case "spawn" -> spawn(c, params);
            case "status" -> report(c, BotQaFleet.status(c.getPlayer().getId()));
            case "remove" -> remove(c);
            default -> usage(c);
        }
    }

    private static void spawn(Client c, String[] params) {
        if (params.length < 2 || params.length > 3) {
            usage(c);
            return;
        }
        try {
            int count = Integer.parseInt(params[1]);
            int mapId = params.length == 3 ? Integer.parseInt(params[2]) : c.getPlayer().getMapId();
            int ownerId = c.getPlayer().getId();
            if (BotQaSoak.isRunning(ownerId)) BotQaSoak.stop(ownerId);
            BotQaFleet.FleetResult result = BotQaFleet.spawn(ownerId, ownerId, count, QA_WORLD, QA_CHANNEL, mapId);
            report(c, result);
        } catch (NumberFormatException e) {
            c.getPlayer().yellowMessage("qafleet spawn requires an integer count and optional map id.");
        }
    }

    private static void remove(Client c) {
        int ownerId = c.getPlayer().getId();
        if (BotQaSoak.isRunning(ownerId)) {
            BotQaSoak.Report soak = BotQaSoak.stop(ownerId);
            c.getPlayer().yellowMessage("QA soak stopped and fleet cleaned: " + soak.reason() + ".");
            return;
        }
        report(c, BotQaFleet.remove(ownerId));
    }

    private static void report(Client c, BotQaFleet.FleetResult result) {
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

    private static boolean onQaChannel(Client c) {
        return c.getChannelServer() != null
                && c.getChannelServer().getWorld() == QA_WORLD
                && c.getChannelServer().getId() == QA_CHANNEL;
    }

    private static void usage(Client c) {
        c.getPlayer().yellowMessage("Usage: !qafleet spawn <1-12> [mapId]|status|remove");
    }
}

package client.command.commands.gm4;

import client.Client;
import client.command.Command;
import soloMapling.ArtificialPlayer.BotQaSoak;

/** GM-only explicit start/stop/status surface for bounded SoloMapling soak testing. */
public class QaSoakCommand extends Command {
    private static final int QA_WORLD = 0;
    private static final int QA_CHANNEL = 1;

    {
        setDescription("Run bounded SoloMapling QA soak: !qasoak start <minutes>|status|stop (max 720 minutes)");
    }

    @Override
    public void execute(Client c, String[] params) {
        if (params.length < 1) {
            usage(c);
            return;
        }
        String action = params[0].toLowerCase();
        switch (action) {
            case "start" -> start(c, params);
            case "status" -> report(c, BotQaSoak.status(c.getPlayer().getId()));
            case "stop" -> report(c, BotQaSoak.stop(c.getPlayer().getId()));
            default -> usage(c);
        }
    }

    private static void start(Client c, String[] params) {
        if (params.length != 2) {
            usage(c);
            return;
        }
        if (!onQaChannel(c)) {
            c.getPlayer().yellowMessage("SoloMapling QA soaks can only be started on world 0, channel 1.");
            return;
        }
        try {
            int minutes = Integer.parseInt(params[1]);
            report(c, BotQaSoak.start(c.getPlayer().getId(), minutes));
        } catch (NumberFormatException e) {
            c.getPlayer().yellowMessage("qasoak start requires an integer duration in minutes.");
        }
    }

    private static void report(Client c, BotQaSoak.Report report) {
        if (!report.accepted()) {
            c.getPlayer().yellowMessage("QA soak rejected: " + report.reason() + ".");
            return;
        }
        long elapsedSeconds = report.elapsedMs() / 1000L;
        c.getPlayer().yellowMessage("QA soak " + report.reason()
                + ": running=" + report.running()
                + " bots=" + report.bots()
                + " elapsed=" + elapsedSeconds + "s"
                + " checks=" + report.checks()
                + " restarts=" + report.restarts()
                + " violations=" + report.violations()
                + " cleaned=" + report.cleanedUp() + ".");
        if (!"none".equals(report.details())) {
            c.getPlayer().yellowMessage("QA soak details: " + report.details());
        }
    }

    private static boolean onQaChannel(Client c) {
        return c.getChannelServer() != null
                && c.getChannelServer().getWorld() == QA_WORLD
                && c.getChannelServer().getId() == QA_CHANNEL;
    }

    private static void usage(Client c) {
        c.getPlayer().yellowMessage("Usage: !qasoak start <1-720 minutes>|status|stop");
    }
}

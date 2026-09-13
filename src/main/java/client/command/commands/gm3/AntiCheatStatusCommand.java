package client.command.commands.gm3;

import client.Character;
import client.Client;
import client.command.Command;
import server.AntiCheatService;

public class AntiCheatStatusCommand extends Command {
    {
        setDescription("Show recent EverLeaf anti-cheat evidence for an online character.");
    }

    @Override
    public void execute(Client c, String[] params) {
        Character gm = c.getPlayer();
        if (params.length < 1) {
            gm.yellowMessage("Syntax: !acstatus <ign>");
            return;
        }

        Character victim = c.getWorldServer().getPlayerStorage().getCharacterByName(params[0]);
        if (victim == null) {
            gm.yellowMessage("Player '" + params[0] + "' is not online in this world.");
            return;
        }

        for (String line : AntiCheatService.getStatus(victim)) {
            gm.yellowMessage(line);
        }
    }
}

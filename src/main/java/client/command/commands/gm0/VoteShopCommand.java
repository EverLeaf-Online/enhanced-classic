package client.command.commands.gm0;

import client.Client;
import client.command.Command;

/** Opens the EverLeaf Free Market utility hub that contains the Vote Point exchange. */
public class VoteShopCommand extends Command {
    {
        setDescription("Open the EverLeaf Vote Point exchange hub.");
    }

    @Override
    public void execute(Client client, String[] params) {
        if (client.getPlayer().getEventInstance() != null) {
            client.getPlayer().yellowMessage("The Vote Point exchange is unavailable inside active events, PQs, or boss instances.");
            return;
        }
        client.getAbstractPlayerInteraction().openNpc(9030100);
    }
}

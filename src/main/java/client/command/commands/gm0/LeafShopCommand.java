package client.command.commands.gm0;

import client.Client;
import client.command.Command;

/** Opens EverLeaf's Maple Leaf sink/exchange from any safe normal context. */
public class LeafShopCommand extends Command {
    {
        setDescription("Open the EverLeaf Maple Leaf exchange.");
    }

    @Override
    public void execute(Client c, String[] params) {
        if (c.getPlayer().getEventInstance() != null) {
            c.getPlayer().yellowMessage("The Maple Leaf exchange is unavailable inside active events, PQs, or boss instances.");
            return;
        }
        c.getAbstractPlayerInteraction().openNpc(9030100, "everleaf_leaf_exchange");
    }
}

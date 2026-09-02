package client.command.commands.gm0;

import client.Character;
import client.Client;
import client.command.Command;
import scripting.npc.NPCScriptManager;
import server.maps.FieldLimit;
import server.maps.MiniDungeonInfo;

/** Opens the EverLeaf utility hub from safe field maps. */
public class EverLeafCommand extends Command {
    private static final int EVERLEAF_HUB_NPC = 9030100;

    {
        setDescription("Open the EverLeaf utility hub.");
    }

    @Override
    public void execute(Client c, String[] params) {
        Character player = c.getPlayer();

        if (!player.isAlive()) {
            player.dropMessage(1, "You cannot open the EverLeaf hub while dead.");
            return;
        }

        if (player.isChangingMaps()) {
            player.dropMessage(1, "Please wait until the map change finishes.");
            return;
        }

        if (player.getTrade() != null || player.getPlayerShop() != null || player.getHiredMerchant() != null) {
            player.dropMessage(1, "Finish your current trade or merchant interaction first.");
            return;
        }

        if (!player.isGM()
                && (player.getEventInstance() != null
                || MiniDungeonInfo.isDungeonMap(player.getMapId())
                || FieldLimit.CANNOTMIGRATE.check(player.getMap().getFieldLimit()))) {
            player.dropMessage(1, "The EverLeaf hub cannot be opened in this map.");
            return;
        }

        NPCScriptManager.getInstance().start(c, EVERLEAF_HUB_NPC, player);
    }
}

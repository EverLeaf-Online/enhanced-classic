/*
    This file is part of the HeavenMS MapleStory Server, commands OdinMS-based
    Copyleft (L) 2016 - 2019 RonanLana

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation version 3 as published by
    the Free Software Foundation. You may not use, modify or distribute
    this program under any other version of the GNU Affero General Public
    License.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/

/*
   @Author: Arthur L - Refactored command content into modules
*/
package client.command.commands.gm3;

import client.Character;
import client.Client;
import client.command.Command;
import net.server.Server;
import server.events.gm.Event;
import tools.PacketCreator;

public class StartEventCommand extends Command {
    private static final int DEFAULT_PLAYER_LIMIT = 50;

    {
        setDescription("Start an event on current map. Usage: !startevent [playerLimit]");
    }

    static int parsePlayerLimit(String[] params) {
        if (params.length == 0) {
            return DEFAULT_PLAYER_LIMIT;
        }
        if (params.length != 1) {
            throw new IllegalArgumentException("Expected zero or one player-limit argument.");
        }

        final int players;
        try {
            players = Integer.parseInt(params[0]);
        } catch (NumberFormatException e) {
            throw new IllegalArgumentException("Player limit must be a positive integer.", e);
        }

        if (players <= 0) {
            throw new IllegalArgumentException("Player limit must be a positive integer.");
        }
        return players;
    }

    @Override
    public void execute(Client c, String[] params) {
        Character player = c.getPlayer();

        final int players;
        try {
            players = parsePlayerLimit(params);
        } catch (IllegalArgumentException e) {
            player.yellowMessage("Syntax: !startevent [playerLimit] (positive integer)");
            return;
        }

        c.getChannelServer().setEvent(new Event(player.getMapId(), players));
        Server.getInstance().broadcastMessage(c.getWorld(), PacketCreator.earnTitleMessage(
                "[Event] An event has started on "
                        + player.getMap().getMapName()
                        + " and will allow "
                        + players
                        + " players to join. Type @joinevent to participate."));
        Server.getInstance().broadcastMessage(c.getWorld(),
                PacketCreator.serverNotice(6, "[Event] An event has started on "
                        + player.getMap().getMapName()
                        + " and will allow "
                        + players
                        + " players to join. Type @joinevent to participate."));
    }
}

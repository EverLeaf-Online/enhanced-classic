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

package client.command.commands.gm0;

import client.Character;
import client.Client;
import client.command.Command;
import constants.id.MapId;
import server.maps.FieldLimit;
import server.maps.MapleMap;
import server.maps.MiniDungeonInfo;
import server.maps.Portal;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.TimeUnit;

public class UnstuckCommand extends Command {
    private static final long COOLDOWN_MS = TimeUnit.MINUTES.toMillis(5);
    private static final Map<Integer, Long> lastUse = new ConcurrentHashMap<>();

    {
        setDescription("Warp to a safe map if your character is stuck.");
    }

    @Override
    public void execute(Client client, String[] params) {
        Character player = client.getPlayer();

        if (!player.isAlive()) {
            player.yellowMessage("You cannot use @unstuck while dead.");
            return;
        }

        if (player.getEventInstance() != null
                || MiniDungeonInfo.isDungeonMap(player.getMapId())
                || FieldLimit.CANNOTMIGRATE.check(player.getMap().getFieldLimit())) {
            player.yellowMessage("@unstuck cannot be used in this map or instance.");
            return;
        }

        long now = System.currentTimeMillis();
        Long previousUse = lastUse.get(player.getId());
        if (previousUse != null) {
            long remaining = COOLDOWN_MS - (now - previousUse);
            if (remaining > 0) {
                long seconds = (remaining + 999) / 1000;
                player.yellowMessage("@unstuck is on cooldown for another " + seconds + " second(s).");
                return;
            }
        }

        MapleMap currentMap = player.getMap();
        MapleMap targetMap = currentMap.getReturnMap();

        if (targetMap == null || targetMap.getId() == currentMap.getId()) {
            targetMap = client.getChannelServer().getMapFactory().getMap(MapId.HENESYS);
        }

        if (targetMap == null) {
            player.yellowMessage("Unable to find a safe return map. Please contact EverLeaf staff.");
            return;
        }

        Portal targetPortal = targetMap.getRandomPlayerSpawnpoint();
        if (targetPortal == null) {
            player.yellowMessage("Unable to find a safe spawn point. Please contact EverLeaf staff.");
            return;
        }

        lastUse.put(player.getId(), now);
        player.changeMap(targetMap, targetPortal);
        player.yellowMessage("You have been moved to a safe map. @unstuck has a 5-minute cooldown.");
    }
}

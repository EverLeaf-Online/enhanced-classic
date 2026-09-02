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
package client.command.commands.gm0;

import client.Client;
import client.command.Command;

import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.TimeZone;

public class TimeCommand extends Command {
    private static final TimeZone EVERLEAF_TIME_ZONE = TimeZone.getTimeZone("America/New_York");

    {
        setDescription("Show current EverLeaf server time (Eastern Time).");
    }

    @Override
    public void execute(Client client, String[] params) {
        DateFormat dateFormat = new SimpleDateFormat("yyyy-MM-dd hh:mm:ss a z");
        dateFormat.setTimeZone(EVERLEAF_TIME_ZONE);
        client.getPlayer().yellowMessage("EverLeaf Server Time: " + dateFormat.format(new Date()));
    }
}

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
package client.command.commands.gm2;

import client.Character;
import client.Client;
import client.Job;
import client.command.Command;

public class JobCommand extends Command {
    {
        setDescription("Change job of a player.");
    }

    private static Job resolveJob(Character issuer, String value) {
        final int jobId;
        try {
            jobId = Integer.parseInt(value);
        } catch (NumberFormatException e) {
            issuer.message("Jobid '" + value + "' is not valid.");
            return null;
        }

        Job job = Job.getById(jobId);
        if (job == null) {
            issuer.message("Jobid " + jobId + " is not available.");
        }
        return job;
    }

    @Override
    public void execute(Client c, String[] params) {
        Character player = c.getPlayer();
        if (params.length == 1) {
            Job job = resolveJob(player, params[0]);
            if (job == null) {
                return;
            }

            player.changeJob(job);
            player.equipChanged();
        } else if (params.length == 2) {
            Character victim = c.getWorldServer().getPlayerStorage().getCharacterByName(params[0]);

            if (victim != null) {
                Job job = resolveJob(player, params[1]);
                if (job == null) {
                    return;
                }

                victim.changeJob(job);
                victim.equipChanged();
            } else {
                player.message("Player '" + params[0] + "' could not be found.");
            }
        } else {
            player.message("Syntax: !job <job id> <opt: IGN of another person>");
        }
    }
}

/*
	This file is part of the OdinMS Maple Story Server
    Copyright (C) 2008 Patrick Huy <patrick.huy@frz.cc>
		       Matthias Butz <matze@odinms.de>
		       Jan Christian Meyer <vimes@odinms.de>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation version 3 as published by the Free Software
    Foundation. You may not use, modify or distribute this program under any other version of the GNU Affero General Public
    License.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/
package server.events.gm;

import client.Character;
import constants.id.MapId;
import server.TimerManager;
import tools.PacketCreator;
import tools.Randomizer;

import java.util.Arrays;
import java.util.concurrent.ScheduledFuture;

/**
 * @author kevintjuh93
 */
public class Ola {
    private static final int EVENT_DURATION_MS = 360000;
    private static final int[] STAGE_PORTAL_COUNTS = {5, 8, 15};

    private final Character chr;
    private final int[] correctPortals;
    private long time = 0;
    private long timeStarted = 0;
    private ScheduledFuture<?> schedule = null;

    public Ola(final Character chr) {
        this(chr, generateCorrectPortals());
    }

    public Ola(final Character chr, int[] correctPortals) {
        if (correctPortals == null || correctPortals.length != STAGE_PORTAL_COUNTS.length) {
            throw new IllegalArgumentException("Ola Ola requires exactly three stage portal selections.");
        }

        this.chr = chr;
        this.correctPortals = Arrays.copyOf(correctPortals, correctPortals.length);
        this.schedule = TimerManager.getInstance().schedule(() -> {
            if (MapId.isOlaOla(chr.getMapId())) {
                chr.changeMap(chr.getMap().getReturnMap());
            }
            resetTimes();
        }, EVENT_DURATION_MS);
    }

    public static int[] generateCorrectPortals() {
        int[] stages = {
                Randomizer.nextInt(STAGE_PORTAL_COUNTS[0]),
                Randomizer.nextInt(STAGE_PORTAL_COUNTS[1]),
                Randomizer.nextInt(STAGE_PORTAL_COUNTS[2])
        };

        // Retail/OdinMS data deliberately skips ch02 for the first stage.
        if (stages[0] == 2) {
            stages[0] = 3;
        }
        return stages;
    }

    public boolean isCorrectPortal(String portalName, int mapId) {
        if (!isTimerStarted() || !MapId.isOlaOla(mapId) || portalName == null) {
            return false;
        }

        int stage = mapId % 10 - 1;
        if (stage < 0 || stage >= correctPortals.length) {
            return false;
        }

        return portalName.equals(String.format("ch%02d", correctPortals[stage]));
    }

    public void startOla() {
        chr.getMap().startEvent();
        chr.sendPacket(PacketCreator.getClock(EVENT_DURATION_MS / 1000));
        this.timeStarted = System.currentTimeMillis();
        this.time = EVENT_DURATION_MS;

        if (chr.getMap().getPortal("join00") != null) {
            chr.getMap().getPortal("join00").setPortalStatus(true);
        }
        chr.sendPacket(PacketCreator.serverNotice(0, "The portal has now opened. Press the up arrow key at the portal to enter."));
    }

    public boolean isTimerStarted() {
        return time > 0 && timeStarted > 0;
    }

    public long getTime() {
        return time;
    }

    public void resetTimes() {
        this.time = 0;
        this.timeStarted = 0;
        if (schedule != null) {
            schedule.cancel(false);
            schedule = null;
        }
    }

    public long getTimeLeft() {
        return Math.max(0, time - (System.currentTimeMillis() - timeStarted));
    }
}

/*
 This file is part of the OdinMS Maple Story Server
 Copyright (C) 2008 Patrick Huy <patrick.huy@frz.cc>
 Matthias Butz <matze@odinms.de>
 Jan Christian Meyer <vimes@odinms.de>

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU Affero General Public License as
 published by the Free Software Foundation version 3 as published by
 the Free Software Foundation. You may not use, modify or distribute
 this program under any other version of the GNU Affero General Public License.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU Affero General Public License for more details.

 You should have received a copy of the GNU Affero General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */
package net.server.handlers.login;

import client.Client;
import client.creator.novice.BeginnerCreator;
import client.creator.novice.EvanCreator;
import client.creator.novice.LegendCreator;
import client.creator.novice.NoblesseCreator;
import net.AbstractPacketHandler;
import net.packet.InPacket;
import tools.PacketCreator;

public final class CreateCharHandler extends AbstractPacketHandler {
    static final int TYPE_CYGNUS = 0;
    static final int TYPE_EXPLORER = 1;
    static final int TYPE_ARAN = 2;
    static final int TYPE_EVAN = 3;

    /**
     * Server-side capability gate for the character-family selector.
     *
     * <p>The modernized client is allowed to display future families as locked previews, but
     * modified clients must never be able to create one before its complete server/WZ/runtime
     * implementation is enabled here.</p>
     */
    static boolean isSupportedCharacterType(int type) {
        return type == TYPE_CYGNUS || type == TYPE_EXPLORER || type == TYPE_ARAN || type == TYPE_EVAN;
    }

    @Override
    public void handlePacket(InPacket p, Client c) {
        String name = p.readString();
        int job = p.readInt();
        int face = p.readInt();

        int hair = p.readInt();
        int haircolor = p.readInt();
        int skincolor = p.readInt();

        int top = p.readInt();
        int bottom = p.readInt();
        int shoes = p.readInt();
        int weapon = p.readInt();
        int gender = p.readByte();

        if (!isSupportedCharacterType(job)) {
            c.sendPacket(PacketCreator.deleteCharResponse(0, 9));
            return;
        }

        int status;
        switch (job) {
        case TYPE_CYGNUS:
            status = NoblesseCreator.createCharacter(c, name, face, hair + haircolor, skincolor, top, bottom, shoes, weapon, gender);
            break;
        case TYPE_EXPLORER:
            status = BeginnerCreator.createCharacter(c, name, face, hair + haircolor, skincolor, top, bottom, shoes, weapon, gender);
            break;
        case TYPE_ARAN:
            status = LegendCreator.createCharacter(c, name, face, hair + haircolor, skincolor, top, bottom, shoes, weapon, gender);
            break;
        case TYPE_EVAN:
            status = EvanCreator.createCharacter(c, name, face, hair + haircolor, skincolor, top, bottom, shoes, weapon, gender);
            break;
        default:
            // Defensive only: isSupportedCharacterType already rejects every other value.
            c.sendPacket(PacketCreator.deleteCharResponse(0, 9));
            return;
        }

        if (status == -2) {
            c.sendPacket(PacketCreator.deleteCharResponse(0, 9));
        }
    }
}

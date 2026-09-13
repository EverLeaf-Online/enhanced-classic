package net.server.channel.handlers;

import client.Client;
import client.keybind.QuickslotBinding;
import net.AbstractPacketHandler;
import net.packet.InPacket;

/**
 * Accepts modern EverLeaf 26-slot quickslot updates while retaining an 8-slot
 * transition path for clients that are finishing a launcher update.
 */
public class QuickslotKeyMappedModifiedHandler extends AbstractPacketHandler {
    @Override
    public void handlePacket(InPacket p, Client c) {
        if (c.getPlayer() == null) {
            return;
        }

        int bytes = p.available();
        int legacyBytes = QuickslotBinding.LEGACY_QUICKSLOT_SIZE * Integer.BYTES;
        int modernBytes = QuickslotBinding.QUICKSLOT_SIZE * Integer.BYTES;
        if (bytes != legacyBytes && bytes != modernBytes) {
            return;
        }

        int count = bytes / Integer.BYTES;
        byte[] keys = new byte[count];
        for (int i = 0; i < count; i++) {
            int key = p.readInt();
            if (key < 0 || key > 0xFF) {
                return;
            }
            keys[i] = (byte) key;
        }
        c.getPlayer().changeQuickslotKeybinding(keys);
    }
}

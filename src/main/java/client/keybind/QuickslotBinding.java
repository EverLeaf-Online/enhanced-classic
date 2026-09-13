package client.keybind;

import net.packet.OutPacket;

import java.util.Arrays;

/**
 * EverLeaf quickslot mapping. The modern HUD exposes 26 positions (13x2).
 * Legacy v83 rows contain eight positions and are expanded losslessly on load.
 */
public class QuickslotBinding {
    public static final int LEGACY_QUICKSLOT_SIZE = 8;
    public static final int QUICKSLOT_SIZE = 26;

    // Matches the first 26 keys installed by EverLeafModernStatusBar in the client.
    public static final byte[] DEFAULT_QUICKSLOTS = {
            0x2A, 0x52, 0x47, 0x49, 0x02, 0x03, 0x04, 0x05, 0x06, 0x1E, 0x1F, 0x20, 0x21,
            0x1D, 0x53, 0x4F, 0x51, 0x10, 0x11, 0x12, 0x13, 0x14, 0x2C, 0x2D, 0x2E, 0x2F
    };

    private final byte[] m_aQuickslotKeyMapped;

    public QuickslotBinding(byte[] aKeys) {
        this.m_aQuickslotKeyMapped = normalize(aKeys);
    }

    public static byte[] normalize(byte[] aKeys) {
        if (aKeys == null) {
            throw new IllegalArgumentException("quickslot keys cannot be null");
        }
        if (aKeys.length == QUICKSLOT_SIZE) {
            return aKeys.clone();
        }
        if (aKeys.length == LEGACY_QUICKSLOT_SIZE) {
            byte[] expanded = DEFAULT_QUICKSLOTS.clone();
            System.arraycopy(aKeys, 0, expanded, 0, LEGACY_QUICKSLOT_SIZE);
            return expanded;
        }
        throw new IllegalArgumentException(String.format(
                "quickslot size should be %d or legacy %d (got %d)",
                QUICKSLOT_SIZE, LEGACY_QUICKSLOT_SIZE, aKeys.length));
    }

    public void encode(OutPacket p) {
        // The patched client builds the same 26-entry defaults locally when this is false.
        if (Arrays.equals(this.m_aQuickslotKeyMapped, DEFAULT_QUICKSLOTS)) {
            p.writeBool(false);
            return;
        }

        p.writeBool(true);
        for (byte nKey : this.m_aQuickslotKeyMapped) {
            p.writeInt(nKey & 0xFF);
        }
    }

    public byte[] GetKeybindings() {
        return m_aQuickslotKeyMapped.clone();
    }
}

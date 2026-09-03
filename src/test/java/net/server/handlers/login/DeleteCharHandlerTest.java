package net.server.handlers.login;

import constants.string.CharsetConstants;
import io.netty.buffer.ByteBuf;
import io.netty.buffer.Unpooled;
import net.packet.ByteBufInPacket;
import net.packet.InPacket;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

class DeleteCharHandlerTest {
    private static final int CHARACTER_ID = 123456;

    @Test
    void parsesPicProtectedDeletePacket() {
        ByteBuf buffer = Unpooled.buffer();
        byte[] pic = "2468".getBytes(CharsetConstants.CHARSET);
        buffer.writeShortLE(pic.length);
        buffer.writeBytes(pic);
        buffer.writeIntLE(CHARACTER_ID);
        InPacket packet = new ByteBufInPacket(buffer);

        DeleteCharHandler.DeleteRequest request = DeleteCharHandler.readDeleteRequest(packet, true);

        assertEquals("2468", request.pic());
        assertEquals(CHARACTER_ID, request.characterId());
        assertEquals(0, packet.available());
    }

    @Test
    void parsesIdOnlyDeletePacketWhenPicIsDisabled() {
        ByteBuf buffer = Unpooled.buffer();
        buffer.writeIntLE(CHARACTER_ID);
        InPacket packet = new ByteBufInPacket(buffer);

        DeleteCharHandler.DeleteRequest request = DeleteCharHandler.readDeleteRequest(packet, false);

        assertEquals("", request.pic());
        assertEquals(CHARACTER_ID, request.characterId());
        assertEquals(0, packet.available());
    }

    @Test
    void parsesEmptyPicPrefixDeletePacketWhenPicIsDisabled() {
        ByteBuf buffer = Unpooled.buffer();
        buffer.writeShortLE(0);
        buffer.writeIntLE(CHARACTER_ID);
        InPacket packet = new ByteBufInPacket(buffer);

        DeleteCharHandler.DeleteRequest request = DeleteCharHandler.readDeleteRequest(packet, false);

        assertEquals("", request.pic());
        assertEquals(CHARACTER_ID, request.characterId());
        assertEquals(0, packet.available());
    }

    @Test
    void ignoresAuthenticationPrefixWhenPicIsBypassed() {
        ByteBuf buffer = Unpooled.buffer();
        buffer.writeShortLE(4);
        buffer.writeBytes(new byte[]{1, 2, 3, 4});
        buffer.writeIntLE(CHARACTER_ID);
        InPacket packet = new ByteBufInPacket(buffer);

        DeleteCharHandler.DeleteRequest request = DeleteCharHandler.readDeleteRequest(packet, false);

        assertEquals(CHARACTER_ID, request.characterId());
        assertEquals(0, packet.available());
    }

    @Test
    void rejectsDeletePacketWithoutCharacterId() {
        ByteBuf buffer = Unpooled.buffer();
        buffer.writeByte(1);
        InPacket packet = new ByteBufInPacket(buffer);

        assertThrows(IllegalArgumentException.class, () -> DeleteCharHandler.readDeleteRequest(packet, false));
    }
}

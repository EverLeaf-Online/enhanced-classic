package soloMapling.ArtificialPlayer;

import client.Character;
import io.netty.buffer.ByteBuf;
import io.netty.buffer.Unpooled;
import net.packet.ByteBufInPacket;
import net.packet.InPacket;
import server.maps.Foothold;
import tools.PacketCreator;
import tools.exceptions.EmptyMovementException;

import java.awt.Point;

import static net.server.channel.handlers.AbstractMovementPacketHandler.updatePositionBot;

/**
 * Minimal movement executor for the first EverLeaf SoloMapling smoke bot.
 *
 * <p>It deliberately mirrors SoloMapling's BotMove packet path without pulling
 * in recordings/pathfinding yet: generate one legal absolute movement command,
 * feed it through the same headless movement parser, update map position, and
 * broadcast the normal v83 player movement packet to real clients.</p>
 */
public final class BareBotMovement {
    private BareBotMovement() {
    }

    public static void moveTo(Character bot, Point target) throws EmptyMovementException {
        if (bot == null || bot.getMap() == null) {
            throw new IllegalArgumentException("bot must be on a map");
        }
        if (target == null) {
            throw new IllegalArgumentException("target must not be null");
        }

        short x = checkedShort(target.x, "x");
        short y = checkedShort(target.y, "y");
        short footholdId = 0;
        Foothold foothold = bot.getMap().getFootholds().findBelow(target);
        if (foothold != null) {
            footholdId = (short) foothold.getId();
        }

        byte stance = target.x < bot.getPosition().x ? (byte) 5 : (byte) 4;
        InPacket packet = createAbsoluteMovementPacket(x, y, footholdId, stance);
        applyAndBroadcast(bot, packet);
    }

    public static void nudge(Character bot, int deltaX) throws EmptyMovementException {
        Point current = bot.getPosition();
        moveTo(bot, new Point(current.x + deltaX, current.y));
    }

    private static InPacket createAbsoluteMovementPacket(short x, short y, short footholdId, byte stance) {
        ByteBuf buffer = Unpooled.buffer();
        for (int i = 0; i < 9; i++) {
            buffer.writeByte(0);
        }

        buffer.writeByte(1);       // one movement command
        buffer.writeByte(0);       // normal/absolute movement
        buffer.writeShortLE(x);
        buffer.writeShortLE(y);
        buffer.writeShortLE(0);    // x wobble
        buffer.writeShortLE(0);    // y wobble
        buffer.writeShortLE(footholdId);
        buffer.writeByte(stance);
        buffer.writeShortLE(250);  // duration
        return new ByteBufInPacket(buffer);
    }

    private static void applyAndBroadcast(Character bot, InPacket packet) throws EmptyMovementException {
        packet.skip(9);
        int movementDataStart = packet.getPosition();
        updatePositionBot(packet, bot, 0);
        long movementDataLength = packet.getPosition() - movementDataStart;
        packet.seek(movementDataStart);

        bot.getMap().moveBot(bot, bot.getPosition());
        if (bot.isHidden()) {
            bot.getMap().broadcastGMMessage(
                    bot,
                    PacketCreator.movePlayer(bot.getId(), packet, movementDataLength),
                    false);
        } else {
            bot.getMap().broadcastMessage(
                    bot,
                    PacketCreator.movePlayer(bot.getId(), packet, movementDataLength),
                    false);
        }
    }

    private static short checkedShort(int value, String field) {
        if (value < Short.MIN_VALUE || value > Short.MAX_VALUE) {
            throw new IllegalArgumentException(field + " is outside v83 movement range: " + value);
        }
        return (short) value;
    }
}

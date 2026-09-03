#!/usr/bin/env python3
"""Apply the minimal SoloMapling player-movement hook onto EverLeaf.

EverLeaf's movement parser stays authoritative. SoloMapling only needs a public
headless variant of the existing player-position parser so generated bot packets
can update an AnimatedMapObject without going through a real Netty session.
"""
from pathlib import Path

TARGET = Path("src/main/java/net/server/channel/handlers/AbstractMovementPacketHandler.java")
MARKER = "public static void updatePositionBot(InPacket p, AnimatedMapObject target, int yOffset)"

METHOD = r'''

    /**
     * SoloMapling headless movement parser.
     *
     * <p>This intentionally mirrors the server-authoritative subset of
     * {@link #updatePosition(InPacket, AnimatedMapObject, int)}. It consumes
     * the generated movement packet, updates absolute position/stance, and
     * ignores client-only wobble/duration fields.</p>
     */
    public static void updatePositionBot(InPacket p, AnimatedMapObject target, int yOffset)
            throws EmptyMovementException {
        byte numCommands = p.readByte();
        if (numCommands < 1) {
            throw new EmptyMovementException(p);
        }

        for (byte i = 0; i < numCommands; i++) {
            byte command = p.readByte();
            switch (command) {
                case 0:
                case 5:
                case 17: {
                    short xpos = p.readShort();
                    short ypos = p.readShort();
                    target.setPosition(new Point(xpos, ypos + yOffset));
                    p.skip(6);
                    target.setStance(p.readByte());
                    p.readShort();
                    break;
                }
                case 1:
                case 2:
                case 6:
                case 12:
                case 13:
                case 16:
                case 18:
                case 19:
                case 20:
                case 22: {
                    p.skip(4);
                    target.setStance(p.readByte());
                    p.readShort();
                    break;
                }
                case 3:
                case 4:
                case 7:
                case 8:
                case 9:
                case 11: {
                    p.skip(8);
                    target.setStance(p.readByte());
                    break;
                }
                case 14:
                    p.skip(9);
                    break;
                case 10:
                    p.readByte();
                    break;
                case 15: {
                    p.skip(12);
                    target.setStance(p.readByte());
                    p.readShort();
                    break;
                }
                case 21:
                    p.skip(3);
                    break;
                default:
                    log.warn("Unhandled bot movement case: {}", command);
                    throw new EmptyMovementException(p);
            }
        }
    }
'''


def main() -> None:
    text = TARGET.read_text(encoding="utf-8")
    if MARKER in text:
        print("SoloMapling movement hook already present.")
        return

    close = text.rfind("}")
    if close == -1:
        raise SystemExit("Could not locate AbstractMovementPacketHandler class closing brace")

    updated = text[:close] + METHOD + text[close:]
    TARGET.write_text(updated, encoding="utf-8")
    print("SoloMapling movement hook applied (AbstractMovementPacketHandler.updatePositionBot).")


if __name__ == "__main__":
    main()

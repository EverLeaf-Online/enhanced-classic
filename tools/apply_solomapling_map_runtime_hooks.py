#!/usr/bin/env python3
"""Apply minimal SoloMapling runtime hooks to EverLeaf MapleMap.

Adds only the headless-bot movement entrypoint and keeps socketless bots out of
normal ranged-object visibility bookkeeping. EverLeaf's map/event logic remains
authoritative.
"""
from pathlib import Path

TARGET = Path("src/main/java/server/maps/MapleMap.java")


def main() -> None:
    text = TARGET.read_text(encoding="utf-8")

    static_import = "import static soloMapling.ArtificialPlayer.BotHelpers.isBot;\n"
    if static_import not in text:
        anchor = "import static java.util.concurrent.TimeUnit.SECONDS;\n"
        if anchor not in text:
            raise SystemExit("Could not locate MapleMap static-import anchor")
        text = text.replace(anchor, anchor + static_import, 1)

    if "public void moveBot(Character player, Point newPosition)" not in text:
        anchor = "    public void movePlayer(Character player, Point newPosition) {\n"
        if anchor not in text:
            raise SystemExit("Could not locate MapleMap.movePlayer anchor")
        addition = """    /** SoloMapling headless movement path: position is server-authoritative. */
    public void moveBot(Character player, Point newPosition) {
        player.setPosition(newPosition);
    }

"""
        text = text.replace(anchor, addition + anchor, 1)

    marker = "// Headless bots do not maintain client-side ranged visibility state."
    if marker not in text:
        old = """                    if (chr.getPosition().distanceSq(mapobject.getPosition()) <= getRangedDistance()) {
                        inRangeCharacters.add(chr);
                        chr.addVisibleMapObject(mapobject);
                    }
"""
        new = """                    if (chr.getPosition().distanceSq(mapobject.getPosition()) <= getRangedDistance()) {
                        // Headless bots do not maintain client-side ranged visibility state.
                        if (!isBot(chr)) {
                            inRangeCharacters.add(chr);
                            chr.addVisibleMapObject(mapobject);
                        }
                    }
"""
        if old not in text:
            raise SystemExit("Could not locate MapleMap ranged-object visibility anchor")
        text = text.replace(old, new, 1)

    TARGET.write_text(text, encoding="utf-8")
    print("SoloMapling map runtime hooks applied (moveBot + headless visibility exclusion).")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Apply minimal SoloMapling combat/runtime host hooks.

EverLeaf remains authoritative for Monster combat/EXP logic. This transform only
prevents socketless bot characters from being auto-selected as monster movement
controllers, matching SoloMapling's required behavior without replacing the
host file.
"""
from pathlib import Path

MONSTER = Path("src/main/java/server/life/Monster.java")


def main() -> None:
    text = MONSTER.read_text(encoding="utf-8")

    import_line = "import soloMapling.ArtificialPlayer.BotHelpers;\n"
    if import_line not in text:
        anchor = "import server.maps.Summon;\n"
        if anchor not in text:
            raise SystemExit("Could not locate Monster import anchor")
        text = text.replace(anchor, anchor + import_line, 1)

    marker = "!BotHelpers.isBot(chr)"
    if marker not in text:
        old = """        for (Character chr : getMap().getAllPlayers()) {
            if (!chr.isHidden()) {
                int ctrlMonsSize = chr.getNumControlledMonsters();
"""
        new = """        for (Character chr : getMap().getAllPlayers()) {
            // Headless SoloMapling characters cannot stream MoveMonster packets.
            // Never let them become automatic monster controllers.
            if (!chr.isHidden() && !BotHelpers.isBot(chr)) {
                int ctrlMonsSize = chr.getNumControlledMonsters();
"""
        if old not in text:
            raise SystemExit("Could not locate Monster controller-selection anchor")
        text = text.replace(old, new, 1)

    MONSTER.write_text(text, encoding="utf-8")
    print("SoloMapling combat hook applied (headless bots excluded from monster control).")


if __name__ == "__main__":
    main()

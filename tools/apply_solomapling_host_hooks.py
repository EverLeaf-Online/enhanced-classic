#!/usr/bin/env python3
"""Apply the minimal SoloMapling host hooks onto EverLeaf core files.

EverLeaf remains authoritative for shared Cosmic host files. This transform only
adds narrowly-scoped hooks required by SoloMapling's headless movement/runtime
systems and fails loudly if the expected EverLeaf anchors drift.
"""
from pathlib import Path


CHARACTER = Path("src/main/java/client/Character.java")
CLIENT = Path("src/main/java/client/Client.java")
FOOTHOLD = Path("src/main/java/server/maps/Foothold.java")


def insert_before_once(text: str, anchor: str, addition: str, marker: str) -> str:
    if marker in text:
        return text
    if anchor not in text:
        raise SystemExit(f"Expected host anchor not found: {anchor!r}")
    return text.replace(anchor, addition + anchor, 1)


def replace_once(text: str, old: str, new: str, marker: str) -> str:
    if marker in text:
        return text
    if old not in text:
        raise SystemExit(f"Expected host pattern not found: {old!r}")
    return text.replace(old, new, 1)


def patch_character() -> None:
    text = CHARACTER.read_text(encoding="utf-8")
    addition = """    // SoloMapling / GCMoveSystem: effective movement stats used to select\n    // the bot navigation profile without bypassing normal equipment/buff logic.\n    public int getTotalMoveSpeedStat() {\n        int total = 100;\n        for (Item item : getInventory(InventoryType.EQUIPPED)) {\n            if (item instanceof Equip equip) {\n                total += equip.getSpeed();\n            }\n        }\n        Integer speedBuff = getBuffedValue(BuffStat.SPEED);\n        if (speedBuff != null) {\n            total += speedBuff;\n        }\n        return Math.max(1, total);\n    }\n\n    public int getTotalJumpStat() {\n        int total = 100;\n        for (Item item : getInventory(InventoryType.EQUIPPED)) {\n            if (item instanceof Equip equip) {\n                total += equip.getJump();\n            }\n        }\n        Integer jumpBuff = getBuffedValue(BuffStat.JUMP);\n        if (jumpBuff != null) {\n            total += jumpBuff;\n        }\n        return Math.max(1, total);\n    }\n\n"""
    text = insert_before_once(
        text,
        "    public int getTotalDex() {\n",
        addition,
        "public int getTotalMoveSpeedStat()",
    )
    CHARACTER.write_text(text, encoding="utf-8")


def patch_client() -> None:
    text = CLIENT.read_text(encoding="utf-8")
    old = """    public synchronized void announceBossHpBar(Monster mm, final int mobHash, Packet packet) {\n        long timeNow = System.currentTimeMillis();\n"""
    new = """    public synchronized void announceBossHpBar(Monster mm, final int mobHash, Packet packet) {\n        // Headless SoloMapling clients intentionally have no bound player.\n        if (player == null) {\n            return;\n        }\n        long timeNow = System.currentTimeMillis();\n"""
    text = replace_once(text, old, new, "Headless SoloMapling clients intentionally have no bound player")
    CLIENT.write_text(text, encoding="utf-8")


def patch_foothold() -> None:
    text = FOOTHOLD.read_text(encoding="utf-8")
    text = replace_once(
        text,
        "    private int next, prev;\n",
        "    private int next, prev;\n    private boolean forbidFallDown;\n",
        "private boolean forbidFallDown;",
    )

    addition = """\n    // SoloMapling / GCMoveSystem terrain helpers.\n    public double slope() {\n        if (isWall()) {\n            return 0.0;\n        }\n        return (double) (p2.y - p1.y) / (double) (p2.x - p1.x);\n    }\n\n    public boolean isForbidFallDown() {\n        return forbidFallDown;\n    }\n\n    public void setForbidFallDown(boolean forbidFallDown) {\n        this.forbidFallDown = forbidFallDown;\n    }\n\n    public static boolean isCollidableWall(Foothold wall, java.util.Map<Integer, Foothold> footholdsById) {\n        if (wall == null || !wall.isWall()) {\n            return false;\n        }\n        Point lowerEndpoint = wall.getY1() >= wall.getY2() ? wall.p1 : wall.p2;\n        return linkedChainReachesGroundAtEndpoint(wall, wall.prev, false, lowerEndpoint, footholdsById)\n                || linkedChainReachesGroundAtEndpoint(wall, wall.next, true, lowerEndpoint, footholdsById);\n    }\n\n    private static boolean linkedChainReachesGroundAtEndpoint(\n            Foothold wall, int linkedId, boolean followNext, Point endpoint,\n            java.util.Map<Integer, Foothold> footholdsById) {\n        if (linkedId == 0) {\n            return false;\n        }\n        Foothold linked = footholdsById.get(linkedId);\n        if (linked == null || !touchesPoint(linked, endpoint)) {\n            return false;\n        }\n        return chainReachesGround(wall, followNext, footholdsById);\n    }\n\n    private static boolean chainReachesGround(\n            Foothold start, boolean followNext, java.util.Map<Integer, Foothold> footholdsById) {\n        int id = followNext ? start.next : start.prev;\n        int depth = 0;\n        while (id != 0 && depth < 10) {\n            Foothold fh = footholdsById.get(id);\n            if (fh == null) {\n                return false;\n            }\n            if (!fh.isWall()) {\n                return true;\n            }\n            id = followNext ? fh.next : fh.prev;\n            depth++;\n        }\n        return false;\n    }\n\n    private static boolean touchesPoint(Foothold foothold, Point point) {\n        return (foothold.getX1() == point.x && foothold.getY1() == point.y)\n                || (foothold.getX2() == point.x && foothold.getY2() == point.y);\n    }\n"""
    text = insert_before_once(
        text,
        "}\n",
        addition,
        "public static boolean isCollidableWall",
    )
    FOOTHOLD.write_text(text, encoding="utf-8")


def main() -> None:
    patch_character()
    patch_client()
    patch_foothold()
    print("SoloMapling host hooks applied (Character, Client, Foothold).")


if __name__ == "__main__":
    main()

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
SERVER_CONFIG = Path("src/main/java/config/ServerConfig.java")
COMMANDS_EXECUTOR = Path("src/main/java/client/command/CommandsExecutor.java")


def insert_before_once(text: str, anchor: str, addition: str, marker: str) -> str:
    if marker in text:
        return text
    if anchor not in text:
        raise SystemExit(f"Expected host anchor not found: {anchor!r}")
    return text.replace(anchor, addition + anchor, 1)


def insert_before_class_close(text: str, addition: str, marker: str) -> str:
    if marker in text:
        return text
    stripped = text.rstrip()
    if not stripped.endswith("}"):
        raise SystemExit("Expected Java class closing brace")
    close_index = text.rfind("}")
    return text[:close_index] + addition + text[close_index:]


def replace_once(text: str, old: str, new: str, marker: str) -> str:
    if marker in text:
        return text
    if old not in text:
        raise SystemExit(f"Expected host pattern not found: {old!r}")
    return text.replace(old, new, 1)


def patch_character() -> None:
    text = CHARACTER.read_text(encoding="utf-8")
    addition = """    // SoloMapling / GCMoveSystem: effective movement stats used to select
    // the bot navigation profile without bypassing normal equipment/buff logic.
    public int getTotalMoveSpeedStat() {
        int total = 100;
        for (Item item : getInventory(InventoryType.EQUIPPED)) {
            if (item instanceof Equip equip) {
                total += equip.getSpeed();
            }
        }
        Integer speedBuff = getBuffedValue(BuffStat.SPEED);
        if (speedBuff != null) {
            total += speedBuff;
        }
        return Math.max(1, total);
    }

    public int getTotalJumpStat() {
        int total = 100;
        for (Item item : getInventory(InventoryType.EQUIPPED)) {
            if (item instanceof Equip equip) {
                total += equip.getJump();
            }
        }
        Integer jumpBuff = getBuffedValue(BuffStat.JUMP);
        if (jumpBuff != null) {
            total += jumpBuff;
        }
        return Math.max(1, total);
    }

"""
    text = insert_before_once(
        text,
        "    public int getTotalDex() {\n",
        addition,
        "public int getTotalMoveSpeedStat()",
    )

    # SoloMapling clones a persisted template character, then gives the in-memory
    # headless clone a synthetic object/player id before it is registered in world,
    # channel and map storage. EverLeaf's id field is mutable but intentionally had
    # no public setter, so expose only the upstream-compatible hook required here.
    id_addition = """    // SoloMapling QA: assign the synthetic in-memory bot identity before
    // registering the cloned template character in channel/world/map storage.
    public void setID(int id) {
        this.id = id;
    }

"""
    text = insert_before_once(
        text,
        "    public boolean isLoggedinWorld() {\n",
        id_addition,
        "public void setID(int id)",
    )

    CHARACTER.write_text(text, encoding="utf-8")


def patch_client() -> None:
    text = CLIENT.read_text(encoding="utf-8")
    old = """    public synchronized void announceBossHpBar(Monster mm, final int mobHash, Packet packet) {
        long timeNow = System.currentTimeMillis();
"""
    new = """    public synchronized void announceBossHpBar(Monster mm, final int mobHash, Packet packet) {
        // Headless SoloMapling clients intentionally have no bound player.
        if (player == null) {
            return;
        }
        long timeNow = System.currentTimeMillis();
"""
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

    addition = """
    // SoloMapling / GCMoveSystem terrain helpers.
    public double slope() {
        if (isWall()) {
            return 0.0;
        }
        return (double) (p2.y - p1.y) / (double) (p2.x - p1.x);
    }

    public boolean isForbidFallDown() {
        return forbidFallDown;
    }

    public void setForbidFallDown(boolean forbidFallDown) {
        this.forbidFallDown = forbidFallDown;
    }

    public static boolean isCollidableWall(Foothold wall, java.util.Map<Integer, Foothold> footholdsById) {
        if (wall == null || !wall.isWall()) {
            return false;
        }
        Point lowerEndpoint = wall.getY1() >= wall.getY2() ? wall.p1 : wall.p2;
        return linkedChainReachesGroundAtEndpoint(wall, wall.prev, false, lowerEndpoint, footholdsById)
                || linkedChainReachesGroundAtEndpoint(wall, wall.next, true, lowerEndpoint, footholdsById);
    }

    private static boolean linkedChainReachesGroundAtEndpoint(
            Foothold wall, int linkedId, boolean followNext, Point endpoint,
            java.util.Map<Integer, Foothold> footholdsById) {
        if (linkedId == 0) {
            return false;
        }
        Foothold linked = footholdsById.get(linkedId);
        if (linked == null || !touchesPoint(linked, endpoint)) {
            return false;
        }
        return chainReachesGround(wall, followNext, footholdsById);
    }

    private static boolean chainReachesGround(
            Foothold start, boolean followNext, java.util.Map<Integer, Foothold> footholdsById) {
        int id = followNext ? start.next : start.prev;
        int depth = 0;
        while (id != 0 && depth < 10) {
            Foothold fh = footholdsById.get(id);
            if (fh == null) {
                return false;
            }
            if (!fh.isWall()) {
                return true;
            }
            id = followNext ? fh.next : fh.prev;
            depth++;
        }
        return false;
    }

    private static boolean touchesPoint(Foothold foothold, Point point) {
        return (foothold.getX1() == point.x && foothold.getY1() == point.y)
                || (foothold.getX2() == point.x && foothold.getY2() == point.y);
    }
"""
    text = insert_before_class_close(
        text,
        addition,
        "public static boolean isCollidableWall",
    )
    FOOTHOLD.write_text(text, encoding="utf-8")


def patch_server_config() -> None:
    text = SERVER_CONFIG.read_text(encoding="utf-8")
    addition = """    // SoloMapling QA: opt-in only. EverLeaf keeps automatic bot population off
    // until the isolated integration smoke suite explicitly enables it.
    public boolean SPAWN_BOTS_ON_STARTUP;

"""
    text = insert_before_once(
        text,
        "    //Server Flags\n",
        addition,
        "public boolean SPAWN_BOTS_ON_STARTUP;",
    )
    SERVER_CONFIG.write_text(text, encoding="utf-8")


def patch_commands_executor() -> None:
    text = COMMANDS_EXECUTOR.read_text(encoding="utf-8")
    addition = "        addCommand(\"qabot\", 4, QaBotCommand.class);\n"
    text = insert_before_once(
        text,
        "        addCommand(\"servermessage\", 4, ServerMessageCommand.class);\n",
        addition,
        "addCommand(\"qabot\", 4, QaBotCommand.class);",
    )
    COMMANDS_EXECUTOR.write_text(text, encoding="utf-8")


def main() -> None:
    patch_character()
    patch_client()
    patch_foothold()
    patch_server_config()
    patch_commands_executor()
    print("SoloMapling host hooks applied (Character, Client, Foothold, ServerConfig, QA command, synthetic bot id).")


if __name__ == "__main__":
    main()

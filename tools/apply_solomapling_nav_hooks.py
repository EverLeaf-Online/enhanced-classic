#!/usr/bin/env python3
"""Apply SoloMapling GCMove live-map navigation hooks onto EverLeaf.

This keeps EverLeaf's map loader/map runtime authoritative and only adds the
terrain data needed by SoloMapling: ropes/ladders, swim state, foothold speed,
and forbid-fall-down foothold flags.
"""
from pathlib import Path

MAPLE_MAP = Path("src/main/java/server/maps/MapleMap.java")
MAP_FACTORY = Path("src/main/java/server/maps/MapFactory.java")


def replace_once(text: str, old: str, new: str, marker: str) -> str:
    if marker in text:
        return text
    if old not in text:
        raise SystemExit(f"Expected navigation host pattern not found: {old!r}")
    return text.replace(old, new, 1)


def patch_maple_map() -> None:
    text = MAPLE_MAP.read_text(encoding="utf-8")
    text = replace_once(
        text,
        "    private FootholdTree footholds = null;\n",
        """    private FootholdTree footholds = null;\n    // SoloMapling / GCMoveSystem live terrain model.\n    private final List<Rope> ropes = new ArrayList<>();\n    private float footholdSpeed = 1.0f;\n    private boolean swim = false;\n""",
        "private final List<Rope> ropes",
    )

    methods = """    public void addRope(Rope rope) {\n        ropes.add(rope);\n    }\n\n    public List<Rope> getRopes() {\n        return ropes;\n    }\n\n    public float getFootholdSpeed() {\n        return footholdSpeed;\n    }\n\n    public void setFootholdSpeed(float footholdSpeed) {\n        this.footholdSpeed = footholdSpeed;\n    }\n\n    public boolean isSwim() {\n        return swim;\n    }\n\n    public void setSwim(boolean swim) {\n        this.swim = swim;\n    }\n\n"""
    text = replace_once(
        text,
        "    public void setMapPointBoundings(int px, int py, int h, int w) {\n",
        methods + "    public void setMapPointBoundings(int px, int py, int h, int w) {\n",
        "public List<Rope> getRopes()",
    )
    MAPLE_MAP.write_text(text, encoding="utf-8")


def patch_map_factory() -> None:
    text = MAP_FACTORY.read_text(encoding="utf-8")

    old = """        map.setFieldLimit(DataTool.getInt(infoData.getChildByPath(\"fieldLimit\"), 0));\n        map.setMobInterval((short) DataTool.getInt(infoData.getChildByPath(\"createMobInterval\"), 5000));\n"""
    new = old + """        // SoloMapling / GCMoveSystem terrain properties from WZ info.\n        map.setSwim(DataTool.getInt(infoData.getChildByPath(\"swim\"), 0) != 0);\n        Data footholdSpeedData = infoData.getChildByPath(\"fs\");\n        if (footholdSpeedData != null) {\n            map.setFootholdSpeed(DataTool.getFloat(footholdSpeedData));\n        }\n"""
    text = replace_once(text, old, new, "SoloMapling / GCMoveSystem terrain properties from WZ info")

    old = """                    fh.setPrev(DataTool.getInt(footHold.getChildByPath(\"prev\")));\n                    fh.setNext(DataTool.getInt(footHold.getChildByPath(\"next\")));\n"""
    new = old + """                    fh.setForbidFallDown(DataTool.getInt(footHold.getChildByPath(\"forbidFallDown\"), 0) != 0);\n"""
    text = replace_once(text, old, new, "fh.setForbidFallDown")

    old = """        map.setFootholds(fTree);\n        if (mapData.getChildByPath(\"area\") != null) {\n"""
    new = """        map.setFootholds(fTree);\n\n        Data ropeData = mapData.getChildByPath(\"ladderRope\");\n        if (ropeData != null) {\n            for (Data rope : ropeData) {\n                int rx = DataTool.getInt(rope.getChildByPath(\"x\"));\n                int ry1 = DataTool.getInt(rope.getChildByPath(\"y1\"));\n                int ry2 = DataTool.getInt(rope.getChildByPath(\"y2\"));\n                boolean ladder = DataTool.getInt(rope.getChildByPath(\"l\"), 0) == 1;\n                map.addRope(new Rope(rx, ry1, ry2, ladder));\n            }\n        }\n        if (mapData.getChildByPath(\"area\") != null) {\n"""
    text = replace_once(text, old, new, "Data ropeData = mapData.getChildByPath(\"ladderRope\")")

    MAP_FACTORY.write_text(text, encoding="utf-8")


def main() -> None:
    patch_maple_map()
    patch_map_factory()
    print("SoloMapling navigation hooks applied (MapleMap, MapFactory).")


if __name__ == "__main__":
    main()

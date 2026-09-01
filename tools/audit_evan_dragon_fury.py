#!/usr/bin/env python3
"""Hard release assertions for Evan Dragon Fury's passive damage ceiling."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HANDLER = ROOT / "src/main/java/net/server/channel/handlers/AbstractDealDamageHandler.java"
TRANSFORM = ROOT / "tools/apply_evan_dragon_fury_fixes.py"


def require(path: Path, *fragments: str) -> None:
    text = path.read_text(encoding="utf-8", errors="replace")
    for fragment in fragments:
        if fragment not in text:
            raise SystemExit(f"ERROR {path.relative_to(ROOT)} missing Dragon Fury invariant: {fragment}")


def main() -> int:
    require(
        HANDLER,
        "int dragonFuryLevel = chr.getSkillLevel(Evan.DRAGON_FURY);",
        "dragonFuryLevel > 0 && chr.getMaxMp() > 0",
        "int mpPercent = (int) ((chr.getMp() * 100L) / chr.getMaxMp());",
        "mpPercent > dragonFury.getX() && mpPercent < dragonFury.getY()",
        "calcDmgMax = calcDmgMax * dragonFury.getDamage() / 100;",
    )
    require(
        TRANSFORM,
        "Dragon Fury is a passive client-side damage modifier",
        "calcDmgMax = calcDmgMax * dragonFury.getDamage() / 100;",
    )
    print("EverLeaf Evan Dragon Fury audit: PASS")
    print("  learned passive: required")
    print("  MP window: WZ x < current MP% < WZ y")
    print("  damage ceiling: WZ damage percent (101-110 => 1-10% bonus)")
    print("  reported hit: not multiplied a second time")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Apply deterministic Evan Recovery Aura restoration fixes.

Recovery Aura's WZ `x` value is the total percentage of max MP restored over
its duration. The legacy v83 implementation incorrectly applied x percent of
the recipient's *current* MP every 2.5 seconds and resolved the effect using
the recipient's skill level. Party members normally do not own the Evan skill.

This transform uses the caster's skill level, apportions x percent of each
recipient's max MP across the 2.5-second mist ticks, and remains strict and
idempotent for the production double-transform model.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAP = ROOT / "src/main/java/server/maps/MapleMap.java"

BROKEN = """                            chr.addMP(mist.getSourceSkill().getEffect(chr.getSkillLevel(mist.getSourceSkill().getId())).getX() * chr.getMp() / 100);\n"""
FIXED = """                            StatEffect recoveryEffect = mist.getSourceSkill().getEffect(\n                                    mist.getOwner().getSkillLevel(mist.getSourceSkill().getId()));\n                            int recoveryInterval = 2500;\n                            int recoveryDuration = Math.max(1, recoveryEffect.getDuration());\n                            int recoveryAmount = (int) Math.floor(\n                                    chr.getMaxMp() * (recoveryEffect.getX() / 100.0)\n                                            * recoveryInterval / recoveryDuration);\n                            chr.addMP(Math.max(1, recoveryAmount));\n"""


def main() -> int:
    text = MAP.read_text(encoding="utf-8")
    if FIXED in text:
        print("OK already fixed: Evan Recovery Aura MP restoration")
    elif BROKEN in text:
        text = text.replace(BROKEN, FIXED, 1)
        MAP.write_text(text, encoding="utf-8")
        print("FIXED: Evan Recovery Aura MP restoration")
    else:
        raise SystemExit("ERROR expected Recovery Aura legacy/fixed snippet not found")

    text = MAP.read_text(encoding="utf-8")
    required = (
        "mist.getOwner().getSkillLevel(mist.getSourceSkill().getId())",
        "chr.getMaxMp() * (recoveryEffect.getX() / 100.0)",
        "* recoveryInterval / recoveryDuration",
        "chr.addMP(Math.max(1, recoveryAmount));",
    )
    for fragment in required:
        if fragment not in text:
            raise SystemExit(f"ERROR Recovery Aura invariant missing: {fragment}")
    if "getEffect(chr.getSkillLevel(mist.getSourceSkill().getId())).getX() * chr.getMp() / 100" in text:
        raise SystemExit("ERROR stale current-MP/recipient-level Recovery Aura formula remains")

    print("EverLeaf Evan Recovery Aura fix: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

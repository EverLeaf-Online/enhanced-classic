#!/usr/bin/env python3
"""Apply the Evan Dragon Fury magic-damage validation fix.

Dragon Fury is a passive client-side damage modifier. The client reports the
boosted hit, so the server must raise its legitimate magic-damage ceiling while
the character's MP percentage is inside the WZ-defined x/y range. Multiplying
the reported hit again would double-apply the passive.

The transform is strict and idempotent and is intentionally kept separate from
the older Evan behavior transform so production's repeated transform pass can
verify it independently.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "src/main/java/net/server/channel/handlers/AbstractDealDamageHandler.java"

BROKEN = """                } else if (chr.getJob() == Job.EVAN7 || chr.getJob() == Job.EVAN8 || chr.getJob() == Job.EVAN9 || chr.getJob() == Job.EVAN10) {\n                    int skillLvl = chr.getSkillLevel(Evan.MAGIC_AMPLIFICATION);\n                    if (skillLvl > 0) {\n                        calcDmgMax = calcDmgMax * SkillFactory.getSkill(Evan.MAGIC_AMPLIFICATION).getEffect(skillLvl).getY() / 100;\n                    }\n                }\n\n                calcDmgMax *= effect.getMatk();\n"""

FIXED = """                } else if (chr.getJob() == Job.EVAN7 || chr.getJob() == Job.EVAN8 || chr.getJob() == Job.EVAN9 || chr.getJob() == Job.EVAN10) {\n                    int skillLvl = chr.getSkillLevel(Evan.MAGIC_AMPLIFICATION);\n                    if (skillLvl > 0) {\n                        calcDmgMax = calcDmgMax * SkillFactory.getSkill(Evan.MAGIC_AMPLIFICATION).getEffect(skillLvl).getY() / 100;\n                    }\n                }\n\n                int dragonFuryLevel = chr.getSkillLevel(Evan.DRAGON_FURY);\n                if (dragonFuryLevel > 0 && chr.getMaxMp() > 0) {\n                    StatEffect dragonFury = SkillFactory.getSkill(Evan.DRAGON_FURY).getEffect(dragonFuryLevel);\n                    int mpPercent = (int) ((chr.getMp() * 100L) / chr.getMaxMp());\n                    if (mpPercent > dragonFury.getX() && mpPercent < dragonFury.getY()) {\n                        calcDmgMax = calcDmgMax * dragonFury.getDamage() / 100;\n                    }\n                }\n\n                calcDmgMax *= effect.getMatk();\n"""


def main() -> int:
    text = TARGET.read_text(encoding="utf-8")
    if FIXED in text:
        print("OK already fixed: Evan Dragon Fury damage validation")
    elif BROKEN in text:
        TARGET.write_text(text.replace(BROKEN, FIXED, 1), encoding="utf-8")
        print("FIXED: Evan Dragon Fury damage validation")
    else:
        raise SystemExit("ERROR expected Evan Dragon Fury validation anchor not found")

    result = TARGET.read_text(encoding="utf-8")
    required = (
        "int dragonFuryLevel = chr.getSkillLevel(Evan.DRAGON_FURY);",
        "int mpPercent = (int) ((chr.getMp() * 100L) / chr.getMaxMp());",
        "mpPercent > dragonFury.getX() && mpPercent < dragonFury.getY()",
        "calcDmgMax = calcDmgMax * dragonFury.getDamage() / 100;",
    )
    for fragment in required:
        if fragment not in result:
            raise SystemExit(f"ERROR missing Evan Dragon Fury invariant: {fragment}")

    print("EverLeaf Evan Dragon Fury fix: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Apply Enhanced Classic source changes deterministically.

This is an interim build transform while the fork is being separated from
upstream Cosmic. It is intentionally idempotent and fails loudly when the
expected upstream source shape changes.
"""
from pathlib import Path


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if new in text:
        return
    if old not in text:
        raise SystemExit(f"Expected source pattern not found in {path}: {old!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


character = Path("src/main/java/client/Character.java")
replace_once(
    character,
    "return isCygnus() ? 120 : 200;",
    "return service.enhanced.LevelCapPolicy.maxLevel(job);",
)

# Add a Character-owned permanent MaxHP floor mutation. Keeping the raw
# protected setMaxHp call inside Character avoids touching hpMpApUsed and also
# makes login migration safe before the normal stat listener/update flow exists.
replace_once(
    character,
    "    public int getMaxClassLevel() {",
    """    public int applyEnhancedPermanentMaxHpFloor(int targetMaxHp) {\n        int clampedTarget = Math.min(30000, Math.max(getMaxHp(), targetMaxHp));\n        int increase = clampedTarget - getMaxHp();\n        if (increase > 0) {\n            setMaxHp(clampedTarget);\n        }\n        return increase;\n    }\n\n    public int getMaxClassLevel() {""",
)

# Apply the no-wash survivability floor after the character's new level is
# finalized, but before local stats are recalculated and sent to the client.
replace_once(
    character,
    "        levelUpGainSp();",
    """        new service.enhanced.SurvivabilityService().applyCurrentFloor(this);\n\n        levelUpGainSp();""",
)

# Existing characters are migrated on load. The dedicated Character mutation
# does not consume AP or depend on the normal announced-stat update path.
replace_once(
    character,
    "            ret.autoban = new AutobanManager(ret);",
    """            ret.autoban = new AutobanManager(ret);\n            new service.enhanced.SurvivabilityService().applyCurrentFloor(ret);""",
)

exp_table = Path("src/main/java/constants/game/ExpTable.java")
replace_once(
    exp_table,
    "return level > 200 ? 2000000000 : exp[level];",
    """if (level <= 200) {\n            return exp[level];\n        }\n        if (level < 250) {\n            // Smooth post-200 curve: 1.70b at 201, approaching 2.0b at 249.\n            return Math.min(2_000_000_000, 1_700_000_000 + ((level - 201) * 6_250_000));\n        }\n        return Integer.MAX_VALUE;""",
)

print("Enhanced Classic level cap + survivability patch applied (250).")

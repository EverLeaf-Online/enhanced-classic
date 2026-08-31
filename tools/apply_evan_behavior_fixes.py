#!/usr/bin/env python3
"""Apply deterministic Evan server behavior fixes.

This transform fixes two legacy switch fallthroughs in StatEffect:
- Evan.SLOW must not also register SOULARROW.
- Evan.PHANTOM_IMPRINT must not also register ARAN_COMBO.

The transform is intentionally strict and idempotent. If upstream source changes
so the expected legacy snippets are no longer present, it verifies the fixed
form instead of silently rewriting unrelated code.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "src/main/java/server/StatEffect.java"

FIXES = (
    (
        """                case Evan.SLOW:\n                    statups.add(new Pair<>(BuffStat.SLOW, x));\n                    // BOWMAN\n                case Priest.MYSTIC_DOOR:\n""",
        """                case Evan.SLOW:\n                    statups.add(new Pair<>(BuffStat.SLOW, x));\n                    break;\n                    // BOWMAN\n                case Priest.MYSTIC_DOOR:\n""",
        "Evan Slow -> Soul Arrow fallthrough",
    ),
    (
        """                case Evan.PHANTOM_IMPRINT:\n                    monsterStatus.put(MonsterStatus.PHANTOM_IMPRINT, x);\n                    //ARAN\n                case Aran.COMBO_ABILITY:\n""",
        """                case Evan.PHANTOM_IMPRINT:\n                    monsterStatus.put(MonsterStatus.PHANTOM_IMPRINT, x);\n                    break;\n                    //ARAN\n                case Aran.COMBO_ABILITY:\n""",
        "Evan Phantom Imprint -> Aran Combo fallthrough",
    ),
)


def main() -> int:
    text = TARGET.read_text(encoding="utf-8")
    changed = False

    for broken, fixed, label in FIXES:
        if fixed in text:
            print(f"OK already fixed: {label}")
            continue
        if broken not in text:
            raise SystemExit(f"ERROR expected Evan behavior snippet not found: {label}")
        text = text.replace(broken, fixed, 1)
        changed = True
        print(f"FIXED: {label}")

    if changed:
        TARGET.write_text(text, encoding="utf-8")

    # Hard verification after mutation.
    for _broken, fixed, label in FIXES:
        if fixed not in text:
            raise SystemExit(f"ERROR Evan behavior fix did not apply: {label}")

    print("EverLeaf Evan behavior fixes: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

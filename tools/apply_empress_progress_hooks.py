#!/usr/bin/env python3
"""Apply EverLeaf Knight Stronghold kill-progress hooks to MapleMap.java.

The repository keeps invasive source edits as deterministic build transforms so
upstream-friendly source files remain easy to compare. This transform is
idempotent and only records Advanced Knight A-E kills while Empress content is
explicitly enabled.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "src/main/java/server/maps/MapleMap.java"

IMPORT_ANCHOR = "import config.YamlConfig;\n"
IMPORTS = (
    "import everleaf.content.EmpressContentPolicy;\n"
    "import everleaf.content.EmpressStrongholdProgressService;\n"
)

KILL_ANCHOR = "            Character dropOwner = monster.killBy(chr);\n"
HOOK = """            Character dropOwner = monster.killBy(chr);

            // EverLeaf Knight Stronghold prerequisite: one kill of each
            // Advanced Knight A-E unlocks the Empress expedition for the
            // character. The feature gate keeps this inert until the complete
            // client/server content package is ready.
            if (EmpressContentPolicy.isEnabled()
                    && getId() >= 271030000 && getId() <= 271030600
                    && monster.getId() >= EmpressStrongholdProgressService.FIRST_ADVANCED_KNIGHT
                    && monster.getId() <= EmpressStrongholdProgressService.LAST_ADVANCED_KNIGHT) {
                boolean newlyCompleted = EmpressStrongholdProgressService.recordAdvancedKnightKill(chr.getId(), monster.getId());
                if (newlyCompleted) {
                    chr.dropMessage(5, "[Knight Stronghold] You have defeated all five Advanced Knights. Empress Cygnus is now unlocked for this character.");
                }
            }
"""


def main() -> int:
    text = PATH.read_text(encoding="utf-8-sig")

    if "import everleaf.content.EmpressContentPolicy;" not in text:
        if IMPORT_ANCHOR not in text:
            raise SystemExit("MapleMap import anchor not found")
        text = text.replace(IMPORT_ANCHOR, IMPORT_ANCHOR + IMPORTS, 1)

    if "EmpressStrongholdProgressService.recordAdvancedKnightKill" not in text:
        if KILL_ANCHOR not in text:
            raise SystemExit("MapleMap kill anchor not found")
        text = text.replace(KILL_ANCHOR, HOOK, 1)

    PATH.write_text(text, encoding="utf-8")
    print("EverLeaf Empress Stronghold kill-progress hooks applied.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

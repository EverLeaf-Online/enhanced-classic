#!/usr/bin/env python3
"""Apply EverLeaf gameplay-integrity fixes deterministically.

The transform closes concrete release gaps found during the September 2026
progression/combat review while keeping upstream-comparison source easy to audit:

* EverLeaf survivability floors replace new HP washing. Fresh AP and AP Resets may
  not add points to HP/MP; legacy HP/MP AP can still be reset back into core stats.
* SP Reset packets validate the source skill before dereferencing/moving it.
* Ranged packet handling fails closed when no weapon is equipped.
* Aran High Defense uses the WZ per-mille multiplier directly instead of ceil(),
  which previously rounded every sub-1000 reduction multiplier back to 1.0.
"""
from pathlib import Path


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if new in text:
        return
    if old not in text:
        raise SystemExit(f"Expected gameplay-integrity pattern not found in {path}: {old!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def main() -> None:
    ap = Path("src/main/java/client/processor/stat/AssignAPProcessor.java")
    cash = Path("src/main/java/net/server/channel/handlers/UseCashItemHandler.java")
    ranged = Path("src/main/java/net/server/channel/handlers/RangedAttackHandler.java")
    damage = Path("src/main/java/net/server/channel/handlers/TakeDamageHandler.java")

    replace_once(
        ap,
        """    public static void APAssignAction(Client c, int num) {\n        c.lockClient();\n        try {\n            addStat(c.getPlayer(), num, false);""",
        """    public static void APAssignAction(Client c, int num) {\n        c.lockClient();\n        try {\n            Character player = c.getPlayer();\n            if (num == 2048 || num == 8192) {\n                player.message(\"EverLeaf survivability progression replaces HP washing. Assign AP to your core stats instead.\");\n                c.sendPacket(PacketCreator.enableActions());\n                return;\n            }\n            addStat(player, num, false);""",
    )

    replace_once(
        ap,
        """    public static boolean APResetAction(Client c, int APFrom, int APTo) {\n        c.lockClient();\n        try {\n            Character player = c.getPlayer();""",
        """    public static boolean APResetAction(Client c, int APFrom, int APTo) {\n        c.lockClient();\n        try {\n            Character player = c.getPlayer();\n            if (APTo == 2048 || APTo == 8192) {\n                player.message(\"EverLeaf survivability progression replaces HP washing. AP Resets cannot add points to HP or MP.\");\n                c.sendPacket(PacketCreator.enableActions());\n                return false;\n            }""",
    )

    replace_once(
        cash,
        """                int SPFrom = p.readInt();\n                Skill skillSPTo = SkillFactory.getSkill(SPTo);\n                Skill skillSPFrom = SkillFactory.getSkill(SPFrom);""",
        """                int SPFrom = p.readInt();\n                if (!AssignSPProcessor.canSPAssign(c, SPFrom)) {\n                    return;\n                }\n                Skill skillSPTo = SkillFactory.getSkill(SPTo);\n                Skill skillSPFrom = SkillFactory.getSkill(SPFrom);""",
    )

    replace_once(
        ranged,
        """            Item weapon = chr.getInventory(InventoryType.EQUIPPED).getItem((short) -11);\n            WeaponType type = ItemInformationProvider.getInstance().getWeaponType(weapon.getItemId());""",
        """            Item weapon = chr.getInventory(InventoryType.EQUIPPED).getItem((short) -11);\n            if (weapon == null) {\n                return;\n            }\n            WeaponType type = ItemInformationProvider.getInstance().getWeaponType(weapon.getItemId());""",
    )

    replace_once(
        damage,
        """                    damage *= Math.ceil(highDef.getEffect(hdLevel).getX() / 1000.0);""",
        """                    damage *= (highDef.getEffect(hdLevel).getX() / 1000.0);""",
    )

    print("EverLeaf gameplay integrity fixes: PASS")
    print("  new HP/MP AP investment: blocked")
    print("  AP Reset targets HP/MP: blocked; legacy HP/MP can be unwound to core stats")
    print("  SP Reset source skill validation: enforced")
    print("  ranged attacks without weapon: fail closed")
    print("  Aran High Defense: WZ per-mille multiplier applied without ceil rounding")


if __name__ == "__main__":
    main()

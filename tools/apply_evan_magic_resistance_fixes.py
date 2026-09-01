#!/usr/bin/env python3
"""Apply Evan Magic Resistance incoming-damage support.

The v83 Mob.wz attack records explicitly mark magical attacks with `magic=1`.
EverLeaf previously discarded that field, so Evan Magic Resistance could be
registered as a party buff while its WZ x-percent reduction was never consumed.

This transform preserves the attack-type bit in MobAttackInfo and applies the
buff only to magical mob attacks before Magic Shield / Magic Guard settlement.
It is strict and idempotent.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ATTACK_INFO = ROOT / "src/main/java/server/life/MobAttackInfo.java"
ATTACK_FACTORY = ROOT / "src/main/java/server/life/MobAttackInfoFactory.java"
TAKE_DAMAGE = ROOT / "src/main/java/net/server/channel/handlers/TakeDamageHandler.java"


def replace_known(path: Path, broken: str, fixed: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if fixed in text:
        print(f"OK already fixed: {label}")
        return
    if broken not in text:
        raise SystemExit(f"ERROR expected Evan Magic Resistance anchor not found: {label}")
    path.write_text(text.replace(broken, fixed, 1), encoding="utf-8")
    print(f"FIXED: {label}")


def patch_attack_info() -> None:
    replace_known(
        ATTACK_INFO,
        """    private int diseaseLevel;\n    private int mpCon;\n""",
        """    private int diseaseLevel;\n    private int mpCon;\n    private boolean magicAttack;\n""",
        "MobAttackInfo magic flag storage",
    )
    replace_known(
        ATTACK_INFO,
        """    public int getMpCon() {\n        return mpCon;\n    }\n}\n""",
        """    public int getMpCon() {\n        return mpCon;\n    }\n\n    public void setMagicAttack(boolean magicAttack) {\n        this.magicAttack = magicAttack;\n    }\n\n    public boolean isMagicAttack() {\n        return magicAttack;\n    }\n}\n""",
        "MobAttackInfo magic flag accessors",
    )


def patch_attack_factory() -> None:
    replace_known(
        ATTACK_FACTORY,
        """                    int disease = DataTool.getInt(\"disease\", attackData, 0);\n                    int level = DataTool.getInt(\"level\", attackData, 0);\n                    int mpCon = DataTool.getInt(\"conMP\", attackData, 0);\n                    ret = new MobAttackInfo(mob.getId(), attack);\n""",
        """                    int disease = DataTool.getInt(\"disease\", attackData, 0);\n                    int level = DataTool.getInt(\"level\", attackData, 0);\n                    int mpCon = DataTool.getInt(\"conMP\", attackData, 0);\n                    boolean magicAttack = DataTool.getInt(\"magic\", attackData, 0) == 1;\n                    ret = new MobAttackInfo(mob.getId(), attack);\n""",
        "MobAttackInfoFactory reads Mob.wz magic flag",
    )
    replace_known(
        ATTACK_FACTORY,
        """                    ret.setDiseaseLevel(level);\n                    ret.setMpCon(mpCon);\n""",
        """                    ret.setDiseaseLevel(level);\n                    ret.setMpCon(mpCon);\n                    ret.setMagicAttack(magicAttack);\n""",
        "MobAttackInfoFactory stores Mob.wz magic flag",
    )


def patch_take_damage() -> None:
    replace_known(
        TAKE_DAMAGE,
        """        boolean is_pgmr = false, is_pg = true, is_deadly = false;\n        int mpattack = 0;\n        Monster attacker = null;\n""",
        """        boolean is_pgmr = false, is_pg = true, is_deadly = false;\n        int mpattack = 0;\n        boolean isMagicAttack = false;\n        Monster attacker = null;\n""",
        "TakeDamage tracks magical mob attack",
    )
    replace_known(
        TAKE_DAMAGE,
        """            MobAttackInfo attackInfo = MobAttackInfoFactory.getMobAttackInfo(attacker, damagefrom);\n            if (attackInfo != null) {\n                if (attackInfo.isDeadlyAttack()) {\n""",
        """            MobAttackInfo attackInfo = MobAttackInfoFactory.getMobAttackInfo(attacker, damagefrom);\n            if (attackInfo != null) {\n                isMagicAttack = attackInfo.isMagicAttack();\n                if (attackInfo.isDeadlyAttack()) {\n""",
        "TakeDamage consumes MobAttackInfo magic flag",
    )
    replace_known(
        TAKE_DAMAGE,
        """            Integer magicShield = chr.getBuffedValue(BuffStat.MAGIC_SHIELD);\n            if (magicShield != null) {\n""",
        """            Integer magicResistance = chr.getBuffedValue(BuffStat.MAGIC_RESISTANCE);\n            if (isMagicAttack && magicResistance != null) {\n                int reductionPercent = Math.max(0, Math.min(100, magicResistance));\n                damage = Math.max(0, damage - (int) Math.floor(damage * (reductionPercent / 100.0)));\n            }\n\n            Integer magicShield = chr.getBuffedValue(BuffStat.MAGIC_SHIELD);\n            if (magicShield != null) {\n""",
        "Evan Magic Resistance damage reduction",
    )


def main() -> int:
    patch_attack_info()
    patch_attack_factory()
    patch_take_damage()

    checks = {
        ATTACK_INFO: (
            "private boolean magicAttack;",
            "public boolean isMagicAttack()",
        ),
        ATTACK_FACTORY: (
            'DataTool.getInt("magic", attackData, 0) == 1',
            "ret.setMagicAttack(magicAttack);",
        ),
        TAKE_DAMAGE: (
            "isMagicAttack = attackInfo.isMagicAttack();",
            "Integer magicResistance = chr.getBuffedValue(BuffStat.MAGIC_RESISTANCE);",
            "if (isMagicAttack && magicResistance != null)",
            "damage = Math.max(0, damage - (int) Math.floor(damage * (reductionPercent / 100.0)));",
        ),
    }
    for path, fragments in checks.items():
        text = path.read_text(encoding="utf-8")
        for fragment in fragments:
            if fragment not in text:
                raise SystemExit(f"ERROR {path.relative_to(ROOT)} missing Magic Resistance invariant: {fragment}")

    print("EverLeaf Evan Magic Resistance fix: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

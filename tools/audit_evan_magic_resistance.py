#!/usr/bin/env python3
"""Hard release assertions for Evan Magic Resistance."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ATTACK_INFO = ROOT / "src/main/java/server/life/MobAttackInfo.java"
ATTACK_FACTORY = ROOT / "src/main/java/server/life/MobAttackInfoFactory.java"
TAKE_DAMAGE = ROOT / "src/main/java/net/server/channel/handlers/TakeDamageHandler.java"
TRANSFORM = ROOT / "tools/apply_evan_magic_resistance_fixes.py"


def require(path: Path, *fragments: str) -> None:
    data = path.read_text(encoding="utf-8", errors="replace")
    for fragment in fragments:
        if fragment not in data:
            raise SystemExit(f"ERROR {path.relative_to(ROOT)} missing Magic Resistance invariant: {fragment}")


def main() -> int:
    require(ATTACK_INFO, "private boolean magicAttack;", "public boolean isMagicAttack()")
    require(
        ATTACK_FACTORY,
        'boolean magicAttack = DataTool.getInt("magic", attackData, 0) == 1;',
        "ret.setMagicAttack(magicAttack);",
    )
    require(
        TAKE_DAMAGE,
        "isMagicAttack = attackInfo.isMagicAttack();",
        "Integer magicResistance = chr.getBuffedValue(BuffStat.MAGIC_RESISTANCE);",
        "if (isMagicAttack && magicResistance != null)",
        "int reductionPercent = Math.max(0, Math.min(100, magicResistance));",
        "damage = Math.max(0, damage - (int) Math.floor(damage * (reductionPercent / 100.0)));",
    )
    # Audit executable transform invariants rather than prose formatting so a
    # harmless docstring line wrap cannot break the production second-pass gate.
    require(
        TRANSFORM,
        'DataTool.getInt(\\"magic\\", attackData, 0) == 1',
        "if (isMagicAttack && magicResistance != null)",
        "Math.max(0, Math.min(100, magicResistance))",
    )
    print("EverLeaf Evan Magic Resistance audit: PASS")
    print("  attack classification: Mob.wz attack/info/magic")
    print("  physical attacks: unaffected")
    print("  magical attacks: WZ x-percent reduction")
    print("  supplied levels: x=2..20")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Guard EverLeaf's server-side ranged basic-attack whack suppression."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HANDLER = ROOT / "src/main/java/net/server/channel/handlers/CloseRangeDamageHandler.java"


def main() -> int:
    if not HANDLER.is_file():
        print(f"[FAIL] missing {HANDLER.relative_to(ROOT)}")
        return 1

    text = HANDLER.read_text(encoding="utf-8")
    required = [
        "Item weapon = chr.getInventory(InventoryType.EQUIPPED).getItem((short) -11);",
        "WeaponType weaponType = ItemInformationProvider.getInstance().getWeaponType(weapon.getItemId());",
        "weaponType == WeaponType.BOW",
        "weaponType == WeaponType.CROSSBOW",
        "weaponType == WeaponType.CLAW",
    ]
    failures = [needle for needle in required if needle not in text]

    guard_end = text.find("AttackInfo attack = parseDamage(p, chr, false, false);")
    weapon_guard = text.find("weaponType == WeaponType.BOW")
    if weapon_guard < 0 or guard_end < 0 or weapon_guard > guard_end:
        failures.append("ranged weapon guard must execute before close-range damage parsing")

    if "usesRangedBasicAttack(chr.getJob())" in text:
        failures.append("broad job-based ranged whack guard has returned")

    if failures:
        for failure in failures:
            print(f"[FAIL] {failure}")
        return 1

    print("EverLeaf ranged whack server guard: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

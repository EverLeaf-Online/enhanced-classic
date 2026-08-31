#!/usr/bin/env python3
"""Apply deterministic Evan server behavior fixes.

Covers legacy Evan defects that otherwise compile cleanly:
- Slow must not fall through into Soul Arrow.
- Phantom Imprint must not fall through into Aran Combo.
- Evan temporary-stat masks must occupy their v83/v88 third-mask slots without
  colliding with Elemental Reset or Wind Walk.
- Soul Stone must register a temporary stat and revive the protected character
  once on death.
- Killer Wings must reuse the existing Homing Beacon target-lock machinery.

The transform is strict and idempotent: it only accepts the known legacy or
known-fixed forms and fails closed if upstream source drifts.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAT_EFFECT = ROOT / "src/main/java/server/StatEffect.java"
BUFF_STAT = ROOT / "src/main/java/client/BuffStat.java"
CHARACTER = ROOT / "src/main/java/client/Character.java"
ATTACK_HANDLER = ROOT / "src/main/java/net/server/channel/handlers/AbstractDealDamageHandler.java"


def replace_known(text: str, broken: str, fixed: str, label: str) -> tuple[str, bool]:
    if fixed in text:
        print(f"OK already fixed: {label}")
        return text, False
    if broken not in text:
        raise SystemExit(f"ERROR expected Evan snippet not found: {label}")
    print(f"FIXED: {label}")
    return text.replace(broken, fixed, 1), True


def patch_stat_effect() -> None:
    text = STAT_EFFECT.read_text(encoding="utf-8")
    changed = False

    fixes = (
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
        (
            """                case Evan.MAGIC_RESISTANCE:\n                    statups.add(new Pair<>(BuffStat.MAGIC_RESISTANCE, x));\n                    break;\n                case Evan.SLOW:\n""",
            """                case Evan.MAGIC_RESISTANCE:\n                    statups.add(new Pair<>(BuffStat.MAGIC_RESISTANCE, x));\n                    break;\n                case Evan.SOUL_STONE:\n                    statups.add(new Pair<>(BuffStat.SOUL_STONE, x));\n                    break;\n                case Evan.SLOW:\n""",
            "Evan Soul Stone temporary-stat registration",
        ),
        (
            """                case Outlaw.HOMING_BEACON:\n                case Corsair.BULLSEYE:\n                    statups.add(new Pair<>(BuffStat.HOMING_BEACON, x));\n""",
            """                case Outlaw.HOMING_BEACON:\n                case Corsair.BULLSEYE:\n                case Evan.KILLER_WINGS:\n                    statups.add(new Pair<>(BuffStat.HOMING_BEACON, x));\n""",
            "Evan Killer Wings homing temporary-stat registration",
        ),
    )

    for broken, fixed, label in fixes:
        text, did_change = replace_known(text, broken, fixed, label)
        changed |= did_change

    if changed:
        STAT_EFFECT.write_text(text, encoding="utf-8")

    for _broken, fixed, label in fixes:
        if fixed not in text:
            raise SystemExit(f"ERROR Evan StatEffect fix did not apply: {label}")


def patch_buff_stat() -> None:
    text = BUFF_STAT.read_text(encoding="utf-8")
    broken = """    //all incorrect buffstats\n    SLOW(0x200000000L, true),\n    ELEMENTAL_RESET(0x200000000L, true),\n    MAGIC_SHIELD(0x400000000L, true),\n    MAGIC_RESISTANCE(0x800000000L, true),\n    // needs Soul Stone\n    //end incorrect buffstats\n\n    WIND_WALK(0x400000000L, true),\n"""
    fixed = """    // Third temporary-stat mask. The enum stores this mask shifted into\n    // the high 32 bits of the first 64-bit mask (matching the existing Aran stats).\n    ELEMENTAL_RESET(0x200000000L, true),\n    WIND_WALK(0x400000000L, true),\n    SLOW(0x400000000000L, true),\n    MAGIC_SHIELD(0x800000000000L, true),\n    MAGIC_RESISTANCE(0x1000000000000L, true),\n    SOUL_STONE(0x2000000000000L, true),\n"""
    text, changed = replace_known(text, broken, fixed, "Evan temporary-stat masks + Soul Stone")
    if changed:
        BUFF_STAT.write_text(text, encoding="utf-8")

    required = {
        "ELEMENTAL_RESET": "0x200000000L",
        "WIND_WALK": "0x400000000L",
        "SLOW": "0x400000000000L",
        "MAGIC_SHIELD": "0x800000000000L",
        "MAGIC_RESISTANCE": "0x1000000000000L",
        "SOUL_STONE": "0x2000000000000L",
    }
    for name, value in required.items():
        if f"{name}({value}, true)" not in text:
            raise SystemExit(f"ERROR Evan buff mask missing/wrong: {name}")

    forbidden = (
        "SLOW(0x200000000L, true)",
        "MAGIC_SHIELD(0x400000000L, true)",
        "MAGIC_RESISTANCE(0x800000000L, true)",
    )
    for fragment in forbidden:
        if fragment in text:
            raise SystemExit(f"ERROR stale colliding Evan buff mask remains: {fragment}")


def patch_character_death() -> None:
    text = CHARACTER.read_text(encoding="utf-8")
    marker = """    private void playerDead() {\n        if (this.getMap().isCPQMap()) {\n"""
    fixed = """    private void playerDead() {\n        StatEffect soulStone = getStatForBuff(BuffStat.SOUL_STONE);\n        if (soulStone != null) {\n            cancelEffectFromBuffStat(BuffStat.SOUL_STONE);\n            int revivePercent = Math.max(1, soulStone.getX());\n            int reviveHp = Math.max(1, (getCurrentMaxHp() * revivePercent) / 100);\n            updateHp(reviveHp);\n            setStance(0);\n            sendPacket(PacketCreator.enableActions());\n            dropMessage(5, \"Soul Stone revived you.\");\n            return;\n        }\n\n        if (this.getMap().isCPQMap()) {\n"""
    text, changed = replace_known(text, marker, fixed, "Evan Soul Stone death interception")
    if changed:
        CHARACTER.write_text(text, encoding="utf-8")
    if fixed not in text:
        raise SystemExit("ERROR Soul Stone death interception did not apply")


def patch_killer_wings_attack() -> None:
    text = ATTACK_HANDLER.read_text(encoding="utf-8")
    broken = """                    } else if (attack.skill == Outlaw.HOMING_BEACON || attack.skill == Corsair.BULLSEYE) {\n                        StatEffect beacon = SkillFactory.getSkill(attack.skill).getEffect(player.getSkillLevel(attack.skill));\n                        beacon.applyBeaconBuff(player, monster.getObjectId());\n"""
    fixed = """                    } else if (attack.skill == Outlaw.HOMING_BEACON || attack.skill == Corsair.BULLSEYE || attack.skill == Evan.KILLER_WINGS) {\n                        StatEffect beacon = SkillFactory.getSkill(attack.skill).getEffect(player.getSkillLevel(attack.skill));\n                        beacon.applyBeaconBuff(player, monster.getObjectId());\n"""
    text, changed = replace_known(text, broken, fixed, "Evan Killer Wings target lock")
    if changed:
        ATTACK_HANDLER.write_text(text, encoding="utf-8")
    if fixed not in text:
        raise SystemExit("ERROR Killer Wings attack target-lock fix did not apply")


def main() -> int:
    patch_stat_effect()
    patch_buff_stat()
    patch_character_death()
    patch_killer_wings_attack()
    print("EverLeaf Evan behavior fixes: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

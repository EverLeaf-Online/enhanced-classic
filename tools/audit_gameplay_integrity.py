#!/usr/bin/env python3
"""Fail-closed structural audit for EverLeaf progression, survivability and combat.

This gate does not pretend to replace packaged-client/live soak testing. It closes
release-time wiring gaps that can be proven from source/WZ/DB contracts and keeps
remaining work limited to runtime feel/balance verification.
"""
from __future__ import annotations

import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(rel: str) -> str:
    path = ROOT / rel
    if not path.is_file():
        raise AssertionError(f"missing required file: {rel}")
    return path.read_text(encoding="utf-8", errors="replace")


def require(rel: str, *tokens: str) -> None:
    text = read(rel)
    for token in tokens:
        if token not in text:
            raise AssertionError(f"{rel} missing required gameplay token: {token!r}")


def audit_progression() -> None:
    require(
        "src/main/java/constants/game/ExpTable.java",
        "if (level <= 200)",
        "if (level < 250)",
        "1_700_000_000",
        "6_250_000",
        "2_000_000_000",
        "return Integer.MAX_VALUE;",
    )
    require(
        "src/main/java/service/enhanced/LevelCapPolicy.java",
        "PLAYER_MAX_LEVEL",
        "250",
    )
    require(
        "src/main/java/everleaf/progression/JdbcWeeklyProgressRepository.java",
        "connection.setAutoCommit(false)",
        "FOR UPDATE",
        "already_claimed",
        "account_budget_exhausted",
        "creditVerdantMarks",
        "insertVerdantLedger",
        "markClaimed",
        "connection.commit()",
        "connection.rollback()",
    )
    require(
        "src/main/java/everleaf/progression/JdbcVerdantMarkRepository.java",
        "FOR UPDATE",
        "everleaf_verdant_mark_balance",
        "everleaf_verdant_mark_ledger",
        "Math.addExact",
        "connection.commit()",
        "connection.rollback()",
    )

    # The selected curve is monotonic and remains in signed-int range through 249.
    curve = [1_700_000_000 + ((level - 201) * 6_250_000) for level in range(201, 250)]
    assert curve[0] == 1_700_000_000
    assert curve[-1] == 2_000_000_000
    assert all(a < b for a, b in zip(curve, curve[1:]))
    assert max(curve) <= 2_000_000_000


def audit_survivability_and_resets() -> None:
    require(
        "src/main/java/service/enhanced/SurvivabilityPolicy.java",
        "enum Archetype",
        "WARRIOR",
        "BRAWLER",
        "RANGED",
        "MAGICIAN",
        "BEGINNER",
        "Math.max(0, minimumMaxHp(job, level) - currentMaxHp)",
        "case 10 -> 25000",
        "default -> 27000",
        "default -> 20000",
        "default -> 12500",
        "default -> 10000",
        "default -> 10500",
    )
    require(
        "src/main/java/service/enhanced/SurvivabilityService.java",
        "if (increase <= 0)",
        "applyEnhancedPermanentMaxHpFloor",
    )
    require(
        "src/main/java/client/processor/stat/AssignAPProcessor.java",
        "EverLeaf survivability progression replaces HP washing",
        "if (num == 2048 || num == 8192)",
        "if (APTo == 2048 || APTo == 8192)",
    )
    require(
        "src/main/java/net/server/channel/handlers/UseCashItemHandler.java",
        "AssignSPProcessor.canSPAssign(c, SPTo)",
        "AssignSPProcessor.canSPAssign(c, SPFrom)",
    )
    require(
        "src/main/java/client/processor/stat/AssignSPProcessor.java",
        "skillBook < 0 || skillBook >= remainingSps.length",
        "GameConstants.isInJobTree",
    )


def audit_skill_and_combat_wiring() -> None:
    require(
        "src/main/java/net/server/channel/handlers/CloseRangeDamageHandler.java",
        "parseDamage(p, chr, false, false)",
        "BuffStat.MORPH",
        "applyAttack(attack, chr, attackCount)",
    )
    require(
        "src/main/java/net/server/channel/handlers/RangedAttackHandler.java",
        "parseDamage(p, chr, true, false)",
        "if (weapon == null)",
        "BuffStat.SOULARROW",
        "BuffStat.SHADOWPARTNER",
        "applyAttack(attack, chr, bulletCount)",
    )
    require(
        "src/main/java/net/server/channel/handlers/MagicDamageHandler.java",
        "parseDamage(p, chr, false, true)",
        "applyAttack(attack, chr, effect.getAttackCount())",
    )
    require(
        "src/main/java/net/server/channel/handlers/SummonDamageHandler.java",
        "calcMaxDamage",
        "DAMAGE_HACK",
        "mob.applyStatus",
        "damageMonster",
    )
    require(
        "src/main/java/net/server/channel/handlers/AbstractDealDamageHandler.java",
        "MonsterStatus.MAGIC_IMMUNITY",
        "MonsterStatus.WEAPON_IMMUNITY",
        "ElementalEffectiveness.WEAK",
        "applyStatus",
        "player.isAlive()",
    )
    require(
        "src/main/java/client/Disease.java",
        "SLOW(", "SEDUCE(", "ZOMBIFY(", "STUN(", "POISON(", "SEAL(", "DARKNESS(", "CURSE(",
    )
    require(
        "src/main/java/client/status/MonsterStatus.java",
        "STUN(", "FREEZE(", "POISON(", "SEAL(", "DOOM(",
        "WEAPON_IMMUNITY(", "MAGIC_IMMUNITY(", "WEAPON_REFLECT(", "MAGIC_REFLECT(",
    )
    require(
        "src/main/java/server/life/MobSkill.java",
        "case DISPEL -> applyDispelEffect",
        "case SEDUCE -> disease = Disease.SEDUCE",
        "case UNDEAD -> disease = Disease.ZOMBIFY",
        "case PHYSICAL_IMMUNE",
        "case MAGIC_IMMUNE",
        "case PHYSICAL_COUNTER",
        "case MAGIC_COUNTER",
        "case SUMMON -> summonMonsters",
    )
    require(
        "src/main/java/net/server/channel/handlers/TakeDamageHandler.java",
        "damage *= (highDef.getEffect(hdLevel).getX() / 1000.0);",
        "BuffStat.MAGIC_GUARD",
        "BuffStat.MESOGUARD",
        "BuffStat.POWERGUARD",
        "BuffStat.MAGIC_SHIELD",
        "MobAttackInfoFactory.getMobAttackInfo",
    )
    if "Math.ceil(highDef.getEffect(hdLevel).getX() / 1000.0)" in read(
        "src/main/java/net/server/channel/handlers/TakeDamageHandler.java"
    ):
        raise AssertionError("Aran High Defense still rounds the WZ reduction multiplier up to 1.0")

    # Prove that the High Defense WZ multiplier is genuinely fractional at some levels,
    # so using ceil() would disable the passive rather than merely changing rounding.
    root = ET.parse(ROOT / "wz/Skill.wz/2112.img.xml").getroot()
    skill = next((node for node in root.iter("imgdir") if node.get("name") == "21120004"), None)
    if skill is None:
        raise AssertionError("Aran High Defense (21120004) missing from Skill.wz")
    xs = [int(node.get("value")) for node in skill.iter("int") if node.get("name") == "x"]
    if not xs or not any(0 < value < 1000 for value in xs):
        raise AssertionError("High Defense WZ x values do not expose the expected fractional per-mille reduction")


def audit_mastery_and_instance_lifecycle() -> None:
    require(
        "src/main/java/server/ItemInformationProvider.java",
        "usableMasteryBooks",
        "canUseSkillBook",
        "2290000",
        "2290139",
    )
    require(
        "src/main/java/scripting/npc/NPCConversationManager.java",
        "getAvailableMasteryBooks",
        "getSkillBookInfo",
    )

    # Event/PQ scripts use explicit death/revive hooks; the inventory audit separately
    # verifies that referenced managers exist. Require real lifecycle coverage rather
    # than a specific event name.
    events = list((ROOT / "scripts/event").glob("*.js"))
    revive = 0
    dead = 0
    for path in events:
        text = path.read_text(encoding="utf-8", errors="replace")
        dead += int(bool(re.search(r"\bfunction\s+playerDead\s*\(", text)))
        revive += int(bool(re.search(r"\bfunction\s+playerRevive\s*\(", text)))
    if dead < 20 or revive < 10:
        raise AssertionError(f"insufficient event death/revive lifecycle coverage: dead={dead} revive={revive}")


def main() -> int:
    try:
        audit_progression()
        audit_survivability_and_resets()
        audit_skill_and_combat_wiring()
        audit_mastery_and_instance_lifecycle()
    except (AssertionError, ET.ParseError) as exc:
        print(f"ERROR {exc}")
        return 1

    print("EverLeaf gameplay integrity audit: PASS")
    print("  post-200 EXP + level-250 cap contract: PRESENT")
    print("  weekly/Marks transactional anti-double-claim contract: PRESENT")
    print("  no-new-HP-washing + legacy unwind policy: PRESENT")
    print("  AP/SP reset packet guardrails: PRESENT")
    print("  melee/ranged/magic/summon attack paths: PRESENT")
    print("  status/dispel/immunity/reflect wiring: PRESENT")
    print("  Aran High Defense WZ multiplier parity: PRESENT")
    print("  mastery-book discovery/eligibility: PRESENT")
    print("  event death/revive lifecycle hooks: PRESENT")
    return 0


if __name__ == "__main__":
    sys.exit(main())

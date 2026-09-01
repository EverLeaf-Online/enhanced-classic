#!/usr/bin/env python3
"""Hard structural release gate for EverLeaf's v83 Evan backport.

This does not replace live-client playtesting. It ensures every server-side
piece required for a fresh Evan to exist and progress remains wired together.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def text(path: str) -> str:
    p = ROOT / path
    if not p.is_file():
        raise SystemExit(f"ERROR missing Evan release file: {path}")
    return p.read_text(encoding="utf-8", errors="replace")


def require(path: str, *fragments: str) -> None:
    data = text(path)
    for fragment in fragments:
        if fragment not in data:
            raise SystemExit(f"ERROR {path} missing Evan invariant: {fragment}")


def forbid(path: str, *fragments: str) -> None:
    data = text(path)
    for fragment in fragments:
        if fragment in data:
            raise SystemExit(f"ERROR {path} retains forbidden Evan pattern: {fragment}")


def audit_skill_data() -> None:
    expected_files = ["2001", "2200", *[str(i) for i in range(2210, 2219)]]
    ids: set[int] = set()
    for stem in expected_files:
        path = ROOT / "wz" / "Skill.wz" / f"{stem}.img.xml"
        if not path.is_file():
            raise SystemExit(f"ERROR missing Evan Skill.wz file: {path.relative_to(ROOT)}")
        ids.update(int(v) for v in re.findall(r'name="(\d{7,8})"', path.read_text(encoding="utf-8", errors="replace")))

    evan_constants = text("src/main/java/constants/skills/Evan.java")
    declared = {int(v) for v in re.findall(r'=\s*(\d{7,8})\s*;', evan_constants)}
    missing = sorted(declared - ids)
    if missing:
        raise SystemExit(f"ERROR Evan Skill.wz is missing declared skills: {missing}")
    if len(declared) != 43:
        raise SystemExit(f"ERROR expected 43 Evan skill constants, found {len(declared)}")


def main() -> int:
    require(
        "src/main/java/net/server/handlers/login/CreateCharHandler.java",
        "import client.creator.novice.EvanCreator;",
        "case 3: // Evan",
        "EvanCreator.createCharacter",
    )
    require(
        "src/main/java/client/creator/novice/EvanCreator.java",
        "Job.EVAN",
        "EVAN_START_MAP = 100030100",
        "new CharacterFactoryRecipe(Job.EVAN, 1, EVAN_START_MAP",
    )

    require(
        "src/main/java/client/Job.java",
        "EVAN(2001)", "EVAN1(2200)", "EVAN2(2210)", "EVAN3(2211)",
        "EVAN4(2212)", "EVAN5(2213)", "EVAN6(2214)", "EVAN7(2215)",
        "EVAN8(2216)", "EVAN9(2217)", "EVAN10(2218)",
    )
    require("src/main/java/constants/game/GameConstants.java", "return job - 2209;")
    require(
        "src/main/java/client/processor/stat/AssignSPProcessor.java",
        "GameConstants.getSkillBook(skillid / 10000)",
        "skillBook < 0 || skillBook >= remainingSps.length",
    )

    require("src/main/java/server/maps/Dragon.java", "class Dragon")
    require("src/main/java/net/server/channel/handlers/MoveDragonHandler.java", "class MoveDragonHandler")
    require("src/main/java/net/PacketProcessor.java", "MoveDragonHandler")
    require(
        "src/main/java/client/Character.java",
        "GameConstants.hasSPTable(newJob) && newJob.getId() != 2001",
        "createDragon();",
        "changeJob(newJob, true);",
        "private synchronized void changeJob(Job newJob, boolean grantJobChangeSp)",
        "if (grantJobChangeSp)",
        "private boolean isEvanGrowthJob()",
        "advanceEvanGrowthStage();\n        levelUpGainSp();",
        "changeJob(nextJob, false);",
        "level == 10 && job == Job.EVAN",
        "level == 20 && job == Job.EVAN1",
        "level == 30 && job == Job.EVAN2",
        "level == 40 && job == Job.EVAN3",
        "level == 50 && job == Job.EVAN4",
        "level == 60 && job == Job.EVAN5",
        "level == 80 && job == Job.EVAN6",
        "level == 100 && job == Job.EVAN7",
        "level == 120 && job == Job.EVAN8",
        "level == 160 && job == Job.EVAN9",
        "job.isA(Job.BLAZEWIZARD1) || isEvanGrowthJob()",
    )
    forbid(
        "src/main/java/client/Character.java",
        "levelUpGainSp();\n        advanceEvanGrowthStage();",
        "changeJob(nextJob);",
    )

    require(
        "src/main/java/net/server/channel/handlers/AbstractDealDamageHandler.java",
        "Evan.ICE_BREATH", "Evan.FIRE_BREATH",
    )
    require(
        "src/main/java/net/server/channel/handlers/CancelBuffHandler.java",
        "Evan.ICE_BREATH", "Evan.FIRE_BREATH",
    )

    require(
        "tools/apply_evan_behavior_fixes.py",
        "Evan Soul Stone death interception",
        "Evan Killer Wings target lock",
        "Evan Critical Magic damage-validation support",
    )
    require(
        "tools/apply_evan_progression_fixes.py",
        "Evan automatic mastery skips generic job-change SP",
        "Evan mastery-before-SP ordering",
    )
    require(
        ".github/workflows/run-build.yml",
        "python3 tools/apply_evan_skill_data.py",
        "python3 tools/apply_evan_behavior_fixes.py",
        "python3 tools/apply_evan_progression_fixes.py",
    )
    require(
        ".github/workflows/deploy-game-production.yml",
        "python3 tools/apply_evan_skill_data.py",
        "python3 tools/apply_evan_behavior_fixes.py",
        "python3 tools/apply_evan_progression_fixes.py",
    )

    audit_skill_data()

    print("EverLeaf Evan release audit: PASS")
    print("  fresh Evan creation: selector 3 -> job 2001, level 1, Utah's attic")
    print("  automatic mastery growth: 10/20/30/40/50/60/80/100/120/160")
    print("  mastery SP: one normal level-up grant into newly unlocked book; no generic changeJob double grant")
    print("  job growth chain: 2001, 2200, 2210-2218")
    print("  Evan Skill.wz: 43/43 declared server skills")
    print("  Evan HP/MP: magician-style level-up growth")
    print("  extended SP, dragon object/movement, charged Breath: wired")
    print("  Evan behavior + progression transforms: CI + production wired")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

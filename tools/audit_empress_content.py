#!/usr/bin/env python3
"""Static safety audit for EverLeaf Gate to the Future / Empress content."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_MAPS = [
    271000000, 271000100, 271000200, 271000210, 271000300,
    271010000, 271010001, 271010100, 271010200, 271010300, 271010301,
    271010400, 271010500, 271020000, 271020100, 271030000, 271030010,
    271030100, 271030101, 271030102, 271030200, 271030201, 271030202,
    271030203, 271030204, 271030205, 271030300, 271030310, 271030320,
    271030400, 271030410, 271030500, 271030510, 271030520, 271030530,
    271030540, 271030600, 271040000, 271040100, 271040200, 271040210,
    271040300,
]
REQUIRED_MOBS = list(range(8600000, 8600007)) + list(range(8610000, 8610015)) + list(range(8850000, 8850012))
REQUIRED_NPCS = [
    2142000, 2142001, 2142002, 2142003, 2142004, 2142005, 2142006, 2142007,
    2142008, 2142009, 2142010, 2143000, 2143001, 2143003, 2143004,
]
FINAL_CYGNUS = 8850011
CHAOS = 2049100
WHITE = 2340000


def need(path: str, failures: list[str]) -> Path:
    p = ROOT / path
    if not p.is_file():
        failures.append(f"missing required file: {path}")
    return p


def audit_foundation(failures: list[str]) -> None:
    policy = need("src/main/java/everleaf/content/EmpressContentPolicy.java", failures)
    event = need("scripts/event/EmpressBattle.js", failures)
    recruiter = need("scripts/npc/2143004.js", failures)
    lockout = need("src/main/java/everleaf/content/EmpressWeeklyLockoutService.java", failures)
    need("database/sql/migration/everleaf_empress_weekly_lockout.sql", failures)
    need("scripts/portal/out_cygnusBackGarden.js", failures)
    need("scripts/portal/back_cygnus.js", failures)
    need("docs/EMPRESS_CONTENT.md", failures)
    need("docs/EMPRESS_CANDIDATE_ASSET_INVENTORY.md", failures)

    if policy.is_file():
        text = policy.read_text(encoding="utf-8-sig", errors="replace")
        if 'EVERLEAF_ENABLE_EMPRESS_CONTENT' not in text or '"false"' not in text:
            failures.append("Empress runtime gate must default disabled")

    if event.is_file():
        text = event.read_text(encoding="utf-8-sig", errors="replace")
        required = ["minPlayers = 3", "maxPlayers = 12", "minLevel = 180", "maxLevel = 250", str(FINAL_CYGNUS)]
        for token in required:
            if token not in text:
                failures.append(f"EmpressBattle.js missing policy token: {token}")
        if "EmpressContentPolicy.isEnabled()" not in text:
            failures.append("EmpressBattle.js must enforce the runtime feature gate")
        if "EmpressWeeklyLockoutService.markClear" not in text:
            failures.append("EmpressBattle.js must record account weekly clears")

    if recruiter.is_file():
        text = recruiter.read_text(encoding="utf-8-sig", errors="replace")
        if "EmpressWeeklyLockoutService.canEnter" not in text:
            failures.append("Empress recruiter must enforce account weekly lockout")
        if "EmpressContentPolicy.isEnabled()" not in text:
            failures.append("Empress recruiter must enforce the runtime feature gate")

    if lockout.is_file():
        text = lockout.read_text(encoding="utf-8-sig", errors="replace")
        if "WeeklyWindow.forInstant" not in text:
            failures.append("Empress weekly lockout must use EverLeaf WeeklyWindow")


def audit_rewards(failures: list[str]) -> None:
    path = need("database/sql/migration/everleaf_boss_rare_scroll_drops.sql", failures)
    if not path.is_file():
        return
    text = path.read_text(encoding="utf-8-sig", errors="replace")

    # Final Cygnus must be an authored boss target with both scrolls in the same
    # migration. Chief Knights and Shinsoo must never be direct rare-scroll targets.
    if not re.search(r"\(\s*8850011\s*,\s*'Empress Cygnus'\s*,\s*40000\s*,\s*10000\s*\)", text):
        failures.append("final Cygnus must target base Chaos=40000 and White=10000")

    for mob_id in range(8850000, 8850011):
        if re.search(rf"\(\s*{mob_id}\s*,", text):
            failures.append(f"Empress support mob {mob_id} must not receive direct Chaos/White rows")

    if str(CHAOS) not in text or str(WHITE) not in text:
        failures.append("Empress boss migration must retain both rare-scroll item IDs")


def audit_staged_xml(failures: list[str]) -> None:
    map_dir = ROOT / "wz/Map.wz/Map/Map2"
    mob_dir = ROOT / "wz/Mob.wz"
    npc_dir = ROOT / "wz/Npc.wz"

    present_maps = [m for m in REQUIRED_MAPS if (map_dir / f"{m}.img.xml").is_file()]
    present_mobs = [m for m in REQUIRED_MOBS if (mob_dir / f"{m}.img.xml").is_file()]
    present_npcs = [n for n in REQUIRED_NPCS if (npc_dir / f"{n}.img.xml").is_file()]
    staged_any = bool(present_maps or present_mobs or present_npcs)

    if not staged_any:
        print("Empress XML mode: gated foundation only (no imported package staged yet)")
        return

    missing_maps = sorted(set(REQUIRED_MAPS) - set(present_maps))
    missing_mobs = sorted(set(REQUIRED_MOBS) - set(present_mobs))
    missing_npcs = sorted(set(REQUIRED_NPCS) - set(present_npcs))
    if missing_maps:
        failures.append(f"partial Empress map import; missing {len(missing_maps)} maps: {missing_maps}")
    if missing_mobs:
        failures.append(f"partial Empress mob import; missing {len(missing_mobs)} mobs: {missing_mobs}")
    if missing_npcs:
        failures.append(f"partial Empress NPC import; missing {len(missing_npcs)} NPCs: {missing_npcs}")

    print(f"Empress XML staged: maps={len(present_maps)}/{len(REQUIRED_MAPS)}, mobs={len(present_mobs)}/{len(REQUIRED_MOBS)}, NPCs={len(present_npcs)}/{len(REQUIRED_NPCS)}")


def main() -> int:
    failures: list[str] = []
    print("EverLeaf Empress content audit")
    audit_foundation(failures)
    audit_rewards(failures)
    audit_staged_xml(failures)

    if failures:
        for failure in failures:
            print(f"[FAIL] {failure}")
        return 1

    print("Empress content guardrails: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

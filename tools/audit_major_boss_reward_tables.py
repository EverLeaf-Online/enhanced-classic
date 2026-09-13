#!/usr/bin/env python3
"""Audit effective reward ownership for EverLeaf's major release bosses.

This is deliberately stricter than the broad reward-source audit. It verifies
that the boss IDs used by encounter scripts agree with the reward-bearing IDs
used by SQL, that controlled Chaos/White Scroll rows target final bodies only,
and that the Papulatus transitional-form correction remains present.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DROP_SQL = ROOT / "database/sql/2-db_drops.sql"
RARE_MIGRATION = ROOT / "database/sql/migration/everleaf_boss_rare_scroll_drops.sql"
PAP_FIX = ROOT / "database/sql/migration/everleaf_fix_papulatus_rare_scroll_target.sql"

CHAOS = 2049100
WHITE = 2340000

BOSSES = {
    8500002: ("Papulatus", 50),
    8800002: ("Zakum", 50),
    8810018: ("Horntail", 60),
    8820001: ("Pink Bean", 80),
    8850011: ("Empress Cygnus", 0),
}

RARE_TARGETS = {
    8500002: (10000, 1500),
    8510000: (10000, 1500),
    9420549: (15000, 2500),
    9420544: (15000, 2500),
    8800002: (20000, 3500),
    8810018: (30000, 7500),
    8850011: (40000, 10000),
    8820001: (50000, 15000),
}

ROW = re.compile(
    r"\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)"
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="replace")


def effective_seed_rows() -> dict[int, dict[int, tuple[int, int, int, int]]]:
    """Model the boss subset of 2-db_drops.sql.

    temp_data has PRIMARY KEY(dropperid,itemid), and the seed uses INSERT IGNORE,
    so the first row wins until a per-dropper DELETE. After drop_data is built,
    the explicit REPLACE block becomes authoritative for overlapping items.
    """
    text = read(DROP_SQL)
    create_at = text.find("CREATE TABLE IF NOT EXISTS `drop_data`")
    if create_at < 0:
        raise ValueError("drop_data creation marker not found")

    wanted = set(BOSSES) | {8500001}
    state = {mob_id: {} for mob_id in wanted}
    pre = text[:create_at]

    token = re.compile(
        r"(DELETE\s+FROM\s+temp_data\s+WHERE\s+dropperid\s*=\s*(\d+)\s*;"
        r"|INSERT(?:\s+IGNORE)?\s+INTO\s+temp_data\s*\([^;]+?\)\s*VALUES\s*(.+?);)",
        re.I | re.S,
    )
    for match in token.finditer(pre):
        statement = match.group(0)
        deleted = re.search(r"DELETE\s+FROM\s+temp_data\s+WHERE\s+dropperid\s*=\s*(\d+)", statement, re.I)
        if deleted:
            mob_id = int(deleted.group(1))
            if mob_id in state:
                state[mob_id].clear()
            continue
        for row in ROW.finditer(statement):
            mob_id, item_id, minimum, maximum, quest_id, chance = map(int, row.groups())
            if mob_id in state:
                state[mob_id].setdefault(item_id, (minimum, maximum, quest_id, chance))

    post = text[create_at:]
    replace_stmt = re.compile(
        r"REPLACE\s+INTO\s+drop_data\s*\([^;]+?\)\s*VALUES\s*(.+?);",
        re.I | re.S,
    )
    for match in replace_stmt.finditer(post):
        for row in ROW.finditer(match.group(1)):
            mob_id, item_id, minimum, maximum, quest_id, chance = map(int, row.groups())
            if mob_id in state:
                state[mob_id][item_id] = (minimum, maximum, quest_id, chance)

    return state


def parse_rare_targets(text: str) -> dict[int, tuple[int, int]]:
    result: dict[int, tuple[int, int]] = {}
    for mob_id, _name, chaos, white in re.findall(
        r"\(\s*(\d+)\s*,\s*'([^']+)'\s*,\s*(\d+)\s*,\s*(\d+)\s*\)", text
    ):
        result[int(mob_id)] = (int(chaos), int(white))
    return result


def require_fragment(path: Path, fragment: str, failures: list[str]) -> None:
    if not path.is_file():
        failures.append(f"missing {path.relative_to(ROOT)}")
        return
    if fragment not in read(path):
        failures.append(f"{path.relative_to(ROOT)} missing contract: {fragment}")


def main() -> int:
    failures: list[str] = []

    try:
        seed = effective_seed_rows()
    except (OSError, ValueError) as exc:
        print(f"[FAIL] could not model boss reward seed: {exc}")
        return 1

    print("EverLeaf major-boss reward table audit")
    for mob_id, (name, minimum_items) in BOSSES.items():
        item_count = len(seed.get(mob_id, {}))
        mastery = sum(1 for item_id in seed.get(mob_id, {}) if 2280000 <= item_id < 2300000)
        print(f"  {name:15} {mob_id}: base-items={item_count:3} mastery-books={mastery:2}")
        if item_count < minimum_items:
            failures.append(f"{name} ({mob_id}) base reward table unexpectedly small: {item_count} < {minimum_items}")

    # 8500001 is a transitional form. It revives into 8500002 and must not own
    # the canonical reward table or EverLeaf-managed rare-scroll rolls.
    if seed.get(8500001):
        failures.append("Papulatus transitional form 8500001 unexpectedly owns base reward rows")

    if not RARE_MIGRATION.is_file():
        failures.append("missing everleaf_boss_rare_scroll_drops.sql")
    else:
        actual_targets = parse_rare_targets(read(RARE_MIGRATION))
        if actual_targets != RARE_TARGETS:
            failures.append(f"rare-scroll boss target table mismatch: {actual_targets}")
        if 8500001 in actual_targets:
            failures.append("Papulatus transitional form 8500001 must not receive managed rare-scroll rows")

    if not PAP_FIX.is_file():
        failures.append("missing Papulatus corrective migration for already-upgraded databases")
    else:
        text = read(PAP_FIX)
        for fragment in (
            "IN (8500001, 8500002)",
            "(8500002, 2049100, 1, 1, 0, 10000)",
            "(8500002, 2340000, 1, 1, 0, 1500)",
        ):
            if fragment not in text:
                failures.append(f"Papulatus corrective migration missing: {fragment}")

    # Encounter ownership contracts: SQL reward bodies must match actual clear
    # bodies used by the retained encounter scripts.
    require_fragment(ROOT / "scripts/event/PapulatusBattle.js", "return mobid == 8500002;", failures)
    require_fragment(ROOT / "scripts/event/ZakumBattle.js", "mobid == 8800002", failures)
    require_fragment(ROOT / "scripts/event/HorntailBattle.js", "mobid == 8810018", failures)
    require_fragment(ROOT / "scripts/event/PinkBeanBattle.js", "mobid == 8820001", failures)
    require_fragment(ROOT / "scripts/event/EmpressBattle.js", "const CYGNUS_FINAL = 8850011;", failures)
    require_fragment(ROOT / "scripts/event/EmpressBattle.js", "allowDrops = true;", failures)
    require_fragment(ROOT / "scripts/npc/2143004.js", 'getEventManager("EmpressBattle")', failures)

    if failures:
        for failure in failures:
            print(f"[FAIL] {failure}")
        return 1

    print("  [OK] Papulatus rare rewards belong to final body 8500002, not transitional 8500001")
    print("  [OK] Zakum/Horntail/Pink Bean/Empress final reward IDs match encounter clear ownership")
    print("  [OK] controlled Chaos/White targets and corrective Papulatus migration are consistent")
    print("Major-boss reward table invariants: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

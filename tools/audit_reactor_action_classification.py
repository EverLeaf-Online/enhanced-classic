#!/usr/bin/env python3
"""Classify scriptless spawned reactors that carry a WZ `action` string.

A WZ action name is not, by itself, proof that EverLeaf needs a same-ID JS
handler. Many are dormant seasonal/event assets inherited from the v95 data.
Others are retained visual/state reactors whose historical side effect is
already owned by an EverLeaf event/NPC/WZ path. This gate keeps the known 45
findings explicitly classified and verifies the retained ownership evidence so
future content changes reopen the finding instead of silently regressing it.
"""
from __future__ import annotations

from pathlib import Path

from audit_reactor_script_coverage import reactor_action, spawned_reactors, SCRIPT_ROOT

ROOT = Path(__file__).resolve().parents[1]

LEGACY = {
    "1002001", "1002002", "1002003", "1002006", "1009000",
    "2002016", "2092000", "2092002", "2092003", "2099000",
    "2222001", "2222002",
    "2292001", "2292002", "2292003", "2292004", "2292005", "2292006", "2298001",
    "2612006", "2612007",
    "6741016", "6822000",
    "9000000", "9000001", "9000002", "9001000", "9002000", "9002001", "9002002",
    "9102008", "9222000", "9702000", "9902000",
}

RETAINED_COVERED = {
    "1058001", "1058003", "1058004", "1058005",
    "1058011", "1058013", "1058014", "1058015",
    "6109010", "6109011", "6702001",
}

# These source contracts are the reason the retained reactors do not need a
# same-ID reactor script. If any contract disappears, the release gate fails
# and the reactor must be reviewed again.
COVERAGE_CONTRACTS = {
    ROOT / "scripts/event/BalrogBattle.js": (
        "function spawnBalrog(eim)",
        "spawnFakeMonsterOnGroundBelow(LifeFactory.getMonster(8830000)",
        "spawnMonsterOnGroundBelow(LifeFactory.getMonster(8830002)",
        "spawnMonsterOnGroundBelow(LifeFactory.getMonster(8830006)",
    ),
    ROOT / "scripts/event/BalrogBattle_Easy.js": (
        "function spawnBalrog(eim)",
        "spawnFakeMonsterOnGroundBelow(LifeFactory.getMonster(8830007)",
        "spawnMonsterOnGroundBelow(LifeFactory.getMonster(8830009)",
        "spawnMonsterOnGroundBelow(LifeFactory.getMonster(8830013)",
    ),
    ROOT / "scripts/event/CWKPQ.js": (
        "function spawnGuardians(eim)",
        "eim.getMonster(9400594)",
        "map.spawnMonsterOnGroundBelow",
    ),
    ROOT / "scripts/npc/9201115.js": (
        "eim.getMonster(9400582)",
        "eim.getMonster(9400590)",
        "eim.getMonster(9400591)",
        "eim.getMonster(9400592)",
        "eim.getMonster(9400593)",
        "eim.setIntProperty(\"glpq6\", 3)",
    ),
}

# APQ's retained finding is different: 6702001 is the repeated gate reactor.
# Verify the map still contains seven named gates using that ID. Historical
# amoriaItem1 metadata contains only a reactor-state transition, no server-side
# spawn/reward payload, so the WZ state machine is the behavior owner.
APQ_MAP = ROOT / "wz/Map.wz/Map/Map6/670010600.img.xml"


def verify_retained_coverage() -> list[str]:
    failures: list[str] = []
    for path, fragments in COVERAGE_CONTRACTS.items():
        if not path.is_file():
            failures.append(f"retained reactor owner missing: {path.relative_to(ROOT)}")
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for fragment in fragments:
            if fragment not in text:
                failures.append(
                    f"retained reactor ownership contract missing in {path.relative_to(ROOT)}: {fragment}"
                )

    if not APQ_MAP.is_file():
        failures.append("APQ gate map missing: wz/Map.wz/Map/Map6/670010600.img.xml")
    else:
        text = APQ_MAP.read_text(encoding="utf-8", errors="ignore")
        if text.count('<string name="id" value="6702001"/>') != 7:
            failures.append("APQ 670010600 no longer has exactly seven 6702001 gate reactors")
        for gate in ("gate00", "gate01", "gate02", "gate03", "gate04", "gate05", "gate06"):
            if f'<string name="name" value="{gate}"/>' not in text:
                failures.append(f"APQ gate reactor name missing: {gate}")
    return failures


def main() -> int:
    usage, parse_errors = spawned_reactors()
    if parse_errors:
        for error in parse_errors:
            print(f"[FAIL] {error}")
        return 1

    action_bearing: dict[str, str] = {}
    for reactor_id in sorted(usage, key=int):
        if (SCRIPT_ROOT / f"{reactor_id}.js").is_file():
            continue
        action, error = reactor_action(reactor_id)
        if error:
            print(f"[FAIL] reactor {reactor_id}: {error}")
            return 1
        if action:
            action_bearing[reactor_id] = action

    actual = set(action_bearing)
    classified = LEGACY | RETAINED_COVERED
    unknown = actual - classified
    stale = classified - actual
    coverage_failures = verify_retained_coverage()

    print(
        f"EverLeaf scriptless-reactor action classification: total={len(actual)} "
        f"legacy={len(actual & LEGACY)} retained-covered={len(actual & RETAINED_COVERED)}"
    )
    if unknown:
        print(f"[FAIL] new/unclassified action-bearing reactors: {sorted(unknown, key=int)}")
    if stale:
        print(f"[FAIL] classification contains reactors no longer matching the finding set: {sorted(stale, key=int)}")
    for failure in coverage_failures:
        print(f"[FAIL] {failure}")

    for reactor_id in sorted(actual & RETAINED_COVERED, key=int):
        maps = ",".join(sorted(usage[reactor_id], key=int))
        print(f"[COVERED] reactor={reactor_id} action={action_bearing[reactor_id]} maps={maps}")

    if unknown or stale or coverage_failures:
        return 1

    print("PASS: all action-bearing scriptless reactors are explicitly classified")
    print("  34 dormant/legacy assets require no release restoration")
    print("  11 retained-content reactors have verified event/NPC/WZ-state owners; no guessed scripts are required")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

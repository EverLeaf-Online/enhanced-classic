#!/usr/bin/env python3
"""Classify scriptless spawned reactors that carry a WZ `action` string.

A WZ action name is not, by itself, proof that EverLeaf needs a same-ID JS
handler. Many are dormant seasonal/event assets inherited from the v95 data.
Others are retained visual/state reactors whose historical side effect is
already owned by an EverLeaf event/NPC script. This gate keeps the known 45
findings explicitly classified so new/unclassified reactors fail review instead
of being silently treated as active content.
"""
from __future__ import annotations

from audit_reactor_script_coverage import reactor_action, spawned_reactors, SCRIPT_ROOT

# Dormant/legacy event assets. These maps/actions are not part of EverLeaf's
# retained release-facing content. 2612006/7 are legacy 2008 New Year cheese
# warehouse reactors; historical Odin/KMS scripts confirm they simply dropped
# event items.
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

# Retained reactors whose gameplay side effect is already represented by the
# canonical server content flow, so a same-ID JS reactor handler is not needed.
#
# Balrog (normal/easy): BalrogBattle*.js spawns the fake body, arms/claws and
# sealed boss directly during event setup. The altar/totem WZ action strings are
# therefore visual/state metadata, not EverLeaf's authoritative spawn path.
#
# CWKPQ: the entrance Guardian wave is spawned by CWKPQ.js::spawnGuardians();
# the boss-room Guardian/Twisted Master waves are spawned by NPC 9201115.js.
# The 6109010/6109011 WZ action names do not own those encounters here.
#
# APQ: map 670010600 contains seven 6702001 reactors named gate00..gate06.
# Historical action metadata for amoriaItem1 is only a reactor state transition
# (type 2 -> state 1), with no monster/reward/script payload; the WZ state
# machine itself supplies that door animation/state behavior.
RETAINED_COVERED = {
    "1058001", "1058003", "1058004", "1058005",
    "1058011", "1058013", "1058014", "1058015",
    "6109010", "6109011", "6702001",
}


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

    print(
        f"EverLeaf scriptless-reactor action classification: total={len(actual)} "
        f"legacy={len(actual & LEGACY)} retained-covered={len(actual & RETAINED_COVERED)}"
    )
    if unknown:
        print(f"[FAIL] new/unclassified action-bearing reactors: {sorted(unknown, key=int)}")
    if stale:
        print(f"[FAIL] classification contains reactors no longer matching the finding set: {sorted(stale, key=int)}")

    for reactor_id in sorted(actual & RETAINED_COVERED, key=int):
        maps = ",".join(sorted(usage[reactor_id], key=int))
        print(f"[COVERED] reactor={reactor_id} action={action_bearing[reactor_id]} maps={maps}")

    if unknown or stale:
        return 1

    print("PASS: all action-bearing scriptless reactors are explicitly classified")
    print("  34 dormant/legacy assets require no release restoration")
    print("  11 retained-content reactors are covered by event/NPC/WZ-state behavior; no guessed scripts are required")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

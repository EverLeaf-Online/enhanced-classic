#!/usr/bin/env python3
"""Report EverLeaf economy/rate settings and NX coupon drop behavior.

This is intentionally read-only. It is used in CI to keep economy assumptions
visible while we tune Enhanced Classic progression.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config.yaml"
SQL_FILES = [ROOT / "database/sql/1-db_database.sql", ROOT / "database/sql/2-db_drops.sql"]
NX_VALUES = {4031865: 100, 4031866: 250}
DENOMINATOR = 999_999  # MapleMap global-drop roll uses nextInt(999999) < chance


def read_rate(text: str, key: str) -> int:
    match = re.search(rf"^\s*{re.escape(key)}:\s*(\d+)\s*$", text, re.MULTILINE)
    if not match:
        raise SystemExit(f"Missing {key} in config.yaml")
    return int(match.group(1))


def find_sql_occurrences(item_id: int):
    hits = []
    insert_table = None
    insert_re = re.compile(r"INSERT(?:\s+IGNORE)?\s+INTO\s+`?([A-Za-z0-9_]+)`?", re.IGNORECASE)
    tuple_re = re.compile(r"\(([^;]+)\)[,;]?\s*$")

    for path in SQL_FILES:
        if not path.is_file():
            continue
        for line_no, raw in enumerate(path.read_text(encoding="utf-8-sig", errors="replace").splitlines(), 1):
            m = insert_re.search(raw)
            if m:
                insert_table = m.group(1)
            if str(item_id) not in raw:
                continue

            values = None
            tm = tuple_re.search(raw.strip())
            if tm:
                parts = [p.strip().strip("'") for p in tm.group(1).split(",")]
                values = parts
            hits.append((path.relative_to(ROOT), line_no, insert_table, raw.strip(), values))
    return hits


def parse_global_chance(values, item_id: int):
    if not values:
        return None
    # drop_data_global schema is normally:
    # (id, continent, itemid, minimum_quantity, maximum_quantity, questid, chance)
    # or INSERTs may omit the id and use six columns. Detect the item position and
    # take the final numeric value as chance.
    try:
        numeric = [int(v) for v in values]
    except ValueError:
        return None
    if item_id not in numeric:
        return None
    return numeric[-1]


def main() -> int:
    cfg = CONFIG.read_text(encoding="utf-8-sig")
    rates = {
        "EXP": read_rate(cfg, "exp_rate"),
        "Meso": read_rate(cfg, "meso_rate"),
        "Drop": read_rate(cfg, "drop_rate"),
        "Boss drop": read_rate(cfg, "boss_drop_rate"),
        "Quest": read_rate(cfg, "quest_rate"),
    }

    print("EverLeaf economy balance audit")
    print("Rates: " + ", ".join(f"{name}={value}x" for name, value in rates.items()))
    print("Global-drop note: global drops are rolled independently of the normal Drop/Boss Drop multiplier.")

    expected_nx_per_kill = 0.0
    found_global = False
    for item_id, nx_value in NX_VALUES.items():
        hits = find_sql_occurrences(item_id)
        print(f"NX coupon {item_id} ({nx_value} NX): {len(hits)} SQL occurrence(s)")
        for path, line_no, table, raw, values in hits:
            print(f"  {path}:{line_no} table={table or 'unknown'} {raw}")
            if table and table.lower() == "drop_data_global":
                chance = parse_global_chance(values, item_id)
                if chance is not None:
                    found_global = True
                    probability = chance / DENOMINATOR
                    expected_nx_per_kill += probability * nx_value
                    print(
                        f"    global chance={chance}/{DENOMINATOR} "
                        f"({probability * 100:.5f}%)"
                    )

    if found_global:
        print(f"Expected NX per 1,000 kills from configured NX globals: {expected_nx_per_kill * 1000:.2f}")
        for kills_per_hour in (500, 1000, 2000, 4000):
            print(f"  at {kills_per_hour:,} kills/hour: ~{expected_nx_per_kill * kills_per_hour:.1f} NX/hour")
    else:
        print("No NX coupon rows were identified in drop_data_global seed SQL; verify the live DB before launch.")

    # First-pass Enhanced Classic guardrails. These are deliberately broad; CI
    # should catch accidental 10x-style drift without pretending playtest balance
    # is solved by static numbers.
    failures = []
    if not 2 <= rates["EXP"] <= 6:
        failures.append(f"EXP rate {rates['EXP']}x is outside the 2x-6x EverLeaf pre-alpha band")
    if not 1 <= rates["Meso"] <= 4:
        failures.append(f"Meso rate {rates['Meso']}x is outside the 1x-4x EverLeaf pre-alpha band")
    if not 1 <= rates["Drop"] <= 3:
        failures.append(f"Drop rate {rates['Drop']}x is outside the 1x-3x EverLeaf pre-alpha band")
    if not 1 <= rates["Boss drop"] <= 3:
        failures.append(f"Boss drop rate {rates['Boss drop']}x is outside the 1x-3x EverLeaf pre-alpha band")

    if failures:
        for failure in failures:
            print(f"[FAIL] {failure}")
        return 1

    print("Economy rate guardrails: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

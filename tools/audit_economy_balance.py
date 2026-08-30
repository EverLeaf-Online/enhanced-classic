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
BASE_SQL = ROOT / "database/sql/1-db_database.sql"
NX_MIGRATION = ROOT / "database/sql/migration/everleaf_nx_drop_balance.sql"
NX_VALUES = {4031865: 100, 4031866: 250}
NX_TARGET_CHANCES = {4031865: 400, 4031866: 100}
DENOMINATOR = 999_999  # MapleMap global-drop roll uses nextInt(999999) < chance


def read_rate(text: str, key: str) -> int:
    match = re.search(rf"^\s*{re.escape(key)}:\s*(\d+)(?:\s*#.*)?\s*$", text, re.MULTILINE)
    if not match:
        raise SystemExit(f"Missing {key} in config.yaml")
    return int(match.group(1))


def extract_seed_global(item_id: int) -> int | None:
    """Return chance for one item in the seeded drop_data_global INSERT."""
    text = BASE_SQL.read_text(encoding="utf-8-sig", errors="replace")
    block_match = re.search(
        r"INSERT\s+INTO\s+`drop_data_global`.*?VALUES\s*(.*?);",
        text,
        re.IGNORECASE | re.DOTALL,
    )
    if not block_match:
        return None

    # Schema: id, continent, itemid, minimum_quantity, maximum_quantity,
    # questid, chance, comments. Comments may contain commas, so capture only
    # the numeric columns that precede them.
    row_re = re.compile(
        rf"\(\s*\d+\s*,\s*-?\d+\s*,\s*{item_id}\s*,\s*\d+\s*,\s*\d+\s*,\s*-?\d+\s*,\s*(\d+)\s*,"
    )
    match = row_re.search(block_match.group(1))
    return int(match.group(1)) if match else None


def extract_target_chance(item_id: int) -> int | None:
    if not NX_MIGRATION.is_file():
        return None
    text = NX_MIGRATION.read_text(encoding="utf-8-sig", errors="replace")
    match = re.search(
        rf"UPDATE\s+`drop_data_global`\s+SET\s+`chance`\s*=\s*(\d+).*?WHERE\s+`itemid`\s*=\s*{item_id}\b",
        text,
        re.IGNORECASE | re.DOTALL,
    )
    return int(match.group(1)) if match else None


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

    failures: list[str] = []
    expected_nx_per_kill = 0.0

    for item_id, nx_value in NX_VALUES.items():
        seed = extract_seed_global(item_id)
        target = extract_target_chance(item_id)
        expected_target = NX_TARGET_CHANCES[item_id]

        if seed is None:
            failures.append(f"NX coupon {item_id} is missing from base drop_data_global seed")
            print(f"NX coupon {item_id} ({nx_value} NX): seed=MISSING")
        else:
            seed_probability = seed / DENOMINATOR
            print(
                f"NX coupon {item_id} ({nx_value} NX): base chance={seed}/{DENOMINATOR} "
                f"({seed_probability * 100:.4f}%)"
            )

        if target is None:
            failures.append(f"NX coupon {item_id} has no EverLeaf balance migration target")
            print("  EverLeaf target: MISSING")
        else:
            probability = target / DENOMINATOR
            expected_nx_per_kill += probability * nx_value
            print(
                f"  EverLeaf target={target}/{DENOMINATOR} "
                f"({probability * 100:.4f}%)"
            )
            if target != expected_target:
                failures.append(
                    f"NX coupon {item_id} target is {target}; expected {expected_target}"
                )

    print(f"EverLeaf NX target expected value: {expected_nx_per_kill * 1000:.2f} NX per 1,000 kills")
    for kills_per_hour in (500, 1000, 2000, 4000):
        print(f"  at {kills_per_hour:,} kills/hour: ~{expected_nx_per_kill * kills_per_hour:.1f} NX/hour")

    # First-pass Enhanced Classic guardrails. These are deliberately broad; CI
    # catches accidental high-rate drift without pretending static numbers can
    # replace alpha telemetry and playtesting.
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

    print("Economy/NX guardrails: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

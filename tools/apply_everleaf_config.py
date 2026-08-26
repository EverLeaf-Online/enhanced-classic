#!/usr/bin/env python3
"""Apply Everleaf development configuration deterministically.

This transform keeps the upstream Cosmic configuration easy to compare while
ensuring builds/tests use Everleaf's intended defaults. It intentionally fails
when expected upstream values change so configuration drift is visible in CI.
"""
from pathlib import Path

CONFIG = Path("config.yaml")


def replace_once(text: str, old: str, new: str) -> str:
    if new in text:
        return text
    if old not in text:
        raise SystemExit(f"Expected config pattern not found: {old!r}")
    return text.replace(old, new, 1)


def main() -> None:
    text = CONFIG.read_text(encoding="utf-8-sig")

    replacements = [
        ("    #Properties for Scania 0", "    # Everleaf primary world (protocol world id 0 / Scania slot)"),
        ("    server_message: Welcome to Scania!", "    server_message: Welcome to Everleaf — Classic roots. New growth."),
        ("    event_message: Scania!", "    event_message: Everleaf — Enhanced Classic v83"),
        ("    why_am_i_recommended: Welcome to Scania!", "    why_am_i_recommended: Everleaf — level 250, modern progression, no P2W."),
        ("    exp_rate: 10", "    exp_rate: 5"),
        ("    meso_rate: 10", "    meso_rate: 3"),
        ("    drop_rate: 10", "    drop_rate: 2"),
        ("    boss_drop_rate: 10", "    boss_drop_rate: 2"),
        ("    quest_rate: 5", "    quest_rate: 1"),
        ("    fishing_rate: 10", "    fishing_rate: 2"),
        ("    travel_rate: 10", "    travel_rate: 2"),
        ("    USE_SUPPLY_RATE_COUPONS: true", "    USE_SUPPLY_RATE_COUPONS: false"),
    ]

    for old, new in replacements:
        text = replace_once(text, old, new)

    CONFIG.write_text(text, encoding="utf-8")
    print("Everleaf development configuration applied.")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Apply EverLeaf development configuration deterministically.

This transform keeps the upstream Cosmic configuration easy to compare while
ensuring builds/tests use EverLeaf's intended defaults. It intentionally fails
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


def replace_first_of(text: str, candidates: tuple[str, ...], new: str) -> str:
    if new in text:
        return text
    for old in candidates:
        if old in text:
            return text.replace(old, new, 1)
    raise SystemExit(f"Expected one of these config patterns: {candidates!r}")


def main() -> None:
    text = CONFIG.read_text(encoding="utf-8-sig")

    text = replace_first_of(
        text,
        (
            "    #Properties for Scania 0",
            "    # Everleaf primary world (protocol world id 0 / Scania slot)",
            "    # EverLeaf primary world (protocol world id 0 / Scania slot)",
        ),
        "    # EverLeaf primary world (protocol world id 0 / Scania slot)",
    )

    # Quote user-facing strings and keep them ASCII. YamlBeans' tokenizer is
    # stricter than modern YAML parsers and can reject punctuation in an
    # unquoted scalar.
    message_replacements = [
        (
            (
                "    server_message: Welcome to Scania!",
                "    server_message: Welcome to Everleaf — Classic roots. New growth.",
                '    server_message: "Welcome to Everleaf - Classic roots. New growth."',
            ),
            '    server_message: "Welcome to EverLeaf - Classic roots. New growth."',
        ),
        (
            (
                "    event_message: Scania!",
                "    event_message: Everleaf — Enhanced Classic v83",
                '    event_message: "Everleaf - Enhanced Classic v83"',
            ),
            '    event_message: "EverLeaf - Enhanced Classic v83"',
        ),
        (
            (
                "    why_am_i_recommended: Welcome to Scania!",
                "    why_am_i_recommended: Everleaf — level 250, modern progression, no P2W.",
                '    why_am_i_recommended: "Everleaf - level 250, modern progression, no P2W."',
            ),
            '    why_am_i_recommended: "EverLeaf - level 250, modern progression, no P2W."',
        ),
    ]
    for candidates, new in message_replacements:
        text = replace_first_of(text, candidates, new)

    replacements = [
        ("    channels: 3", "    channels: 8"),
        ("    exp_rate: 10", "    exp_rate: 5"),
        ("    meso_rate: 10", "    meso_rate: 3"),
        ("    drop_rate: 10", "    drop_rate: 2"),
        ("    boss_drop_rate: 10", "    boss_drop_rate: 2"),
        ("    quest_rate: 5", "    quest_rate: 1"),
        ("    fishing_rate: 10", "    fishing_rate: 2"),
        ("    travel_rate: 10", "    travel_rate: 2"),
        ("    AUTOMATIC_REGISTER: true", "    AUTOMATIC_REGISTER: false"),
        ("    USE_SUPPLY_RATE_COUPONS: true", "    USE_SUPPLY_RATE_COUPONS: false"),
    ]

    # The primary EverLeaf world is intentionally eight channels. The source
    # currently already carries this value; accepting either 8 or upstream 3
    # keeps the transform deterministic if the baseline changes later.
    if "    channels: 8" not in text:
        text = replace_once(text, "    channels: 3", "    channels: 8")

    for old, new in replacements[1:]:
        text = replace_once(text, old, new)

    CONFIG.write_text(text, encoding="utf-8")
    print("EverLeaf development configuration applied (8 channels; website registration required).")


if __name__ == "__main__":
    main()

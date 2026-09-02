#!/usr/bin/env python3
"""Apply EverLeaf development configuration deterministically.

This transform keeps the upstream Cosmic configuration easy to compare while
ensuring builds/tests use EverLeaf's intended defaults. It intentionally fails
when expected upstream values change so configuration drift is visible in CI.
"""
from pathlib import Path
import subprocess

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


def force_primary_world_channels(text: str, channels: int) -> str:
    """Set only world 0's channel count, regardless of later world values.

    Production preserves the previous config before applying this transform, so
    global idempotency checks are unsafe: a later world could already contain the
    target value while world 0 is still stale. Restrict the edit to the first
    world block instead.
    """
    worlds_pos = text.find("worlds:")
    server_pos = text.find("\nserver:")
    if worlds_pos == -1 or server_pos == -1 or server_pos <= worlds_pos:
        raise SystemExit("Could not locate worlds section in config.yaml")

    world_section = text[worlds_pos:server_pos]
    first_world_start = world_section.find("  - flag:")
    second_world_start = world_section.find("\n  - flag:", first_world_start + 1)
    if first_world_start == -1:
        raise SystemExit("Could not locate primary world block in config.yaml")
    if second_world_start == -1:
        second_world_start = len(world_section)

    first_world = world_section[first_world_start:second_world_start]
    lines = first_world.splitlines(keepends=True)
    channel_indices = [i for i, line in enumerate(lines) if line.lstrip().startswith("channels:")]
    if len(channel_indices) != 1:
        raise SystemExit(f"Expected exactly one primary-world channels line, found {len(channel_indices)}")

    index = channel_indices[0]
    newline = "\n" if lines[index].endswith("\n") else ""
    indent = lines[index][: len(lines[index]) - len(lines[index].lstrip())]
    lines[index] = f"{indent}channels: {channels}{newline}"
    updated_first_world = "".join(lines)
    updated_world_section = (
        world_section[:first_world_start]
        + updated_first_world
        + world_section[second_world_start:]
    )
    return text[:worlds_pos] + updated_world_section + text[server_pos:]


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

    # EverLeaf uses Cosmic's full v83 channel list: 20 channels on ports
    # 7575-7594. Always force the primary world block rather than relying on a
    # global search so preserved production config cannot silently stay at 8.
    text = force_primary_world_channels(text, 20)

    # Channel.java advertises server.HOST back to the MapleStory client after
    # world/channel selection. Loopback here makes remote players reconnect to
    # their own PC, so production must advertise EverLeaf's public IPv4 address.
    text = replace_once(text, "    HOST: 127.0.0.1", "    HOST: 132.145.141.79")

    replacements = [
        ("    exp_rate: 10", "    exp_rate: 5"),
        ("    meso_rate: 10", "    meso_rate: 3"),
        ("    drop_rate: 10", "    drop_rate: 2"),
        ("    boss_drop_rate: 10", "    boss_drop_rate: 2"),
        ("    quest_rate: 5", "    quest_rate: 1"),
        ("    fishing_rate: 10", "    fishing_rate: 2"),
        ("    travel_rate: 10", "    travel_rate: 2"),
        ("    AUTOMATIC_REGISTER: true", "    AUTOMATIC_REGISTER: false"),
        ("    USE_SUPPLY_RATE_COUPONS: true", "    USE_SUPPLY_RATE_COUPONS: false"),
        ("    USE_ANNOUNCE_NX_COUPON_LOOT: false", "    USE_ANNOUNCE_NX_COUPON_LOOT: true"),
    ]

    for old, new in replacements:
        text = replace_once(text, old, new)

    CONFIG.write_text(text, encoding="utf-8")

    # This feature branch carries SoloMapling as an additive QA layer. Apply
    # its narrowly-scoped host hooks through the same deterministic transform
    # stage so CI tests the reconciled EverLeaf host code without replacing it.
    subprocess.run(["python3", "tools/apply_solomapling_host_hooks.py"], check=True)

    print("EverLeaf development configuration applied (20 channels; public channel host; website registration required).")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Apply Enhanced Classic development defaults to Cosmic's config.yaml.

This intentionally uses exact, validated replacements instead of a YAML writer so
comments and formatting in the upstream configuration remain intact.
"""
from pathlib import Path

CONFIG = Path(__file__).resolve().parents[1] / "config.yaml"

REPLACEMENTS = {
    "    exp_rate: 10\n": "    exp_rate: 5\n",
    "    meso_rate: 10\n": "    meso_rate: 3\n",
    "    drop_rate: 10\n": "    drop_rate: 2\n",
    "    boss_drop_rate: 10                      #NOTE: Boss drop rate OVERRIDES common drop rate, for bosses-only.\n":
        "    boss_drop_rate: 2                       #NOTE: Boss drop rate OVERRIDES common drop rate, for bosses-only.\n",
    "    quest_rate: 5                           #Multiplier for Exp & Meso gains when completing a quest. Only available when USE_QUEST_RATE is true. Stacks with server Exp & Meso rates.\n":
        "    quest_rate: 1                           #Enhanced Classic: quests will be tuned directly instead of globally over-multiplied.\n",
    "    fishing_rate: 10                        #Multiplier for success likelihood on meso thrown during fishing.\n":
        "    fishing_rate: 2                         #Enhanced Classic development baseline.\n",
    "    travel_rate: 10                         #Means of transportation rides/departs using 1/N of the default time.\n":
        "    travel_rate: 2                         #Enhanced Classic: faster travel without effectively removing it.\n",
    "    USE_SUPPLY_RATE_COUPONS: true       #Allows rate coupons to be sold through the Cash Shop.\n":
        "    USE_SUPPLY_RATE_COUPONS: false      #Enhanced Classic: no paid rate advantages / no P2W.\n",
}

# These values intentionally target only the first configured world. EverLeaf currently
# runs one world (server.WORLDS = 1), so changing every upstream world's channel count
# would be misleading and would waste resources if more worlds are ever enabled.
FIRST_WORLD_REPLACEMENTS = {
    "    server_message: Welcome to Scania!\n": "    server_message: Welcome to EverLeaf!\n",
    "    event_message: Scania!\n": "    event_message: EverLeaf Enhanced Classic\n",
    "    why_am_i_recommended: Welcome to Scania!\n": "    why_am_i_recommended: Welcome to EverLeaf!\n",
    "    channels: 3\n": "    channels: 20\n",
}


def replace_first_world(updated: str, old: str, new: str) -> str:
    """Replace only the first-world occurrence while remaining idempotent."""
    first_server = updated.find("server:\n")
    world_section = updated if first_server == -1 else updated[:first_server]

    if new in world_section:
        return updated

    # Accept the former EverLeaf 8-channel value as an upgrade source.
    if old == "    channels: 3\n":
        old8 = "    channels: 8\n"
        pos8 = world_section.find(old8)
        if pos8 != -1:
            return updated[:pos8] + new + updated[pos8 + len(old8):]

    pos = world_section.find(old)
    if pos == -1:
        raise SystemExit(f"Expected first-world config line not found: {old.strip()}")

    return updated[:pos] + new + updated[pos + len(old):]


def main() -> None:
    original = CONFIG.read_text(encoding="utf-8-sig")
    updated = original

    for old, new in REPLACEMENTS.items():
        count = updated.count(old)
        if count == 0:
            # Idempotency: accept an already-patched value.
            if new in updated:
                continue
            raise SystemExit(f"Expected config line not found: {old.strip()}")
        if count != 1:
            raise SystemExit(f"Expected exactly one match, found {count}: {old.strip()}")
        updated = updated.replace(old, new, 1)

    for old, new in FIRST_WORLD_REPLACEMENTS.items():
        updated = replace_first_world(updated, old, new)

    if updated != original:
        CONFIG.write_text(updated, encoding="utf-8")
        print("Applied Enhanced Classic configuration defaults (EverLeaf: 20 channels).")
    else:
        print("Enhanced Classic configuration defaults already applied (EverLeaf: 20 channels).")


if __name__ == "__main__":
    main()

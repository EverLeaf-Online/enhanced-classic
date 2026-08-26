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

    if updated != original:
        CONFIG.write_text(updated, encoding="utf-8")
        print("Applied Enhanced Classic configuration defaults.")
    else:
        print("Enhanced Classic configuration defaults already applied.")


if __name__ == "__main__":
    main()

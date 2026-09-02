#!/usr/bin/env python3
"""Static policy checks for EverLeaf's Maple Leaf exchange."""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SHOP = ROOT / "scripts/npc/everleaf_leaf_exchange.js"
COMMAND = ROOT / "src/main/java/client/command/commands/gm0/LeafShopCommand.java"
TRANSFORM = ROOT / "tools/apply_level_cap_250.py"

FORBIDDEN_IDS = {
    2049100: "Chaos Scroll",
    2340000: "White Scroll",
    4031865: "100 NX Coupon",
    4031866: "250 NX Coupon",
}

EXPECTED_COSTS = {
    "AP_RESET_LEAVES": 15,
    "CHARM_LEAVES": 25,
    "CHAIR_LEAVES": 30,
    "MERCHANT_LEAVES": 40,
    "MAPLE_WEAPON_LEAVES": 60,
}


def fail(message: str) -> None:
    raise SystemExit(f"[FAIL] {message}")


def read(path: Path) -> str:
    if not path.is_file():
        fail(f"Missing required file: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8")


def main() -> None:
    shop = read(SHOP)
    command = read(COMMAND)
    transform = read(TRANSFORM)

    for item_id, name in FORBIDDEN_IDS.items():
        if re.search(rf"(?<!\d){item_id}(?!\d)", shop):
            fail(f"Maple Leaf exchange must not contain {name} ({item_id})")

    costs = {
        name: int(value)
        for name, value in re.findall(r"var\s+([A-Z_]+_LEAVES)\s*=\s*(\d+)\s*;", shop)
    }
    if costs != EXPECTED_COSTS:
        fail(f"Maple Leaf price table changed unexpectedly: {costs}")

    if "MAPLE_WEAPON_MESO = 1000000" not in shop or "MERCHANT_MESO = 500000" not in shop:
        fail("High-value Leaf rewards must retain their meso sink component")

    chair_match = re.search(r"var\s+chairs\s*=\s*\[(.*?)\];", shop, re.S)
    weapon_match = re.search(r"var\s+mapleWeapons\s*=\s*\[(.*?)\];", shop, re.S)
    if not chair_match or not weapon_match:
        fail("Leaf shop cosmetic/Maple weapon allowlists are missing")

    chairs = [int(v) for v in re.findall(r"\b\d{7}\b", chair_match.group(1))]
    weapons = [int(v) for v in re.findall(r"\b\d{7}\b", weapon_match.group(1))]
    if not chairs or any(not 3010000 <= item < 3020000 for item in chairs):
        fail("Leaf chair allowlist contains invalid/non-chair IDs")
    if not weapons or any(not 1300000 <= item < 1500000 for item in weapons):
        fail("Leaf Maple weapon allowlist contains invalid/non-weapon IDs")

    for token in ["cm.haveItem(MAPLE_LEAF, leaves)", "cm.canHold(itemId, qty)", "cm.gainItem(MAPLE_LEAF, -leaves)"]:
        if token not in shop:
            fail(f"Leaf exchange missing transaction guard: {token}")

    if "getEventInstance() != null" not in command:
        fail("@leafshop must stay disabled in active event/PQ/boss instances")
    if 'openNpc(9030100, "everleaf_leaf_exchange")' not in command:
        fail("@leafshop is not wired to the Leaf exchange script")
    if 'addCommand(new String[]{"leafshop", "leaves"}, LeafShopCommand.class);' not in transform:
        fail("Leaf shop command is not registered by the EverLeaf source transform")

    print("[PASS] Maple Leaf exchange policy audit")
    print(f"       leaf_costs={costs}")
    print(f"       cosmetic_chairs={len(chairs)} classic_maple_weapons={len(weapons)}")
    print("       NX/Chaos/White=end-user exchange blocked")
    print("       high-value rewards include meso sinks")


if __name__ == "__main__":
    main()

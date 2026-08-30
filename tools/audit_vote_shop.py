#!/usr/bin/env python3
"""Static policy checks for EverLeaf's Vote Point exchange.

The vote shop is intentionally convenience/cosmetic focused. This audit is
kept simple and strict so an accidental high-impact reward cannot quietly land
in the exchange during future edits.
"""

from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
SHOP = ROOT / "scripts" / "npc" / "9030100.js"

FORBIDDEN_ITEM_IDS = {
    2049100: "Chaos Scroll",
    2340000: "White Scroll",
}

REQUIRED_SNIPPETS = [
    "Vote Point Exchange",
    "getVotePoints()",
    "useVotePoints(",
    "VOTE_LEAF_COST",
    "VOTE_CHARM_COST",
    "VOTE_MERCHANT_COST",
    "VOTE_CHAIR_COST",
]


def fail(message: str) -> None:
    print(f"[FAIL] {message}")
    raise SystemExit(1)


def main() -> None:
    if not SHOP.is_file():
        fail(f"Vote shop script missing: {SHOP.relative_to(ROOT)}")

    text = SHOP.read_text(encoding="utf-8")

    for snippet in REQUIRED_SNIPPETS:
        if snippet not in text:
            fail(f"Vote shop is missing required guard/policy marker: {snippet}")

    for item_id, name in FORBIDDEN_ITEM_IDS.items():
        # Ignore policy comments that name the items. Flag only numeric item IDs,
        # which are what an actual reward path would need.
        if re.search(rf"(?<!\d){item_id}(?!\d)", text):
            fail(f"Vote shop must not directly sell {name} ({item_id})")

    costs = {
        name: int(value)
        for name, value in re.findall(r"var\s+(VOTE_[A-Z_]+_COST)\s*=\s*(\d+)\s*;", text)
    }
    if len(costs) < 4:
        fail("Could not parse all expected Vote Point prices")
    if any(value <= 0 for value in costs.values()):
        fail(f"Vote Point prices must be positive: {costs}")

    chair_match = re.search(r"var\s+voteChairs\s*=\s*\[(.*?)\];", text, re.S)
    if not chair_match:
        fail("Vote chair allowlist is missing")
    chairs = [int(v) for v in re.findall(r"\b\d{7}\b", chair_match.group(1))]
    if not chairs:
        fail("Vote chair allowlist is empty")
    if any(not (3010000 <= item_id < 3020000) for item_id in chairs):
        fail("Vote chair allowlist contains a non-chair item ID")

    print("[PASS] Vote Point exchange policy audit")
    print(f"       prices={costs}")
    print(f"       cosmetic_chairs={len(chairs)}")
    print("       forbidden_direct_rewards=Chaos Scroll, White Scroll")


if __name__ == "__main__":
    main()

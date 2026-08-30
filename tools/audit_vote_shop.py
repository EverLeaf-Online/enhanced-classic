#!/usr/bin/env python3
"""Static policy checks for EverLeaf's Vote Point exchange.

The FM hub also hosts the separate PQ Point exchange, which is intentionally
allowed controlled Chaos/White access. These checks therefore inspect only the
Vote Point reward implementation, not the whole multi-currency NPC script.
"""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SHOP = ROOT / "scripts" / "npc" / "9030100.js"

FORBIDDEN_VOTE_REWARD_NAMES = [
    "CHAOS_SCROLL",
    "WHITE_SCROLL",
    "AP_RESET",
]

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
    raise SystemExit(f"[FAIL] {message}")


def main() -> None:
    if not SHOP.is_file():
        fail(f"Vote shop script missing: {SHOP.relative_to(ROOT)}")

    text = SHOP.read_text(encoding="utf-8")

    for snippet in REQUIRED_SNIPPETS:
        if snippet not in text:
            fail(f"Vote shop is missing required guard/policy marker: {snippet}")

    start = text.find("function showVoteExchange()")
    end = text.find("function pqService()")
    if start < 0 or end <= start:
        fail("Could not isolate Vote Point exchange implementation")
    vote_section = text[start:end]

    for forbidden in FORBIDDEN_VOTE_REWARD_NAMES:
        if forbidden in vote_section:
            fail(f"Vote Point exchange must not use progression reward constant: {forbidden}")

    costs = {
        name: int(value)
        for name, value in re.findall(r"var\s+(VOTE_[A-Z_]+_COST)\s*=\s*(\d+)\s*;", text)
    }
    expected_costs = {
        "VOTE_LEAF_COST",
        "VOTE_CHARM_COST",
        "VOTE_MERCHANT_COST",
        "VOTE_CHAIR_COST",
    }
    if set(costs) != expected_costs:
        fail(f"Unexpected Vote Point price set: {costs}")
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

    allowed_vote_reward_constants = {
        "MAPLE_LEAF",
        "SAFETY_CHARM",
        "HIRED_MERCHANT",
    }
    referenced = set(re.findall(r"\b[A-Z][A-Z0-9_]{3,}\b", vote_section))
    reward_constants = {name for name in referenced if name in {
        "MAPLE_LEAF", "SAFETY_CHARM", "HIRED_MERCHANT",
        "AP_RESET", "CHAOS_SCROLL", "WHITE_SCROLL"
    }}
    if not reward_constants.issubset(allowed_vote_reward_constants):
        fail(f"Vote exchange contains unapproved reward constants: {sorted(reward_constants)}")

    print("[PASS] Vote Point exchange policy audit")
    print(f"       prices={costs}")
    print(f"       cosmetic_chairs={len(chairs)}")
    print("       direct rewards=Maple Leaves, Safety Charms, Hired Merchant, cosmetic chair")
    print("       progression rewards=blocked")


if __name__ == "__main__":
    main()

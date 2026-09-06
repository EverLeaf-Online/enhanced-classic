#!/usr/bin/env python3
"""Static readiness checks for EverLeaf PQ Points and legacy event rewards."""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SERVICE = ROOT / "src/main/java/everleaf/progression/PqPointService.java"
MIGRATION = ROOT / "database/sql/migration/everleaf_pq_points.sql"
TRANSFORM = ROOT / "tools/apply_pq_points.py"
HOOK = ROOT / "src/main/java/everleaf/progression/PqPointClearHook.java"
SHOP = ROOT / "scripts/npc/9030100.js"

EXPECTED = {
    "HenesysPQ": 1,
    "KerningPQ": 1,
    "LudiPQ": 2,
    "LudiMazePQ": 2,
    "EllinPQ": 3,
    "OrbisPQ": 3,
    "PiratePQ": 3,
    "MagatiaPQ_A": 4,
    "MagatiaPQ_Z": 4,
    "AmoriaPQ": 4,
    "CWKPQ": 6,
}

EXPECTED_SHOP_COSTS = {
    "PQ_LEAF_COST": 5,
    "PQ_AP_RESET_COST": 4,
    "PQ_CHAIR_COST": 8,
    "PQ_CHAOS_COST": 25,
    "PQ_WHITE_COST": 120,
}

FORBIDDEN_AWARD_EVENTS = {
    "BossRushPQ",
    "ZakumBattle",
    "HorntailBattle",
    "PinkBeanBattle",
    "PapulatusBattle",
    "ScargaBattle",
}


def fail(message: str) -> None:
    raise SystemExit(f"[FAIL] {message}")


def read(path: Path) -> str:
    if not path.is_file():
        fail(f"Missing required file: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8")


def main() -> None:
    service = read(SERVICE)
    migration = read(MIGRATION)
    transform = read(TRANSFORM)
    hook = read(HOOK)
    shop = read(SHOP)

    parsed = {
        name: int(points)
        for name, points in re.findall(r'awards\.put\("([A-Za-z0-9_]+)",\s*(\d+)\);', service)
    }
    if parsed != EXPECTED:
        fail(f"PQ clear award table changed unexpectedly: {parsed}")

    for event in FORBIDDEN_AWARD_EVENTS:
        if event in parsed:
            fail(f"Boss/non-PQ event must not automatically award PQ Points: {event}")

    required_sql = [
        "everleaf_pq_point_balance",
        "everleaf_pq_point_ledger",
        "UNIQUE KEY `uq_everleaf_pq_points_reason`",
        "FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`) ON DELETE CASCADE",
    ]
    for token in required_sql:
        if token not in migration:
            fail(f"PQ Points migration missing safety requirement: {token}")

    if "PqPointClearHook.onEventCleared(em.getName(), name, getPlayers())" not in transform:
        fail("PQ Point build transform is not wired to the centralized event clear path")

    # The centralized clear transition must be idempotent. Without this guard,
    # duplicate script callbacks can award legacy Quest Points multiple times
    # even though the PQ Point ledger itself rejects duplicate reason keys.
    for token in ["synchronized (this)", "if (eventCleared)", "return;", "eventCleared = true;"]:
        if token not in transform:
            fail(f"PQ clear transform is missing idempotency guard: {token}")

    # Legacy randomized event rewards used by PQ completion NPCs must also be
    # exactly-once per character/reward level. Inventory-full failures must be
    # retryable and therefore must not reserve a claim.
    reward_guard_tokens = [
        "eventRewardClaims",
        "rewardClaimKey",
        "eventRewardClaims.contains(rewardClaimKey)",
        "eventRewardClaims.add(rewardClaimKey)",
        "if (!hasRewardSlot(player, eventLevel))",
        "return false;",
    ]
    for token in reward_guard_tokens:
        if token not in transform:
            fail(f"Legacy event reward transform is missing exactly-once guard: {token}")

    for token in ["clearAward(eventName)", "awardClear(", '"duplicate_reason"']:
        if token not in hook:
            fail(f"PQ Point clear hook missing guard: {token}")

    shop_costs = {
        name: int(value)
        for name, value in re.findall(r"var\s+(PQ_[A-Z_]+_COST)\s*=\s*(\d+)\s*;", shop)
    }
    if shop_costs != EXPECTED_SHOP_COSTS:
        fail(f"PQ shop price table changed unexpectedly: {shop_costs}")

    if shop_costs["PQ_WHITE_COST"] < shop_costs["PQ_CHAOS_COST"] * 4:
        fail("White Scroll must remain materially more expensive than Chaos Scroll")
    if shop_costs["PQ_CHAOS_COST"] <= max(parsed.values()):
        fail("Chaos Scroll must require multiple high-tier PQ clears")

    pq_start = shop.find("function showPqExchange()")
    pq_end = shop.find("function returnToPreviousLocation()")
    if pq_start < 0 or pq_end <= pq_start:
        fail("Could not isolate PQ Point shop implementation")
    pq_section = shop[pq_start:pq_end]

    for required in ["CHAOS_SCROLL", "WHITE_SCROLL", "MAPLE_LEAF", "AP_RESET", "pqChairs"]:
        if required not in pq_section:
            fail(f"PQ Point shop is missing expected controlled reward: {required}")

    # Keep direct equipment out of the PQ currency shop. Cosmetic chairs are
    # the only Setup equipment-like IDs permitted in this section.
    numeric_ids = [int(v) for v in re.findall(r"\b\d{7}\b", pq_section)]
    direct_equips = [item for item in numeric_ids if 1000000 <= item < 2000000]
    if direct_equips:
        fail(f"PQ shop must not sell direct equipment IDs: {direct_equips}")

    print("[PASS] PQ Points architecture/shop audit")
    print(f"       whitelisted_pqs={len(parsed)}")
    print(f"       clear_award_range={min(parsed.values())}-{max(parsed.values())}")
    print(f"       shop_costs={shop_costs}")
    print("       duplicate clear protection=event transition + unique account/reason ledger key")
    print("       legacy event reward protection=per-character/per-level claim guard")
    print("       boss-only events excluded from automatic PQ currency")
    print("       White Scroll cost >= 4x Chaos Scroll cost")


if __name__ == "__main__":
    main()

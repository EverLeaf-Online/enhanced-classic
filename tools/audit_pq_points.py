#!/usr/bin/env python3
"""Static readiness checks for EverLeaf PQ Points."""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SERVICE = ROOT / "src/main/java/everleaf/progression/PqPointService.java"
MIGRATION = ROOT / "database/sql/migration/everleaf_pq_points.sql"
TRANSFORM = ROOT / "tools/apply_pq_points.py"
HOOK = ROOT / "src/main/java/everleaf/progression/PqPointClearHook.java"

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

    for token in ["clearAward(eventName)", "awardClear(", '"duplicate_reason"']:
        if token not in hook:
            fail(f"PQ Point clear hook missing guard: {token}")

    print("[PASS] PQ Points architecture audit")
    print(f"       whitelisted_pqs={len(parsed)}")
    print(f"       award_range={min(parsed.values())}-{max(parsed.values())}")
    print("       duplicate clear protection=unique account/reason ledger key")
    print("       boss-only events excluded from automatic PQ currency")


if __name__ == "__main__":
    main()

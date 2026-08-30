#!/usr/bin/env python3
"""Static safety/readiness checks for EverLeaf Pet Vac."""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SERVICE = ROOT / "src/main/java/everleaf/progression/PetVacService.java"
ENTITLEMENTS = ROOT / "src/main/java/everleaf/progression/AccountEntitlementService.java"
MIGRATION = ROOT / "database/sql/migration/everleaf_account_entitlements.sql"
MOVE_HANDLER = ROOT / "src/main/java/net/server/channel/handlers/MovePetHandler.java"
SHOP = ROOT / "scripts/npc/9030100.js"


def fail(message: str) -> None:
    raise SystemExit(f"[FAIL] {message}")


def read(path: Path) -> str:
    if not path.is_file():
        fail(f"Missing required file: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8")


def const_number(text: str, name: str) -> float:
    m = re.search(rf"public static final (?:double|int|long)\s+{re.escape(name)}\s*=\s*([0-9.]+)", text)
    if not m:
        fail(f"Could not parse Pet Vac constant {name}")
    return float(m.group(1))


def main() -> None:
    service = read(SERVICE)
    entitlements = read(ENTITLEMENTS)
    migration = read(MIGRATION)
    move = read(MOVE_HANDLER)
    shop = read(SHOP)

    vac_range = const_number(service, "VACUUM_RANGE")
    max_items = int(const_number(service, "MAX_ITEMS_PER_TRIGGER"))
    cooldown = int(const_number(service, "TRIGGER_COOLDOWN_MS"))

    if vac_range > 300:
        fail(f"Pet Vac range is too large for the conservative release policy: {vac_range}")
    if max_items > 5:
        fail(f"Pet Vac attempts too many drops per trigger: {max_items}")
    if cooldown < 250:
        fail(f"Pet Vac trigger cooldown is too aggressive: {cooldown}ms")

    required_service_guards = [
        "chr.getEventInstance() != null",
        "chr.isEquippedMesoMagnet()",
        "chr.isEquippedItemPouch()",
        "chr.isEquippedPetItemIgnore()",
        "chr.getExcludedItems()",
        "chr.pickupItem(object, petIndex)",
        "AccountEntitlementService.PET_VAC",
        "active = false",
    ]
    for token in required_service_guards:
        if token not in service:
            fail(f"Pet Vac service is missing safety guard: {token}")

    if "PetVacService.getInstance().onPetMoved(player, player.getPet(slot), slot);" not in move:
        fail("Validated pet movement is not wired to the Pet Vac service")

    required_entitlement = [
        'public static final String PET_VAC = "PET_VAC"',
        "grantTimed(",
        "FOR UPDATE",
        "sourceAlreadyApplied(",
        "permanentResult()",
    ]
    for token in required_entitlement:
        if token not in entitlements:
            fail(f"Pet Vac entitlement service missing requirement: {token}")

    required_sql = [
        "everleaf_account_entitlement",
        "everleaf_account_entitlement_ledger",
        "UNIQUE KEY `uq_everleaf_entitlement_source`",
        "FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`) ON DELETE CASCADE",
    ]
    for token in required_sql:
        if token not in migration:
            fail(f"Account entitlement migration missing requirement: {token}")

    required_shop = [
        "VOTE_PET_VAC_7_COST = 5",
        "VOTE_PET_VAC_30_COST = 18",
        "purchasePetVac(7, VOTE_PET_VAC_7_COST)",
        "purchasePetVac(30, VOTE_PET_VAC_30_COST)",
        "Duration.ofDays(days)",
        '"VOTE_SHOP"',
        "addVotePoints(cost)",
        "invalidateEntitlementCache",
    ]
    for token in required_shop:
        if token not in shop:
            fail(f"Vote Point Pet Vac purchase path missing requirement: {token}")

    for forbidden in ["purchasePetVacPermanent", "VOTE_PET_VAC_PERMANENT_COST", "grantPermanent("]:
        if forbidden in shop:
            fail(f"Permanent Pet Vac is not approved for this release: {forbidden}")

    print("[PASS] Pet Vac safety/readiness audit")
    print(f"       range={vac_range}px max_items_per_trigger={max_items} cooldown={cooldown}ms")
    print("       event/PQ/boss instances=blocked")
    print("       item pouch/meso magnet + item-ignore rules=preserved")
    print("       final pickup authority=Character.pickupItem")
    print("       entitlement=account-wide timed 7d/30d with auditable grants")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Release-facing audit for EverLeaf stack and transfer integrity."""
from __future__ import annotations

import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIPULATOR = ROOT / "src/main/java/client/inventory/manipulator/InventoryManipulator.java"
INTERACTIONS = ROOT / "src/main/java/net/server/channel/handlers/PlayerInteractionHandler.java"
DUEY = ROOT / "src/main/java/client/processor/npc/DueyProcessor.java"
STORAGE = ROOT / "src/main/java/client/processor/npc/StorageProcessor.java"
PLAYER_SHOP = ROOT / "src/main/java/server/maps/PlayerShop.java"
HIRED_MERCHANT = ROOT / "src/main/java/server/maps/HiredMerchant.java"
ITEM = ROOT / "src/main/java/client/inventory/Item.java"
ITEM_FACTORY = ROOT / "src/main/java/client/inventory/ItemFactory.java"
ITEM_INFO = ROOT / "src/main/java/server/ItemInformationProvider.java"
ITEM_WZ = ROOT / "wz/Item.wz"


def read(path: Path) -> str:
    if not path.is_file():
        raise SystemExit(f"ERROR missing item integrity source: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8", errors="replace")


def require(path: Path, *fragments: str) -> None:
    data = read(path)
    for fragment in fragments:
        if fragment not in data:
            raise SystemExit(f"ERROR {path.relative_to(ROOT)} missing item integrity invariant: {fragment}")


def audit_stack_code() -> None:
    data = read(MANIPULATOR)
    for fragment in (
        "if (slotMax <= 0)",
        "ItemConstants.isPet(itemId) ? Long.MAX_VALUE : -1L",
        "eItem.getExpiration() == stackExpiration",
        "item.getExpiration() == eItem.getExpiration()",
        "checkSpace(Client c, int itemid, int quantity, String owner, long expiration)",
    ):
        if fragment not in data:
            raise SystemExit(f"ERROR stack integrity invariant missing: {fragment}")
    if data.count("if (slotMax <= 0)") < 3:
        raise SystemExit("ERROR slotMax fail-closed guard is not present in addById, addFromDrop, and checkSpace")

    require(
        PLAYER_SHOP,
        "InventoryManipulator.checkSpace(c, newItem.getItemId(), newItem.getQuantity(), newItem.getOwner(), newItem.getExpiration())",
    )
    require(
        HIRED_MERCHANT,
        "InventoryManipulator.checkSpace(c, newItem.getItemId(), newItem.getQuantity(), newItem.getOwner(), newItem.getExpiration())",
    )
    require(
        STORAGE,
        "InventoryManipulator.checkSpace(c, item.getItemId(), item.getQuantity(), item.getOwner(), item.getExpiration())",
    )
    require(
        DUEY,
        "InventoryManipulator.checkSpace(c, dpItem.getItemId(), dpItem.getQuantity(), dpItem.getOwner(), dpItem.getExpiration())",
    )


def audit_transfer_code() -> None:
    require(
        ITEM,
        "ItemConstants.UNTRADEABLE",
        "ItemInformationProvider.getInstance().isDropRestricted(this.getItemId())",
        "!KarmaManipulator.hasKarmaFlag(this)",
        "ItemConstants.ACCOUNT_SHARING",
        "public long getExpiration()",
        "public void setExpiration(long expire)",
    )

    interactions = read(INTERACTIONS)
    direct_runtime = "if (item.isUntradeable())"
    direct_wz = "if (ii.isDropRestricted(item.getItemId()))"
    shop_runtime = "if (ivItem == null || ivItem.isUntradeable())"
    shop_wz = "ItemInformationProvider.getInstance().isUnmerchable(ivItem.getItemId())"
    for fragment in (direct_runtime, direct_wz, shop_runtime, shop_wz):
        if fragment not in interactions:
            raise SystemExit(f"ERROR PlayerInteractionHandler transfer invariant missing: {fragment}")
    if interactions.index(direct_runtime) > interactions.index("if (quantity < 1 || quantity > item.getQuantity())"):
        raise SystemExit("ERROR direct trade runtime untradeable check occurs after quantity processing")

    require(
        DUEY,
        "item.isUntradeable() || ii.isUnmerchable(item.getItemId())",
        "KarmaManipulator.toggleKarmaFlagToUntradeable(item);",
    )

    require(
        ITEM_INFO,
        'DataTool.getIntConvert("info/tradeBlock", data, 0)',
        'DataTool.getIntConvert("info/accountSharable", data, 0)',
        'DataTool.getIntConvert("info/equipTradeBlock", getItemData(itemId), 0)',
        'DataTool.getIntConvert("info/tradeAvailable", getItemData(itemId), 0)',
    )

    factory = read(ITEM_FACTORY)
    if factory.count('setExpiration(rs.getLong("expiration"))') < 2:
        raise SystemExit("ERROR expiration is not restored for both regular items and equips")
    require(ITEM_FACTORY, "psItem.setLong(11, item.getExpiration());")


def audit_slotmax_data() -> tuple[int, int, int, Counter[int]]:
    if not ITEM_WZ.is_dir():
        raise SystemExit("ERROR Item.wz directory is missing")

    files = 0
    slot_nodes = 0
    max_slot = 0
    counts: Counter[int] = Counter()
    invalid: list[tuple[str, str]] = []

    for path in ITEM_WZ.rglob("*.xml"):
        files += 1
        try:
            root = ET.parse(path).getroot()
        except ET.ParseError as exc:
            raise SystemExit(f"ERROR malformed Item.wz XML {path.relative_to(ROOT)}: {exc}")

        for node in root.iter():
            if node.attrib.get("name") != "slotMax":
                continue
            raw = node.attrib.get("value")
            if raw is None:
                invalid.append((str(path.relative_to(ROOT)), "missing value"))
                continue
            try:
                value = int(raw)
            except ValueError:
                invalid.append((str(path.relative_to(ROOT)), raw))
                continue
            slot_nodes += 1
            counts[value] += 1
            max_slot = max(max_slot, value)
            if value <= 0 or value > 32767:
                invalid.append((str(path.relative_to(ROOT)), raw))

    if files < 10:
        raise SystemExit(f"ERROR suspiciously small Item.wz XML corpus: {files} files")
    if slot_nodes < 100:
        raise SystemExit(f"ERROR suspiciously few Item.wz slotMax nodes: {slot_nodes}")
    if invalid:
        sample = "; ".join(f"{path}={value}" for path, value in invalid[:20])
        raise SystemExit(f"ERROR invalid Item.wz slotMax values ({len(invalid)}): {sample}")

    return files, slot_nodes, max_slot, counts


def main() -> int:
    audit_stack_code()
    audit_transfer_code()
    files, slot_nodes, max_slot, counts = audit_slotmax_data()

    print("EverLeaf item transfer/stack integrity audit: PASS")
    print("  runtime UNTRADEABLE: direct trade + player shop + Duey gated")
    print("  WZ tradeBlock/accountSharable/equipTradeBlock/tradeAvailable: wired")
    print("  Karma-aware direct trade gate: retained")
    print("  expiration persistence: regular items + equips save/load wired")
    print("  stack merges: owner + flag + expiration compatible")
    print("  capacity preflight: PlayerShop/HiredMerchant/Storage/Duey expiration-aware")
    print("  malformed slotMax: add/preflight paths fail closed")
    print(f"  Item.wz XML files parsed: {files}")
    print(f"  explicit slotMax nodes validated: {slot_nodes}")
    print(f"  maximum explicit slotMax: {max_slot}")
    print("  most common slotMax values: " + ", ".join(f"{value}={count}" for value, count in counts.most_common(8)))
    print("  NOTE: Duey/merchant settlement atomicity remains a separate concurrency follow-up")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

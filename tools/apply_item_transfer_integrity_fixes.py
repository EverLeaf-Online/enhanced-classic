#!/usr/bin/env python3
"""Apply deterministic EverLeaf transfer-integrity fixes.

Direct player trade historically checked WZ merch/drop restrictions but omitted
Item.isUntradeable(), unlike Player Shops and Duey. That can allow an item carrying
the runtime UNTRADEABLE flag to enter a direct trade when its WZ metadata alone is
not restricted. Keep the existing Karma-aware WZ gate as defense in depth.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "src/main/java/net/server/channel/handlers/PlayerInteractionHandler.java"


def main() -> int:
    text = TARGET.read_text(encoding="utf-8")

    old = """                if (ii.isUnmerchable(item.getItemId())) {
                    if (ItemConstants.isPet(item.getItemId())) {
                        c.sendPacket(PacketCreator.serverNotice(1, \"Pets are not allowed to be traded.\"));
                    } else {
                        c.sendPacket(PacketCreator.serverNotice(1, \"Cash items are not allowed to be traded.\"));
                    }

                    c.sendPacket(PacketCreator.enableActions());
                    return;
                }

                if (quantity < 1 || quantity > item.getQuantity()) {
"""
    new = """                if (ii.isUnmerchable(item.getItemId())) {
                    if (ItemConstants.isPet(item.getItemId())) {
                        c.sendPacket(PacketCreator.serverNotice(1, \"Pets are not allowed to be traded.\"));
                    } else {
                        c.sendPacket(PacketCreator.serverNotice(1, \"Cash items are not allowed to be traded.\"));
                    }

                    c.sendPacket(PacketCreator.enableActions());
                    return;
                }

                if (item.isUntradeable()) {
                    c.sendPacket(PacketCreator.serverNotice(1, \"That item is untradeable.\"));
                    c.sendPacket(PacketCreator.enableActions());
                    return;
                }

                if (quantity < 1 || quantity > item.getQuantity()) {
"""

    if new in text:
        print("OK already fixed: direct trade runtime untradeable gate")
    elif old in text:
        text = text.replace(old, new, 1)
        TARGET.write_text(text, encoding="utf-8")
        print("FIXED: direct trade runtime untradeable gate")
    else:
        raise SystemExit("ERROR direct-trade item validation snippet not found")

    final = TARGET.read_text(encoding="utf-8")
    runtime_guard = "if (item.isUntradeable())"
    wz_guard = "if (ii.isDropRestricted(item.getItemId()))"
    quantity_guard = "if (quantity < 1 || quantity > item.getQuantity())"
    if runtime_guard not in final or wz_guard not in final:
        raise SystemExit("ERROR direct trade runtime/WZ transfer guards are not both present")
    if final.index(runtime_guard) > final.index(quantity_guard):
        raise SystemExit("ERROR runtime untradeable validation occurs too late")

    print("EverLeaf item transfer integrity fixes: PASS")
    print("  direct trade runtime UNTRADEABLE flag: enforced")
    print("  WZ drop restriction + Karma gate: retained")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

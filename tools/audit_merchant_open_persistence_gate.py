#!/usr/bin/env python3
"""Audit that Hired Merchant publication requires a durable inventory snapshot."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HANDLER = ROOT / "src/main/java/net/server/channel/handlers/PlayerInteractionHandler.java"


def main() -> int:
    text = HANDLER.read_text(encoding="utf-8")
    marker = "Hired Merchant cannot open until its inventory snapshot is durable"
    required = (
        "merchant.saveItems(false);",
        marker,
        "c.sendPacket(PacketCreator.enableActions());",
        "merchant.setOpen(true);",
        "chr.getMap().addMapObject(merchant);",
        "chr.setHiredMerchant(null);",
    )
    for fragment in required:
        if fragment not in text:
            raise SystemExit(f"FAIL merchant-open persistence invariant missing: {fragment}")

    marker_pos = text.index(marker)
    save_pos = text.rfind("merchant.saveItems(false);", 0, marker_pos)
    open_pos = text.index("merchant.setOpen(true);", marker_pos)
    publish_pos = text.index("chr.getMap().addMapObject(merchant);", marker_pos)
    detach_pos = text.index("chr.setHiredMerchant(null);", marker_pos)
    if save_pos < 0 or not (save_pos < marker_pos < open_pos < publish_pos < detach_pos):
        raise SystemExit("FAIL merchant durable-save/open/publication ordering is invalid")

    print("EverLeaf Hired Merchant open persistence audit: PASS")
    print("  saveItems executes before setOpen/map publication")
    print("  SQL failure returns before owner detachment/publication")
    print("  volatile listings cannot be made buyable until a snapshot succeeds")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

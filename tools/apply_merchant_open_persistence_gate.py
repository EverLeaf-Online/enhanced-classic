#!/usr/bin/env python3
"""Require a durable Hired Merchant snapshot before publishing the shop."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HANDLER = ROOT / "src/main/java/net/server/channel/handlers/PlayerInteractionHandler.java"


def main() -> int:
    text = HANDLER.read_text(encoding="utf-8")
    marker = "Hired Merchant cannot open until its inventory snapshot is durable"
    if marker in text:
        print("OK already fixed: Hired Merchant open persistence gate")
    else:
        old = '''                } else if (merchant != null && merchant.isOwner(chr)) {\n                    chr.setHasMerchant(true);\n                    merchant.setOpen(true);\n                    chr.getMap().addMapObject(merchant);\n                    chr.setHiredMerchant(null);\n                    chr.getMap().broadcastMessage(PacketCreator.spawnHiredMerchantBox(merchant));\n                }\n'''
        new = '''                } else if (merchant != null && merchant.isOwner(chr)) {\n                    try {\n                        merchant.saveItems(false);\n                    } catch (SQLException ex) {\n                        log.error("Hired Merchant cannot open until its inventory snapshot is durable for chr {}", chr.getName(), ex);\n                        c.sendPacket(PacketCreator.serverNotice(1, "Your merchant could not be saved, so it was not opened. Please try again."));\n                        c.sendPacket(PacketCreator.enableActions());\n                        return;\n                    }\n\n                    chr.setHasMerchant(true);\n                    merchant.setOpen(true);\n                    chr.getMap().addMapObject(merchant);\n                    chr.setHiredMerchant(null);\n                    chr.getMap().broadcastMessage(PacketCreator.spawnHiredMerchantBox(merchant));\n                }\n'''
        if old not in text:
            raise SystemExit("ERROR expected Hired Merchant open snippet not found")
        HANDLER.write_text(text.replace(old, new, 1), encoding="utf-8")
        print("FIXED: Hired Merchant open persistence gate")

    final = HANDLER.read_text(encoding="utf-8")
    required = (
        "merchant.saveItems(false);",
        "Hired Merchant cannot open until its inventory snapshot is durable",
        "merchant.setOpen(true);",
        "chr.getMap().addMapObject(merchant);",
    )
    for fragment in required:
        if fragment not in final:
            raise SystemExit(f"ERROR merchant-open persistence invariant missing: {fragment}")

    durable = final.index("Hired Merchant cannot open until its inventory snapshot is durable")
    opened = final.index("merchant.setOpen(true);", durable)
    if durable > opened:
        raise SystemExit("ERROR merchant is opened before durable snapshot gate")

    print("EverLeaf Hired Merchant open persistence gate: PASS")
    print("  owner-open attempts persist merchant stock before publication")
    print("  SQL failure leaves merchant closed and owner-attached")
    print("  map publication and setOpen(true) occur only after saveItems succeeds")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

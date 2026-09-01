#!/usr/bin/env python3
"""Release gate for player-facing Duey package ownership invariants."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DUEY = ROOT / "src/main/java/client/processor/npc/DueyProcessor.java"


def main() -> int:
    text = DUEY.read_text(encoding="utf-8", errors="replace")
    required = (
        'private static boolean removeOwnedPackageFromDB(int packageId, int receiverId)',
        'DELETE FROM dueypackages WHERE PackageId = ? AND ReceiverId = ?',
        'removeOwnedPackageFromDB(packageid, c.getPlayer().getId())',
        'SELECT * FROM dueypackages dp WHERE PackageId = ? AND ReceiverId = ?',
        'ps.setInt(2, c.getPlayer().getId());',
        'if (dp == null)',
        'if (dp.isDeliveringTime())',
        'removePackageFromDB(pid);',
        'InventoryManipulator.checkSpace(c, dpItem.getItemId(), dpItem.getQuantity(), dpItem.getOwner(), dpItem.getExpiration())',
    )
    for fragment in required:
        if fragment not in text:
            raise SystemExit(f"ERROR Duey ownership invariant missing: {fragment}")

    # Player remove must no longer invoke the trusted package-id-only helper.
    player_remove_start = text.index("public static void dueyRemovePackage")
    player_claim_start = text.index("public static void dueyClaimPackage")
    player_remove = text[player_remove_start:player_claim_start]
    if "removePackageFromDB(packageid);" in player_remove:
        raise SystemExit("ERROR player Duey remove still uses unowned package-id-only deletion")

    # Claim query must bind the client-supplied package id to the logged-in character.
    claim_end = text.index("public static void dueySendTalk", player_claim_start)
    claim = text[player_claim_start:claim_end]
    if 'WHERE PackageId = ?"' in claim:
        raise SystemExit("ERROR player Duey claim retains package-id-only lookup")

    print("EverLeaf Duey ownership audit: PASS")
    print("  forged package claim ids: receiver-bound")
    print("  forged package remove ids: receiver-bound")
    print("  missing/foreign package behavior: fail closed")
    print("  trusted expiry cleanup: preserved")
    print("  timed-item claim preflight: expiration-aware")
    print("  NOTE: send/claim settlement atomicity remains the next Duey hardening slice")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

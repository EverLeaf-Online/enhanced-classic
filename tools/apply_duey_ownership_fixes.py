#!/usr/bin/env python3
"""Apply deterministic Duey package-ownership hardening.

Player-originated claim/remove packets carry a package id chosen by the client.
Every such operation must bind that id to the currently authenticated character's
ReceiverId. Trusted server cleanup keeps its package-id-only path.

This transform is intentionally composition-safe: later Duey transforms may
strengthen the receiver-bound helper while preserving its ownership invariant.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "src/main/java/client/processor/npc/DueyProcessor.java"


def replace_once(text: str, old: str, new: str, label: str) -> tuple[str, bool]:
    if new in text:
        print(f"OK already fixed: {label}")
        return text, False
    if old not in text:
        raise SystemExit(f"ERROR expected Duey snippet not found: {label}")
    print(f"FIXED: {label}")
    return text.replace(old, new, 1), True


def main() -> int:
    text = TARGET.read_text(encoding="utf-8")
    changed = False

    trusted_remove = """    private static void removePackageFromDB(int packageId) {
        try (Connection con = DatabaseConnection.getConnection();
             PreparedStatement ps = con.prepareStatement(\"DELETE FROM dueypackages WHERE PackageId = ?\")) {
            ps.setInt(1, packageId);
            ps.executeUpdate();

            deletePackageFromInventoryDB(con, packageId);
        } catch (SQLException e) {
            e.printStackTrace();
        }
    }
"""
    trusted_and_owned = trusted_remove + """
    private static boolean removeOwnedPackageFromDB(int packageId, int receiverId) {
        try (Connection con = DatabaseConnection.getConnection();
             PreparedStatement ps = con.prepareStatement(\"DELETE FROM dueypackages WHERE PackageId = ? AND ReceiverId = ?\")) {
            ps.setInt(1, packageId);
            ps.setInt(2, receiverId);
            int removed = ps.executeUpdate();
            if (removed != 1) {
                return false;
            }

            deletePackageFromInventoryDB(con, packageId);
            return true;
        } catch (SQLException e) {
            log.error(\"Failed to remove owned Duey package {} for receiver {}\", packageId, receiverId, e);
            return false;
        }
    }
"""
    if "private static boolean removeOwnedPackageFromDB(int packageId, int receiverId)" in text:
        print("OK already fixed: receiver-bound package deletion helper")
    else:
        text, did = replace_once(text, trusted_remove, trusted_and_owned, "receiver-bound package deletion helper")
        changed |= did

    old_remove = """    public static void dueyRemovePackage(Client c, int packageid, boolean playerRemove) {
        if (c.tryacquireClient()) {
            try {
                removePackageFromDB(packageid);
                c.sendPacket(PacketCreator.removeItemFromDuey(playerRemove, packageid));
            } finally {
                c.releaseClient();
            }
        }
    }
"""
    new_remove = """    public static void dueyRemovePackage(Client c, int packageid, boolean playerRemove) {
        if (c.tryacquireClient()) {
            try {
                if (!removeOwnedPackageFromDB(packageid, c.getPlayer().getId())) {
                    log.warn(\"Chr {} attempted to remove unavailable Duey package {}\", c.getPlayer().getName(), packageid);
                    c.sendPacket(PacketCreator.sendDueyMSG(Actions.TOCLIENT_RECV_UNKNOWN_ERROR.getCode()));
                    return;
                }
                c.sendPacket(PacketCreator.removeItemFromDuey(playerRemove, packageid));
            } finally {
                c.releaseClient();
            }
        }
    }
"""
    text, did = replace_once(text, old_remove, new_remove, "player remove ownership gate")
    changed |= did

    old_claim = """                    try (Connection con = DatabaseConnection.getConnection();
                         PreparedStatement ps = con.prepareStatement(\"SELECT * FROM dueypackages dp WHERE PackageId = ?\")) {
                        ps.setInt(1, packageId);

                        try (ResultSet rs = ps.executeQuery()) {
"""
    new_claim = """                    try (Connection con = DatabaseConnection.getConnection();
                         PreparedStatement ps = con.prepareStatement(\"SELECT * FROM dueypackages dp WHERE PackageId = ? AND ReceiverId = ?\")) {
                        ps.setInt(1, packageId);
                        ps.setInt(2, c.getPlayer().getId());

                        try (ResultSet rs = ps.executeQuery()) {
"""
    text, did = replace_once(text, old_claim, new_claim, "claim lookup ownership gate")
    changed |= did

    if changed:
        TARGET.write_text(text, encoding="utf-8")

    final = TARGET.read_text(encoding="utf-8")
    required = (
        'private static boolean removeOwnedPackageFromDB(int packageId, int receiverId)',
        'DELETE FROM dueypackages WHERE PackageId = ? AND ReceiverId = ?',
        'removeOwnedPackageFromDB(packageid, c.getPlayer().getId())',
        'SELECT * FROM dueypackages dp WHERE PackageId = ? AND ReceiverId = ?',
        'ps.setInt(2, c.getPlayer().getId());',
        'removePackageFromDB(pid);',
    )
    for fragment in required:
        if fragment not in final:
            raise SystemExit(f"ERROR Duey ownership invariant missing: {fragment}")

    print("EverLeaf Duey ownership hardening: PASS")
    print("  player claim: package id + authenticated ReceiverId")
    print("  player delete: package id + authenticated ReceiverId")
    print("  trusted expiry cleanup: package-id-only helper preserved")
    print("  transform composition/idempotency: later helper strengthening accepted")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Verify that known EverLeaf non-Empress features remain on canonical branches.

This is intentionally behavior-marker based rather than commit-SHA based.  Old
feature branches were often squashed, cherry-picked, or superseded by stronger
implementations, so ancestry alone cannot prove that a QoL/security feature
survived consolidation.
"""
from __future__ import annotations

import subprocess
import sys

CANONICAL = {
    "server": "origin/release-dev",
    "web": "origin/master",
    "client": "origin/client-dev",
}

# (area, path, all required markers)
CHECKS = [
    # Core progression / QoL
    ("server", "src/main/java/constants/game/ExpTable.java", ["250"]),
    ("server", "src/main/java/net/server/channel/handlers/EnterMTSHandler.java", ["getTrade()", "getPlayerShop()", "getHiredMerchant()"]),
    ("server", "src/main/java/server/Storage.java", ["currentNpcid", "currentMapId", "isStorageOpen"]),
    ("server", "src/main/java/net/server/channel/handlers/NPCShopHandler.java", ["tryacquireClient", "getShop", "getPosition"]),
    ("server", "src/main/java/net/server/channel/handlers/ItemMoveHandler.java", ["tryacquireClient", "InventoryType.UNDEFINED", "EquipmentRequirements.canEquipForJob"]),
    ("server", "src/main/java/server/events/gm/Ola.java", ["generateCorrectPortals", "isCorrectPortal", "STAGE_PORTAL_COUNTS"]),

    # Evan current release scope
    ("server", "src/main/java/client/Character.java", ["EVAN"]),
    ("server", "src/main/java/constants/skills/Evan.java", ["DRAGON_FURY", "MAGIC_RESISTANCE"]),
    ("server", "scripts/npc/2007.js", ["Evan"]),

    # Transaction / economy hardening surfaces
    ("server", "src/main/java/server/shops/HiredMerchant.java", ["synchronized"]),
    ("server", "src/main/java/server/shops/PlayerShop.java", ["synchronized"]),
    ("server", "src/main/java/net/server/channel/handlers/StorageHandler.java", ["isStorageOpen"]),

    # Client / launcher safety
    ("server", "launcher/EverLeaf.Launcher/BoundedDownload.cs", ["ContentLength", "expectedSize"]),
    ("server", "launcher/EverLeaf.Launcher/LaunchTicket.cs", [".everleaf-launch", "CleanupStale"]),
    ("server", "launcher/EverLeaf.Launcher/MainWindow.xaml.cs", ["LaunchTicket"]),
    ("client", "client/tools/evan-xml-donor-builder/main.cpp", ["MapleLib"]),

    # Website / CMS / account / Wiki / voting
    ("web", "web/src/views/account.ejs", ["VOTE FOR NX", "Pending Vote NX", "accountQuick"]),
    ("web", "web/src/routes/vote.js", ["timingSafeEqual", "queueVerifiedVoteNx", "gtop100.com"]),
    ("web", "web/scripts/backup-mysql.js", ["--single-transaction", "--protocol=socket", "Intentionally do not use --databases"]),
    ("web", "web/src/routes/wiki.js", ["wikiCatalog"]),
    ("web", "web/src/views/wiki-entry.ejs", ["provenance"]),
    ("web", "web/src/views/admin.ejs", ["admin"]),
    ("web", "web/src/views/rankings.ejs", ["rank"]),
]


def run(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    p = subprocess.run(args, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if check and p.returncode:
        raise RuntimeError(f"command failed: {' '.join(args)}\n{p.stderr}")
    return p


def read_ref(ref: str, path: str) -> str | None:
    p = run("git", "show", f"{ref}:{path}", check=False)
    return p.stdout if p.returncode == 0 else None


def main() -> int:
    failures: list[str] = []
    passed = 0
    for area, path, markers in CHECKS:
        ref = CANONICAL[area]
        text = read_ref(ref, path)
        if text is None:
            failures.append(f"{area}: missing {path} on {ref}")
            continue
        missing = [marker for marker in markers if marker not in text]
        if missing:
            failures.append(f"{area}: {path} missing marker(s): {', '.join(missing)}")
            continue
        passed += 1

    # Policy guard: Empress and Community-files are reference/excluded lines,
    # never canonical release inputs.
    canonical_values = set(CANONICAL.values())
    for forbidden in ("origin/empress-dev", "origin/Community-files"):
        if forbidden in canonical_values:
            failures.append(f"excluded branch became canonical: {forbidden}")

    print(f"Canonical feature audit: {passed}/{len(CHECKS)} checks passed")
    for failure in failures:
        print(f"[FAIL] {failure}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())

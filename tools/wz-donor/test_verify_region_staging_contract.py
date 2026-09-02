#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import tempfile
from pathlib import Path

from verify_region_staging_contract import verify


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        core7 = root / "core7.zip"
        string = root / "string.zip"
        core7.write_bytes(b"core7-fixture")
        string.write_bytes(b"string-fixture")
        portal = root / "scripts" / "portal" / "ninja_Boss.js"
        portal.parent.mkdir(parents=True)
        portal.write_text('function enter(pi) { pi.warp(800040410, "out00"); return true; }\n', encoding="utf-8")

        contract = {
            "batchId": "fixture",
            "approved": False,
            "importAllowed": False,
            "automaticImport": False,
            "productionApplyAllowed": False,
            "evidence": {"core7ArchiveSha256": sha(core7), "stringArchiveSha256": sha(string)},
            "maps": ["800040000"],
            "mobs": ["9400408", "9400409"],
            "castleNpcs": ["9110100"],
            "questDependencyNpcs": ["1002101", "9110002"],
            "items": ["4000337"],
            "seedQuestIds": ["8165"],
            "questIds": ["8163", "8164", "8165"],
            "prerequisiteQuestIds": ["8163", "8164"],
            "prerequisiteEdges": {"8164": ["8163"], "8165": ["8164"]},
            "portalTargets": ["800040000"],
            "portalScript": {
                "path": "scripts/portal/ninja_Boss.js",
                "sha256": sha(portal),
                "targetMap": "800040410",
                "targetPortal": "out00",
            },
            "mobDependencyAssertions": {
                "reviveDependencyMobsAdded": [],
                "9400408": {"reviveMobs": ["9400409"]},
            },
            "deliberateReplacementCollisions": [{
                "family": "Npc.wz",
                "contentId": "9110100",
                "donorFingerprint": "donor-hash",
                "baselineFingerprint": "baseline-hash",
                "baselineReferenceCount": 1,
                "baselineReferenceFiles": ["wz/Etc.wz/NpcLocation.img.xml"],
            }],
        }
        profile = {
            "clusterId": "gms-v95-ninja-castle-review",
            "approved": False,
            "importAllowed": False,
            "automaticImport": False,
            "maps": [{"contentId": "800040000"}],
            "mobs": [{"contentId": "9400408"}, {"contentId": "9400409"}],
            "npcs": [{"contentId": "9110100"}],
            "items": ["4000337"],
            "portalTargets": [{"mapId": "800040000"}],
            "reviveDependencyMobsAdded": [],
            "mobDependencies": {"9400408": {"reviveMobs": ["9400409"], "linkedMobs": []}},
            "blockingReview": {"missingPortalScripts": [], "unresolvedPortalTargets": []},
            "changedCollisions": [{
                "contentId": "9110100",
                "family": "Npc.wz",
                "donorFingerprint": "donor-hash",
                "baselineFingerprint": "baseline-hash",
                "baselineReferences": {
                    "referenceCount": 1,
                    "samples": [{"path": "wz/Etc.wz/NpcLocation.img.xml", "matches": 1}],
                },
                "proposedDormantReplacementCandidate": True,
                "replacementApproved": False,
            }],
        }
        quest = {
            "approved": False,
            "importAllowed": False,
            "automaticImport": False,
            "seedQuestIds": ["8165"],
            "questIds": ["8163", "8164", "8165"],
            "prerequisiteQuestIds": ["8163", "8164"],
            "prerequisiteEdges": {"8164": ["8163"], "8165": ["8164"]},
            "npcIds": ["1002101", "9110002"],
        }

        result = verify(contract, profile, quest, core7, string, root)
        assert result["passed"] is True, result["errors"]
        assert result["productionApplyAllowed"] is False

        drifted = dict(profile)
        drifted["changedCollisions"] = [dict(profile["changedCollisions"][0])]
        drifted["changedCollisions"][0]["baselineFingerprint"] = "unexpected"
        result = verify(contract, drifted, quest, core7, string, root)
        assert result["passed"] is False
        assert any("baseline fingerprint drifted" in e for e in result["errors"])

        portal.write_text('function enter(pi) { pi.warp(999999999, "bad"); }\n', encoding="utf-8")
        result = verify(contract, profile, quest, core7, string, root)
        assert result["passed"] is False
        assert any("portal script hash drifted" in e for e in result["errors"])

    print("region staging contract verifier regression: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

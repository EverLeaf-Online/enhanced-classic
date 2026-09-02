#!/usr/bin/env python3
"""Fail-closed verifier for a review-only regional WZ staging contract."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def ids(rows):
    return [str(row["contentId"]) for row in rows]


def norm_edges(value):
    return {str(k): [str(x) for x in v] for k, v in value.items()}


def verify(contract, profile, quest, core7: Path, string: Path, repo_root: Path):
    errors = []

    def check(condition, message):
        if not condition:
            errors.append(message)

    check(contract.get("approved") is False, "contract approved must remain false")
    check(contract.get("importAllowed") is False, "contract importAllowed must remain false")
    check(contract.get("automaticImport") is False, "contract automaticImport must remain false")
    check(contract.get("productionApplyAllowed") is False, "contract productionApplyAllowed must remain false")

    evidence = contract["evidence"]
    check(sha256(core7) == evidence["core7ArchiveSha256"], "core7 archive SHA-256 drifted")
    check(sha256(string) == evidence["stringArchiveSha256"], "String archive SHA-256 drifted")

    check(profile.get("approved") is False, "profile approved must remain false")
    check(profile.get("importAllowed") is False, "profile importAllowed must remain false")
    check(profile.get("automaticImport") is False, "profile automaticImport must remain false")
    check(profile.get("clusterId") == "gms-v95-ninja-castle-review", "unexpected regional profile clusterId")

    check(ids(profile["maps"]) == contract["maps"], "map closure drifted")
    check(ids(profile["mobs"]) == contract["mobs"], "mob closure drifted")
    check(ids(profile["npcs"]) == contract["castleNpcs"], "castle NPC closure drifted")
    check([str(x) for x in profile["items"]] == contract["items"], "item closure drifted")
    check([str(x["mapId"]) for x in profile["portalTargets"]] == contract["portalTargets"], "portal target closure drifted")
    check(profile.get("reviveDependencyMobsAdded", []) == contract["mobDependencyAssertions"]["reviveDependencyMobsAdded"], "revive dependency expansion drifted")

    for mob_id, expected in contract["mobDependencyAssertions"].items():
        if mob_id == "reviveDependencyMobsAdded":
            continue
        actual = profile.get("mobDependencies", {}).get(mob_id, {})
        check(actual.get("reviveMobs", []) == expected.get("reviveMobs", []), f"mob {mob_id} revive dependency drifted")

    blocking = profile.get("blockingReview", {})
    check(blocking.get("missingPortalScripts", []) == [], "regional profile still has missing portal scripts")
    check(blocking.get("unresolvedPortalTargets", []) == [], "regional profile has unresolved portal targets")

    expected_collisions = {x["contentId"]: x for x in contract["deliberateReplacementCollisions"]}
    actual_collisions = {str(x["contentId"]): x for x in profile.get("changedCollisions", [])}
    check(set(actual_collisions) == set(expected_collisions), "changed collision set drifted")
    for cid, expected in expected_collisions.items():
        actual = actual_collisions.get(cid)
        if actual is None:
            continue
        check(actual.get("family") == expected["family"], f"collision {cid} family drifted")
        check(actual.get("donorFingerprint") == expected["donorFingerprint"], f"collision {cid} donor fingerprint drifted")
        check(actual.get("baselineFingerprint") == expected["baselineFingerprint"], f"collision {cid} baseline fingerprint drifted")
        refs = actual.get("baselineReferences", {})
        check(refs.get("referenceCount") == expected["baselineReferenceCount"], f"collision {cid} baseline reference count drifted")
        files = sorted(x["path"] for x in refs.get("samples", []))
        check(files == sorted(expected["baselineReferenceFiles"]), f"collision {cid} baseline reference files drifted")
        check(actual.get("proposedDormantReplacementCandidate") is True, f"collision {cid} no longer qualifies as dormant replacement candidate")
        check(actual.get("replacementApproved") is False, f"collision {cid} replacementApproved must remain false")

    check(quest.get("approved") is False, "quest evidence approved must remain false")
    check(quest.get("importAllowed") is False, "quest evidence importAllowed must remain false")
    check(quest.get("automaticImport") is False, "quest evidence automaticImport must remain false")
    check([str(x) for x in quest.get("seedQuestIds", [])] == contract["seedQuestIds"], "seed quest set drifted")
    check([str(x) for x in quest.get("questIds", [])] == contract["questIds"], "expanded quest closure drifted")
    check([str(x) for x in quest.get("prerequisiteQuestIds", [])] == contract["prerequisiteQuestIds"], "prerequisite quest set drifted")
    check(norm_edges(quest.get("prerequisiteEdges", {})) == norm_edges(contract["prerequisiteEdges"]), "prerequisite quest edges drifted")
    check([str(x) for x in quest.get("npcIds", [])] == contract["questDependencyNpcs"], "quest NPC closure drifted")

    portal = contract["portalScript"]
    portal_path = repo_root / portal["path"]
    check(portal_path.is_file(), "ninja_Boss portal script is missing")
    if portal_path.is_file():
        check(sha256(portal_path) == portal["sha256"], "ninja_Boss portal script hash drifted")
        text = portal_path.read_text(encoding="utf-8")
        check(str(portal["targetMap"]) in text and str(portal["targetPortal"]) in text, "ninja_Boss portal destination drifted")

    result = {
        "schemaVersion": 1,
        "kind": "review-only-region-staging-contract-verification",
        "batchId": contract["batchId"],
        "passed": not errors,
        "errors": errors,
        "counts": {
            "maps": len(contract["maps"]),
            "mobs": len(contract["mobs"]),
            "castleNpcs": len(contract["castleNpcs"]),
            "questDependencyNpcs": len(contract["questDependencyNpcs"]),
            "items": len(contract["items"]),
            "quests": len(contract["questIds"]),
            "portalTargets": len(contract["portalTargets"]),
            "deliberateReplacementCollisions": len(contract["deliberateReplacementCollisions"]),
        },
        "approved": False,
        "importAllowed": False,
        "automaticImport": False,
        "productionApplyAllowed": False,
    }
    return result


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("contract", type=Path)
    p.add_argument("--profile", type=Path, required=True)
    p.add_argument("--quest-evidence", type=Path, required=True)
    p.add_argument("--core7-archive", type=Path, required=True)
    p.add_argument("--string-archive", type=Path, required=True)
    p.add_argument("--repo-root", type=Path, default=Path("."))
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()

    result = verify(
        json.loads(a.contract.read_text(encoding="utf-8")),
        json.loads(a.profile.read_text(encoding="utf-8")),
        json.loads(a.quest_evidence.read_text(encoding="utf-8")),
        a.core7_archive,
        a.string_archive,
        a.repo_root,
    )
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["counts"], sort_keys=True))
    if result["errors"]:
        for error in result["errors"]:
            print("ERROR:", error)
        return 1
    print("staging contract verified; approved=false / productionApplyAllowed=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

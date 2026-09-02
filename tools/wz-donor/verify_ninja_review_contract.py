#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

EXPECTED_COUNTS = {
    "mapIds": 33,
    "mobIds": 11,
    "npcIds": 15,
    "reactorIds": 0,
    "itemIds": 10,
    "questIds": 7,
}

FALSE_FLAGS = (
    "approved",
    "applyAllowed",
    "automaticApply",
    "importAllowed",
    "automaticImport",
)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def verify(contract_path: Path, quest_drop_path: Path, portal_path: Path) -> list[str]:
    errors: list[str] = []
    contract = load_json(contract_path)
    drops = load_json(quest_drop_path)
    portal = portal_path.read_text(encoding="utf-8")

    if contract.get("mode") != "extraction-only-review":
        errors.append("contract mode must remain extraction-only-review")

    closure = contract.get("closure", {})
    for key, expected in EXPECTED_COUNTS.items():
        actual = len(closure.get(key, []))
        if actual != expected:
            errors.append(f"{key} count drifted: expected {expected}, got {actual}")

    if closure.get("mapIds", [None])[0] != 800040000 or closure.get("mapIds", [None])[-1] != 800040410:
        errors.append("Ninja Castle map closure endpoints drifted")
    if closure.get("mobIds") != list(range(9400400, 9400411)):
        errors.append("Ninja Castle mob closure must remain 9400400-9400410")
    if closure.get("npcIds") != list(range(9110100, 9110115)):
        errors.append("Ninja Castle NPC closure must remain 9110100-9110114")
    if closure.get("itemIds") != list(range(4000337, 4000347)):
        errors.append("Ninja Castle item closure must remain 4000337-4000346")
    if closure.get("questIds") != list(range(8165, 8172)):
        errors.append("Ninja Castle quest closure must remain 8165-8171")

    collision = contract.get("collisionPolicy", {}).get("9110100", {})
    if collision.get("donorFingerprint") != "40bc1006d76ee175a06a1954dffb130e8687bc9d52cf6c99e77ad0c9a157b3e1":
        errors.append("9110100 donor fingerprint drifted")
    if collision.get("baselineFingerprint") != "e1f35d4998091f6fa5e269641e8d2036c5c2adcaf3f8b48975bf5163a4e9fcac":
        errors.append("9110100 baseline fingerprint drifted")
    if collision.get("baselineReferenceCount") != 1:
        errors.append("9110100 baseline reference count must remain 1 until re-reviewed")
    if collision.get("baselineReferenceFiles") != ["wz/Etc.wz/NpcLocation.img.xml"]:
        errors.append("9110100 baseline reference file set drifted")
    if collision.get("decision") != "deliberate-replacement-review":
        errors.append("9110100 collision decision drifted")
    if collision.get("blockIfFingerprintChanges") is not True:
        errors.append("9110100 must remain fail-closed on fingerprint drift")

    mob_policy = contract.get("mobDependencyPolicy", {})
    if mob_policy.get("reviveEdges") != [{"from": 9400408, "to": 9400409}]:
        errors.append("Emperor Toad revive edge drifted")
    if mob_policy.get("additionalReviveMobsRequired") != []:
        errors.append("unexpected additional revive mobs appeared")
    if mob_policy.get("bossQuestDropOwner") != 9400409:
        errors.append("boss quest-drop ownership must remain on final revived form 9400409")

    unresolved = sorted(contract.get("unresolvedQuestDropItems", []))
    if unresolved != sorted(drops.get("unresolvedItems", [])):
        errors.append("implementation contract unresolved quest-drop set disagrees with quest-drop contract")
    if unresolved != [4000339, 4000341, 4000343]:
        errors.append("unresolved Ninja Castle quest-drop set drifted")

    item_set = set(closure.get("itemIds", []))
    mob_set = set(closure.get("mobIds", []))
    for row in drops.get("rows", []):
        if row.get("itemId") not in item_set:
            errors.append(f"quest-drop item outside regional closure: {row.get('itemId')}")
        if row.get("dropperId") not in mob_set:
            errors.append(f"quest-drop mob outside regional closure: {row.get('dropperId')}")

    portal_policy = contract.get("portalPolicy", {}).get("ninja_Boss", {})
    if portal_policy.get("fromMap") != 800040401 or portal_policy.get("toMap") != 800040410:
        errors.append("ninja_Boss portal map contract drifted")
    if portal_policy.get("targetPortal") != "out00":
        errors.append("ninja_Boss target portal drifted")
    if "pi.playPortalSound();" not in portal:
        errors.append("ninja_Boss must play the standard portal sound")
    if 'pi.warp(800040410, "out00");' not in portal:
        errors.append("ninja_Boss must warp to 800040410/out00")
    if "return true;" not in portal:
        errors.append("ninja_Boss must return true after successful warp")

    for key in FALSE_FLAGS:
        if contract.get(key) is not False:
            errors.append(f"{key} must remain false")
    for key in ("approved", "applyAllowed", "automaticApply"):
        if drops.get(key) is not False:
            errors.append(f"quest-drop contract {key} must remain false")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, default=Path("tools/wz-donor/clusters/gms-v95-ninja-castle-implementation-review.json"))
    parser.add_argument("--quest-drops", type=Path, default=Path("tools/wz-donor/clusters/gms-v95-ninja-castle-quest-drops.json"))
    parser.add_argument("--portal", type=Path, default=Path("scripts/portal/ninja_Boss.js"))
    args = parser.parse_args()

    errors = verify(args.contract, args.quest_drops, args.portal)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("Ninja Castle extraction-only implementation review contract: PASS")
    print("approved=false / importAllowed=false / automaticImport=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

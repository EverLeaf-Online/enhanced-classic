#!/usr/bin/env python3
"""Validate the pinned Cosmic WZ release metadata without downloading assets."""

import json
import re
from pathlib import Path


root = Path(__file__).resolve().parents[2]
cosmic = json.loads((root / "client/cosmic-wz-baseline.json").read_text(encoding="utf-8"))
managed = json.loads((root / "client/managed-client-baseline.json").read_text(encoding="utf-8"))

expected = {
    "Character.wz", "Etc.wz", "Item.wz", "List.wz", "Map.wz", "Mob.wz",
    "Npc.wz", "Quest.wz", "Reactor.wz", "Skill.wz", "String.wz", "UI.wz",
}
sha256 = re.compile(r"^[0-9a-f]{64}$")

assert cosmic["schemaVersion"] == 1
assert cosmic["releaseTag"] == "cosmic-wz-v0.14.0"
assert cosmic["archiveName"] == "CosmicWZ_2024-07-17_v0.14.0.zip"
assert sha256.fullmatch(cosmic["archiveSha256"])
assert cosmic["partCount"] == 21

files = cosmic["files"]
assert isinstance(files, list) and len(files) == len(expected)
by_path = {entry["path"]: entry for entry in files}
assert set(by_path) == expected
assert len(by_path) == len(files)
for path, entry in by_path.items():
    assert isinstance(entry["size"], int) and entry["size"] > 0, path
    assert sha256.fullmatch(entry["sha256"]), path

managed_paths = {entry["path"] for entry in managed["managedFiles"]}
assert expected <= managed_paths

# These upstream Git LFS identities are the critical server/client compatibility gate.
assert by_path["Map.wz"]["sha256"] == "a39da5ac66cb3cb1803b1a8f70f19cdf67ca191016e16c853f521b3c8156aca4"
assert by_path["Npc.wz"]["sha256"] == "2992910ac5f65fa3d1ca4b2469fa4105f948f6ceb4a6c47ee6953be9d04dee17"

print("Cosmic WZ baseline metadata tests passed.")

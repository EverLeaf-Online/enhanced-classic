#!/usr/bin/env python3
"""Build a review-only server XML dependency bundle for safe v180 map tiers.

This consumes MAP_BACKPORT_TIERS.json and the normalized MAP_TIER_MANIFESTS.json
produced by generate_map_tier_manifests.py. It copies only donor-overlay XML that
is required by selected effective tiers and is not already present in the v83 target tree. Existing target XML is never overwritten.

The output is a staging artifact only. It does not copy scripts and it refuses
to bundle any map whose normalized effective tier is C_SCRIPT_OR_LINK_WORK or
B_GENERIC_NPC_REVIEW when the requested tiers are A/B-present.
"""

from __future__ import annotations

import argparse
import json
import shutil
from collections import defaultdict
from pathlib import Path

ALLOWED_DEFAULT = ("A_STATIC", "B_DEPENDENCIES_PRESENT")


def read_lines(path: Path) -> set[str]:
    return {line.strip().replace("\\", "/") for line in path.read_text(encoding="utf-8").splitlines() if line.strip()}


def numeric_map_id_from_path(path: str) -> int:
    name = path.rsplit("/", 1)[-1]
    if not name.endswith(".img"):
        raise ValueError(f"not a map image path: {path}")
    return int(name[:-4])


def index_xml_by_stem(root: Path) -> dict[int, Path]:
    result: dict[int, Path] = {}
    if not root.exists():
        return result
    for p in root.rglob("*.img.xml"):
        stem = p.name[:-8]
        if not stem.isdigit():
            continue
        key = int(stem)
        old = result.setdefault(key, p)
        if old != p:
            raise ValueError(f"duplicate numeric XML id {key} under {root}: {old} vs {p}")
    return result


def copy_relative(src: Path, root: Path, out_root: Path) -> str:
    rel = src.relative_to(root)
    dst = out_root / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return(rel.as_posix())


def effective_map_sets(manifest_dir: Path) -> dict[str, set[int]]:
    summary = json.loads((manifest_dir / "MAP_TIER_MANIFESTS.json").read_text(encoding="utf-8"))
    result: dict[str, set[int]] = {}
    for tier, spec in summary["tiers"].items():
        lines = read_lines(manifest_dir / spec["manifestFile"])
        result[tier] = {numeric_map_id_from_path(x) for x in lines}
        if len(result[tier]) != int(spec["count"]):
            raise ValueError(f"manifest count mismatch for {tier}")
    return result


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--audit", type=Path, required=True)
    ap.add_argument("--tier-manifest-dir", type=Path, required=True)
    ap.add_argument("--overlay-root", type=Path, required=True)
    ap.add_argument("--target-root", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    ap.add_argument("--tiers", nargs="+", default=list(ALLOWED_DEFAULT))
    args = ap.parse_args()

    tier_sets = effective_map_sets(args.tier_manifest_dir)
    requested_tiers = tuple(args.tiers)
    unsupported = [x for x in requested_tiers if x not in ALLOWED_DEFAULT]
    if unsupported:
        raise ValueError(f"only review-safe tiers are supported: {unsupported}")
    selected_ids: set[int] = set()
    for tier in requested_tiers:
        selected_ids |= tier_sets[tier]

    audit = json.loads(args.audit.read_text(encoding="utf-8"))
    rows_by_id = {int(r["mapId"]): r for r in audit["maps"]}
    if len(rows_by_id) != len(audit["maps"]):
        raise ValueError("duplicate map IDs in audit")
    missing_rows = sorted(selected_ids - rows_by_id.keys())
    if missing_rows:
        raise ValueError(f"selected maps missing audit rows: {missing_rows[:20]}")

    # Effective-tier manifests are authoritative; still enforce hard dependency
    # invariants here so this bundle cannot silently widen its safety boundary.
    hard_fields = (
        "missingMapScripts",
        "missingPortalScripts",
        "missingReactorScripts",
        "missingDestinationMaps",
    )
    for map_id in sorted(selected_ids):
        row = rows_by_id[map_id]
        if any(row.get(field) for field in hard_fields):
            raise ValueError(f"selected map {map_id} still has a hard missing runtime dependency")
        if row.get("missingNpcScripts"):
            raise ValueError(f"selected map {map_id} still has a missing NPC script")

    roots = {
        "Map.wz": (args.overlay_root / "Map.wz", args.target_root / "Map.wz"),
        "Mob.wz": (args.overlay_root / "Mob.wz", args.target_root / "Mob.wz"),
        "Npc.wz": (args.overlay_root / "Npc.wz", args.target_root / "Npc.wz"),
        "Reactor.wz": (args.overlay_root / "Reactor.wz", args.target_root / "Reactor.wz"),
    }
    indexes = {
        family: (index_xml_by_stem(overlay), index_xml_by_stem(target))
        for family, (overlay, target) in roots.items()
    }

    dependency_ids: dict[str, set[int]] = {
        "Mob.wz": set(),
        "Npc.wz": set(),
        "Reactor.wz": set(),
    }
    for map_id in selected_ids:
        row = rows_by_id[map_id]
        dependency_ids["Mob.wz"].update(int(x) for x in row.get("mobIds", []))
        dependency_ids["Npc.wz"].update(int(x) for x in row.get("npcIds", []))
        dependency_ids["Reactor.wz"].update(int(x) for x in row.get("reactorIds", []))

    if args.out_dir.exists():
        shutil.rmtree(args.out_dir)
    args.out_dir.mkdir(parents=True)

    copied: dict[str, list[str]] = defaultdict(list)
    satisfied_by_target: dict[str, list[int]] = defaultdict(list)
    unresolved: dict[str, list[int]] = defaultdict(list)

    # Every selected map is donor-only by construction and must exist in overlay.
    map_overlay, map_target = indexes["Map.wz"]
    for map_id in sorted(selected_ids):
        if map_id in map_target:
            # This should be rare and is safe: never overwrite a target map.
            satisfied_by_target["Map.wz"].append(map_id)
            continue
        src = map_overlay.get(map_id)
        if src is None:
            unresolved["Map.wz"].append(map_id)
            continue
        copied["Map.wz"].append(
            copy_relative(src, roots["Map.wz"][0], args.out_dir / "Map.wz")
        )

    for family in ("Mob.wz", "Npc.wz", "Reactor.wz"):
        overlay_index, target_index = indexes[family]
        overlay_root, _ = roots[family]
        for object_id in sorted(dependency_ids[family]):
            if object_id in target_index:
                satisfied_by_target[family].append(object_id)
                continue
            src = overlay_index.get(object_id)
            if src is None:
                unresolved[family].append(object_id)
                continue
            copied[family].append(copy_relative(src, overlay_root, args.out_dir / family))

    unresolved_nonempty = {k: v for k, v in unresolved.items() if v}
    if unresolved_nonempty:
        raise ValueError(
            "unresolved selected map dependencies: "
            + json.dumps({k: v[:30] for k, v in unresolved_nonempty.items()}, sort_keys=True)
        )

    tier_counts = {tier: len(tier_sets[tier] & selected_ids) for tier in requested_tiers}
    manifest = {
        "schemaVersion": 1,
        "kind": "everleaf-v180-safe-map-server-xml-bundle",
        "approved": False,
        "productionApplyAllowed": False,
        "selectedEffectiveTiers": list(requested_tiers),
        "selectedMapCount": len(selected_ids),
        "selectedTierCounts": tier_counts,
        "dependencyReferenceCounts": {k: len(v) for k, v in dependency_ids.items()},
        "copiedDonorOnlyXmlCounts": {k: len(v) for k, v in copied.items()},
        "satisfiedByExistingTargetCounts": {k: len(v) for k, v in satisfied_by_target.items()},
        "unresolvedCounts": {k: len(v) for k, v in unresolved.items()},
        "unresolvedDependencies": {k: v for k, v in unresolved.items()},
        "policy": (
            "Review-only bundle for normalized A_STATIC and B_DEPENDENCIES_PRESENT maps. "
            "Copies donor overlay XML only when absent from the v83 target; never overwrites "
            "target XML and rejects hard missing runtime dependencies. No production apply."
        ),
        "files": {k: sorted(v) for k, v in copied.items()},
    }
    (args.out_dir / "MANIFEST.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (args.out_dir / "README.txt").write_text(
        "EverLeaf GMS v180 safe-map server XML bundle. STAGING/REVIEW ONLY. "
        "No production apply. Existing v83 XML is never overwritten.\n",
        encoding="utf-8",
    )
    print(json.dumps({k: v for k, v in manifest.items() if k != "files"}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

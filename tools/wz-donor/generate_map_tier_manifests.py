#!/usr/bin/env python3
"""Generate exact v180 numeric map manifests from the runtime dependency tier audit.

The audit classifies each staged numeric map by runtime dependency risk. This tool
maps those IDs back to their exact Map.w: image paths and writes deterministic
per-tier manifests for candidate builds. It intentionally excludes shared Back/Obj/
Tile/etc. assets; those are already staged separately by the broad asset manifests.

The generator also normalizes stale tier labels from the audit when the row itself
contains evidence of an unresolved runtime dependency. This prevents an unsafe map
from entering the A/B candidate solely because an older classification label was not refreshed after dependency analysis.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

MAP_PATH_RE = re.compile(r"^Map/Map\d+/(\d{9})\.img$")
EXPECTED_TIERS = (
    "A_STATIC",
    "B_DEPENDENCIES_PRESENT",
    "B_GENERIC_NPC_REVIEW",
    "C_SCRIPT_OR_LINK_WORK",
)


def effective_tier(row: dict[str, object]) -> tuple[str, str | None]:
    """Return the safe effective tier and an optional reclassification reason."""
    source = str(row["tier"])

    hard_missing = (
        "missingMapScripts",
        "missingPortalScripts",
        "missingReactorScripts",
        "missingDestinationMaps",
    )
    if any(row.get(name) for name in hard_missing):
        if source != "C_SCRIPT_OR_LINK_WORK":
            return "C_SCRIPT_OR_LINK_WORK", "hard runtime dependency missing"
        return source, None

    missing_npcs = bool(row.get("missingNpcScripts"))
    if missing_npcs and source != "B_GENERIC_NPC_REVIEW":
        if source != "C_SCRIPT_OR_LINK_WORK":
            return "C_SCRIPT_OR_LINK_WORK", "missing NPC script outside generic-NPC review tier"
        return source, None

    if source == "A_STATIC" and any(
        row.get(name) for name in ("mapScripts", "portalScripts", "npcIds", "reactorIds")
    ):
        return "B_DEPENDENCIES_PRESENT", "runtime dependency references are present"

    return source, None


def load_map_paths(path: Path) -> dict[int, str]:
    by_id: dict[int, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip().replace("\\", "/")
        match = MAP_PATH_RE.match(line)
        if not match:
            continue
        map_id = int(match.group(1))
        previous = by_id.setdefault(map_id, line)
        if previous != line:
            raise ValueError(
                f"ambiguous Map.w: path for {map_id}: {previous!r} vs {line!r}"
            )
    return by_id


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tiers", type=Path, required=True, help="MAP_BACKPORT_TIERS.json")
    ap.add_argument("--maps", type=Path, required=True, help="maps_all.txt")
    ap.add_argument("--out-dir", type=Path, required=True)
    args = ap.parse_args()

    audit = json.loads(args.tiers.read_text(encoding="utf-8"))
    rows = audit.get("maps")
    if not isinstance(rows, list):
        raise ValueError("tier audit has no maps[] array")

    path_by_id = load_map_paths(args.maps)
    grouped: dict[str, list[str]] = {tier: [] for tier in EXPECTED_TIERS}
    seen_ids: set[int] = set()
    missing_paths: list[int] = []
    reclassified: list[dict[str, object]] = []

    for row in rows:
        map_id = int(row["mapId"])
        source_tier = str(row["tier"])
        if source_tier not in grouped:
            raise ValueError(f"unknown tier {source_tier!r} for map {map_id}")
        if map_id in seen_ids:
            raise ValueError(f"duplicate map id in tier audit: {map_id}")
        seen_ids.add(map_id)

        tier, reason = effective_tier(row)
        if reason is not None:
            reclassified.append(
                {
                    "mapId": map_id,
                    "sourceTier": source_tier,
                    "effectiveTier": tier,
                    "reason": reason,
                }
            )

        image_path = path_by_id.get(map_id)
        if image_path is None:
            missing_paths.append(map_id)
            continue
        grouped[tier].append(image_path)

    if missing_paths:
        sample = ", ".join(map(str, missing_paths[:20]))
        raise ValueError(
            f"{len(missing_paths)} tiered map IDs missing from maps manifest; sample={sample}"
        )

    args.out_dir.mkdir(parents=True, exist_ok=True)
    outputs: dict[str, dict[str, object]] = {}
    for tier in EXPECTED_TIERS:
        paths = sorted(set(grouped[tier]), key=str.casefold)
        file_name = "maps_" + tier.lower() + ".txt"
        output_path = args.out_dir / file_name
        output_path.write_text("".join(f"{x}\n" for x in paths), encoding="ascii")
        outputs[tier] = {"count": len(paths), "manifestFile": file_name}

    source_counts = {str(k): int(v) for k, v in audit.get("tierCounts", {}).items()}
    effective_counts = {tier: len(grouped[tier]) for tier in EXPECTED_TIERS}
    if sum(effective_counts.values()) != len(rows):
        raise ValueError("effective tier manifests do not cover every audited map exactly once")

    summary = {
        "schemaVersion": 2,
        "kind": "everleaf-v180-map-tier-manifests",
        "approved": False,
        "productionApplyAllowed": False,
        "sourceTierAudit": str(args.tiers),
        "sourceMapManifest": str(args.maps),
        "numericMapPathCount": len(path_by_id),
        "tieredMapCount": len(rows),
        "sourceTierCounts": source_counts,
        "effectiveTierCounts": effective_counts,
        "reclassifiedCount": len(reclassified),
        "reclassifications": reclassified,
        "tiers": outputs,
        "policy": (
            "Exact numeric Map.wz donor-only paths grouped by dependency evidence. "
            "Rows with unresolved hard runtime dependencies are forced into "
            "C_SCRIPT_OR_LINK_WORK. No production apply."
        ),
    }
    (args.out_dir / "MAP_TIER_MANIFESTS.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

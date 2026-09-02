#!/usr/bin/env python3
"""Build a review-first EverLeaf import manifest from a WZ donor diff report."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

CATEGORY_RISK = {
    "equipment": "low",
    "items": "low",
    "npcs": "medium",
    "mobs": "medium",
    "reactors": "medium",
    "maps": "medium",
    "quests": "high",
    "skills": "high",
}

CATEGORY_REVIEW = {
    "equipment": ["Character.wz client node", "String.wz name/description", "equip slot/job requirements"],
    "items": ["Item.wz client node", "String.wz name/description", "server item behavior"],
    "npcs": ["Npc.wz client node", "String.wz name", "NPC script if interactive"],
    "mobs": ["Mob.wz client node", "String.wz name", "skills/drops/server mob behavior"],
    "reactors": ["Reactor.wz client node", "reactor script/drop behavior", "map references"],
    "maps": ["Map.wz client assets", "portals/life/reactors", "tiles/objects/backgrounds/sound", "map scripts"],
    "quests": ["Quest.wz", "String.wz quest text", "NPC/item/map dependencies", "server quest compatibility"],
    "skills": ["Skill.wz", "Character/Effect/Sound assets", "server skill implementation", "packet/client compatibility"],
}


def build_manifest(report: dict) -> dict:
    missing_by_source = report.get("dependencies", {}).get("missingBySource", {})
    candidates = []

    for category, category_report in report["categories"].items():
        risk = CATEGORY_RISK.get(category, "high")
        review = CATEGORY_REVIEW.get(category, ["manual compatibility review"])
        for entry in category_report.get("newEntries", []):
            content_id = entry["content_id"]
            source_key = f"{category}:{content_id}"
            missing = missing_by_source.get(source_key, [])
            effective_risk = "blocked" if missing else risk
            candidates.append(
                {
                    "category": category,
                    "contentId": content_id,
                    "sourcePath": entry["relative_path"],
                    "sourceSha256": entry["sha256"],
                    "risk": effective_risk,
                    "approved": False,
                    "reviewRequired": review,
                    "missingDependencies": missing,
                    "notes": "",
                }
            )

    risk_order = {"low": 0, "medium": 1, "high": 2, "blocked": 3}
    candidates.sort(key=lambda c: (risk_order.get(c["risk"], 9), c["category"], int(c["contentId"])))

    counts = {"low": 0, "medium": 0, "high": 0, "blocked": 0}
    for candidate in candidates:
        counts[candidate["risk"]] = counts.get(candidate["risk"], 0) + 1

    return {
        "schemaVersion": 1,
        "donorId": report.get("donorId", "unknown-donor"),
        "baseline": report.get("baseline"),
        "donor": report.get("donor"),
        "mode": "review-first",
        "automaticImport": False,
        "candidateCount": len(candidates),
        "riskCounts": counts,
        "candidates": candidates,
        "approvalRule": "Only entries with approved=true may be considered by a future staging importer; this file alone never mutates WZ data.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a disabled-by-default import manifest from a WZ donor diff.")
    parser.add_argument("diff", type=Path, help="JSON report produced by wz_diff.py")
    parser.add_argument("--output", type=Path, default=Path("tools/output/wz-import-manifest.json"))
    args = parser.parse_args()

    report = json.loads(args.diff.read_text(encoding="utf-8"))
    manifest = build_manifest(report)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print(f"Donor: {manifest['donorId']}")
    print(f"Candidates: {manifest['candidateCount']}")
    print("Risk counts: " + ", ".join(f"{k}={v}" for k, v in manifest["riskCounts"].items()))
    print(f"Manifest: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

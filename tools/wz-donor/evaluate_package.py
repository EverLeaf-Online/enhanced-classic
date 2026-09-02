#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def classify(category_report: dict, content_id: str) -> str:
    cid = str(int(content_id))
    new_ids = {str(int(x)) for x in category_report.get("newIds", [])}
    collisions = {str(int(x)) for x in category_report.get("collisionIds", [])}
    changed = {str(int(x)) for x in category_report.get("changedCollisionIds", [])}
    donor_entries = category_report.get("donorCount", 0)
    if cid in new_ids:
        return "donor-new"
    if cid in changed:
        return "collision-changed"
    if cid in collisions:
        return "collision-identical"
    return "missing-from-donor"


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate one frozen EverLeaf content package against a WZ donor diff.")
    parser.add_argument("package", type=Path)
    parser.add_argument("diff", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    package = load(args.package)
    diff = load(args.diff)
    if package.get("mode") != "review-only" or package.get("approved") is not False:
        raise SystemExit("package must remain review-only and approved=false")
    if package.get("automaticImport") is not False:
        raise SystemExit("automaticImport must remain false")

    categories = diff.get("categories", {})
    rows: list[dict] = []
    counts = {"donor-new": 0, "collision-changed": 0, "collision-identical": 0, "missing-from-donor": 0}

    for category, ids in (package.get("content") or {}).items():
        if category not in categories:
            for content_id in ids:
                rows.append({"category": category, "contentId": str(content_id), "state": "category-not-in-diff"})
            continue
        report = categories[category]
        for content_id in ids:
            state = classify(report, str(content_id))
            counts[state] += 1
            rows.append({"category": category, "contentId": str(content_id), "state": state})

    selected = {(row["category"], str(int(row["contentId"]))) for row in rows if row["state"] != "category-not-in-diff"}
    missing_refs = []
    for ref in (diff.get("dependencies") or {}).get("missingReferences", []):
        source = (ref.get("source_category"), str(int(ref.get("source_id"))))
        if source in selected:
            missing_refs.append(ref)

    result = {
        "schemaVersion": 1,
        "packageId": package.get("packageId"),
        "donorId": diff.get("donorId"),
        "mode": "review-only-evaluation",
        "applyAllowed": False,
        "approved": False,
        "counts": counts,
        "selectedCount": len(rows),
        "missingSelectedDependencies": missing_refs,
        "missingSelectedDependencyCount": len(missing_refs),
        "entries": rows,
        "readyForImportReview": counts["missing-from-donor"] == 0 and len(missing_refs) == 0,
        "warning": "readyForImportReview is not production approval. Client assets, scripts, parser compatibility and real-client staging remain mandatory."
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    print(f"Package: {result['packageId']}")
    print(f"Selected IDs: {result['selectedCount']}")
    for key, value in counts.items():
        print(f"{key}: {value}")
    print(f"Missing selected dependencies: {len(missing_refs)}")
    print(f"Ready for import review: {result['readyForImportReview']}")
    print(f"Report: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize unresolved references for a frozen EverLeaf donor package evaluation.")
    parser.add_argument("evaluation", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    evaluation = load(args.evaluation)
    refs = evaluation.get("missingSelectedDependencies") or []

    by_target = Counter(ref.get("target_category", "unknown") for ref in refs)
    by_property = Counter(ref.get("property_name", "unknown") for ref in refs)
    by_source_category = Counter(ref.get("source_category", "unknown") for ref in refs)
    by_source = Counter(f"{ref.get('source_category')}:{ref.get('source_id')}" for ref in refs)

    unique_targets = sorted(
        {
            (str(ref.get("target_category")), str(ref.get("target_id")))
            for ref in refs
        },
        key=lambda row: (row[0], int(row[1]) if row[1].isdigit() else row[1]),
    )

    target_ids: dict[str, list[str]] = defaultdict(list)
    for category, content_id in unique_targets:
        target_ids[category].append(content_id)

    result = {
        "schemaVersion": 1,
        "packageId": evaluation.get("packageId"),
        "mode": "read-only-dependency-summary",
        "applyAllowed": False,
        "missingReferenceCount": len(refs),
        "uniqueMissingTargetCount": len(unique_targets),
        "countsByTargetCategory": dict(sorted(by_target.items())),
        "countsBySourceCategory": dict(sorted(by_source_category.items())),
        "countsByProperty": dict(sorted(by_property.items())),
        "topSources": [
            {"source": source, "missingReferenceCount": count}
            for source, count in by_source.most_common(25)
        ],
        "missingTargetIds": dict(sorted(target_ids.items())),
        "missingReferences": refs,
        "warning": "These are conservative high-confidence WZ references. Each unresolved target must be classified before package approval; this report does not authorize importing dependencies automatically.",
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    print(f"Package: {result['packageId']}")
    print(f"Missing references: {result['missingReferenceCount']}")
    print(f"Unique missing targets: {result['uniqueMissingTargetCount']}")
    print("By target category:")
    for category, count in result["countsByTargetCategory"].items():
        print(f"  {category}: {count}")
    print("By property:")
    for prop, count in result["countsByProperty"].items():
        print(f"  {prop}: {count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

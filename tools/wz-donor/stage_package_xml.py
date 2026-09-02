#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def source_path(category: str, content_id: str) -> Path:
    cid = str(int(content_id))
    if category == "maps":
        first = cid[0]
        # GMS exported map files are grouped as Map0..Map9 by leading digit.
        return Path("Map.wz") / "Map" / f"Map{first}" / f"{cid}.img.xml"
    if category == "mobs":
        return Path("Mob.wz") / f"{cid}.img.xml"
    if category == "npcs":
        return Path("Npc.wz") / f"{cid}.img.xml"
    if category == "reactors":
        return Path("Reactor.wz") / f"{cid}.img.xml"
    raise ValueError(f"unsupported package category for direct XML staging: {category}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Merge a review-only donor package into a disposable EverLeaf WZ XML staging tree.")
    parser.add_argument("package", type=Path)
    parser.add_argument("--canonical", type=Path, required=True)
    parser.add_argument("--donor", type=Path, required=True)
    parser.add_argument("--staging", type=Path, required=True)
    args = parser.parse_args()

    package = load(args.package)
    if package.get("mode") != "review-only" or package.get("approved") is not False:
        raise SystemExit("package must remain review-only and approved=false")
    if package.get("automaticImport") is not False:
        raise SystemExit("automaticImport must remain false")

    canonical = args.canonical.resolve()
    donor = args.donor.resolve()
    staging = args.staging.resolve()
    if canonical == staging:
        raise SystemExit("staging path must differ from canonical")
    if not canonical.is_dir() or not donor.is_dir():
        raise SystemExit("canonical and donor roots must exist")

    if staging.exists():
        shutil.rmtree(staging)
    shutil.copytree(canonical, staging)

    files: list[dict] = []
    missing: list[str] = []
    for category, ids in (package.get("content") or {}).items():
        for content_id in ids:
            try:
                rel = source_path(category, str(content_id))
            except ValueError:
                continue
            src = donor / rel
            dst = staging / rel
            if not src.is_file():
                missing.append(rel.as_posix())
                continue
            state = "replace" if dst.exists() else "add"
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            files.append({
                "category": category,
                "contentId": str(content_id),
                "source": rel.as_posix(),
                "destination": rel.as_posix(),
                "operation": state,
            })

    report = {
        "schemaVersion": 1,
        "packageId": package.get("packageId"),
        "mode": "isolated-staging-merge",
        "canonicalMutated": False,
        "productionApplyAllowed": False,
        "approved": False,
        "selectedFiles": len(files),
        "missingSourceFiles": missing,
        "files": files,
    }
    (staging / "STAGING_PACKAGE_REPORT.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print(f"Package: {report['packageId']}")
    print(f"Staged files: {len(files)}")
    print(f"Missing source files: {len(missing)}")
    print("canonicalMutated=false / productionApplyAllowed=false / approved=false")
    for path in missing:
        print(f"MISSING {path}")
    return 0 if not missing else 3


if __name__ == "__main__":
    raise SystemExit(main())

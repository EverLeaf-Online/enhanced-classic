#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import xml.etree.ElementTree as ET
from pathlib import Path


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def find_named_node(path: Path, expected_name: str) -> bool:
    if not path.is_file():
        return False
    try:
        root = ET.parse(path).getroot()
    except (OSError, ET.ParseError):
        return False
    needle = expected_name.lower()
    return any(node.attrib.get("name", "").lower() == needle for node in root.iter())


def first_existing(root: Path, candidates: list[Path]) -> Path | None:
    for candidate in candidates:
        path = root / candidate
        if path.is_file():
            return path
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify non-ID client assets required by a frozen EverLeaf WZ package.")
    parser.add_argument("package", type=Path)
    parser.add_argument("--donor", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    package = load_json(args.package)
    donor = args.donor
    if package.get("mode") != "review-only" or package.get("approved") is not False:
        raise SystemExit("package must remain review-only and approved=false")

    checks: list[dict] = []

    map_root = donor / "Map.wz"
    for kind, folder in (("tiles", "Tile"), ("objects", "Obj"), ("backgrounds", "Back")):
        for name in (package.get("clientAssets") or {}).get(kind, []):
            candidates = [
                Path("Map.wz") / folder / f"{name}.img.xml",
                Path("Map.wz") / folder / f"{name}.xml",
            ]
            found = first_existing(donor, candidates)
            checks.append({
                "kind": kind[:-1] if kind.endswith("s") else kind,
                "name": name,
                "present": found is not None,
                "path": found.relative_to(donor).as_posix() if found else None,
            })

    for bgm in (package.get("clientAssets") or {}).get("bgm", []):
        family, _, track = bgm.partition("/")
        candidates = [
            Path("Sound.wz") / f"{family}.img.xml",
            Path("Sound.wz") / f"{family}.xml",
        ]
        source = first_existing(donor, candidates)
        present = source is not None and find_named_node(source, track)
        checks.append({
            "kind": "bgm",
            "name": bgm,
            "present": present,
            "path": source.relative_to(donor).as_posix() if source else None,
        })

    missing = [check for check in checks if not check["present"]]
    result = {
        "schemaVersion": 1,
        "packageId": package.get("packageId"),
        "mode": "read-only-asset-verification",
        "applyAllowed": False,
        "checked": len(checks),
        "present": len(checks) - len(missing),
        "missing": len(missing),
        "checks": checks,
        "missingAssets": missing,
        "readyForAssetReview": len(missing) == 0,
        "warning": "This verifies named package assets only. It does not prove every linked image, effect, sound, script, or packet dependency is compatible with v83."
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    print(f"Package: {result['packageId']}")
    print(f"Assets checked: {result['checked']}")
    print(f"Present: {result['present']}")
    print(f"Missing: {result['missing']}")
    for check in missing:
        print(f"MISSING {check['kind']}: {check['name']}")
    return 0 if not missing else 3


if __name__ == "__main__":
    raise SystemExit(main())

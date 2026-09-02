#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def tree_digest(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        rel = path.relative_to(root).as_posix().encode("utf-8")
        digest.update(len(rel).to_bytes(4, "big"))
        digest.update(rel)
        digest.update(bytes.fromhex(file_sha256(path)))
    return digest.hexdigest()


def canonical_numeric(value: str) -> str:
    return str(int(value))


def direct_ids(root: ET.Element) -> list[str]:
    ids: list[str] = []
    for child in list(root):
        if child.tag != "imgdir":
            continue
        name = child.attrib.get("name", "")
        try:
            ids.append(canonical_numeric(name))
        except ValueError:
            continue
    return ids


def merge_fragment(target_path: Path, fragment_path: Path, expected_ids: list[str]) -> dict:
    target_tree = ET.parse(target_path)
    target_root = target_tree.getroot()
    fragment_root = ET.parse(fragment_path).getroot()

    target_ids = set(direct_ids(target_root))
    fragment_nodes = [child for child in list(fragment_root) if child.tag == "imgdir"]
    fragment_ids = [canonical_numeric(node.attrib["name"]) for node in fragment_nodes]

    if fragment_ids != expected_ids:
        raise ValueError(
            f"{fragment_path}: fragment IDs drifted; expected {expected_ids}, got {fragment_ids}"
        )
    collisions = sorted(target_ids.intersection(fragment_ids), key=int)
    if collisions:
        raise ValueError(f"{target_path}: refusing existing target IDs {collisions}")

    before_count = len(list(target_root))
    for node in fragment_nodes:
        target_root.append(node)
    ET.indent(target_tree, space="  ")
    target_tree.write(target_path, encoding="utf-8", xml_declaration=True)

    verify_root = ET.parse(target_path).getroot()
    verify_ids = direct_ids(verify_root)
    for cid in expected_ids:
        if verify_ids.count(cid) != 1:
            raise ValueError(f"{target_path}: expected exactly one staged node for {cid}")

    return {
        "path": target_path.as_posix(),
        "insertedIds": fragment_ids,
        "beforeChildCount": before_count,
        "afterChildCount": len(list(verify_root)),
        "sha256": file_sha256(target_path),
    }


def stage(canonical_wz: Path, patch_root: Path, staging_wz: Path) -> dict:
    patch_manifest_path = patch_root / "PATCH_MANIFEST.json"
    patch_manifest = json.loads(patch_manifest_path.read_text(encoding="utf-8"))
    if patch_manifest.get("mode") != "isolated-patch-artifact":
        raise ValueError("patch manifest mode must be isolated-patch-artifact")
    if patch_manifest.get("applyAllowed") is not False or patch_manifest.get("approved") is not False:
        raise ValueError("patch artifact must remain non-applying and unapproved")
    expected_ids = [str(value) for value in patch_manifest.get("candidateIds", [])]
    if expected_ids != ["2022711", "2022712"]:
        raise ValueError(f"unexpected candidate IDs: {expected_ids}")

    canonical_before = tree_digest(canonical_wz)
    if staging_wz.exists():
        shutil.rmtree(staging_wz)
    shutil.copytree(canonical_wz, staging_wz)

    merge_results: list[dict] = []
    for rel in ("Item.wz/Consume/0202.img.xml", "String.wz/Consume.img.xml"):
        fragment = patch_root / rel
        target = staging_wz / rel
        if not fragment.is_file():
            raise ValueError(f"missing patch fragment: {rel}")
        if not target.is_file():
            raise ValueError(f"missing canonical target: {rel}")
        result = merge_fragment(target, fragment, expected_ids)
        result["path"] = rel
        merge_results.append(result)

    canonical_after = tree_digest(canonical_wz)
    if canonical_after != canonical_before:
        raise RuntimeError("canonical WZ tree changed during staging merge")

    report = {
        "schemaVersion": 1,
        "mode": "temporary-staging-copy",
        "canonicalMutated": False,
        "productionApplyAllowed": False,
        "approved": False,
        "candidateIds": expected_ids,
        "canonicalTreeSha256Before": canonical_before,
        "canonicalTreeSha256After": canonical_after,
        "stagingTreeSha256": tree_digest(staging_wz),
        "mergedFiles": merge_results,
    }
    (staging_wz / "STAGING_MERGE_REPORT.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Merge a frozen WZ patch artifact into a disposable staging copy only.")
    parser.add_argument("--canonical", type=Path, required=True, help="Canonical v83 WZ XML root")
    parser.add_argument("--patch", type=Path, required=True, help="Non-applying patch artifact root")
    parser.add_argument("--staging", type=Path, required=True, help="Disposable staging WZ output root")
    args = parser.parse_args()

    report = stage(args.canonical.resolve(), args.patch.resolve(), args.staging.resolve())
    print("Staging merge complete")
    print("Candidates: " + ", ".join(report["candidateIds"]))
    print("canonicalMutated=false / productionApplyAllowed=false / approved=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

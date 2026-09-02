#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

NUMERIC_ID = re.compile(r"^\d{1,10}$")


def canonical_id(value: str | None) -> str | None:
    if not value or not NUMERIC_ID.fullmatch(value):
        return None
    return str(int(value))


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def find_numeric_node(path: Path, content_id: str) -> tuple[ET.Element, ET.Element]:
    tree = ET.parse(path)
    root = tree.getroot()
    target = canonical_id(content_id)
    for node in root.iter("imgdir"):
        if canonical_id(node.attrib.get("name")) == target:
            return root, node
    raise ValueError(f"{content_id}: numeric node not found in {path}")


def direct_string_entry(path: Path, content_id: str) -> tuple[ET.Element, ET.Element]:
    tree = ET.parse(path)
    root = tree.getroot()
    target = canonical_id(content_id)
    for node in root.iter("imgdir"):
        if canonical_id(node.attrib.get("name")) != target:
            continue
        direct_strings = {
            child.attrib.get("name", "").lower(): child.attrib.get("value", "")
            for child in list(node)
            if child.tag == "string"
        }
        if direct_strings.get("name"):
            return root, node
    raise ValueError(f"{content_id}: direct String.wz entry not found in {path}")


def write_fragment(root_name: str, nodes: list[ET.Element], output: Path) -> None:
    root = ET.Element("imgdir", {"name": root_name})
    for node in nodes:
        root.append(copy.deepcopy(node))
    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ")
    output.parent.mkdir(parents=True, exist_ok=True)
    tree.write(output, encoding="utf-8", xml_declaration=True)


def build(batch: dict, donor_root: Path, string_root: Path, output_root: Path) -> dict:
    if batch.get("mode") != "review-only" or batch.get("approved") is not False:
        raise ValueError("batch must remain review-only and approved=false")
    if batch.get("automaticImport") is not False:
        raise ValueError("automaticImport must remain false")

    candidates = batch.get("candidates") or []
    if not candidates:
        raise ValueError("batch has no candidates")

    item_groups: dict[str, list[tuple[dict, ET.Element, str]]] = {}
    string_groups: dict[str, list[tuple[dict, ET.Element, str]]] = {}

    for candidate in candidates:
        cid = str(candidate["contentId"])
        if candidate.get("approved") is not False:
            raise ValueError(f"{cid}: candidate approved must remain false")
        source_path = candidate["sourcePath"]
        source = donor_root / source_path
        if not source.exists():
            raise ValueError(f"{cid}: donor source missing: {source_path}")
        _, item_node = find_numeric_node(source, cid)

        # The String export keeps Consume.img as one XML document.
        string_source = string_root / "String.wz" / "Consume.img.xml"
        if not string_source.exists():
            raise ValueError("String.wz/Consume.img.xml missing")
        _, string_node = direct_string_entry(string_source, cid)
        actual_name = next(
            (child.attrib.get("value", "") for child in list(string_node)
             if child.tag == "string" and child.attrib.get("name", "").lower() == "name"),
            "",
        )
        if actual_name != candidate.get("name"):
            raise ValueError(f"{cid}: String.wz name mismatch: {actual_name!r}")

        item_groups.setdefault(source_path, []).append((candidate, item_node, source.name))
        string_groups.setdefault("String.wz/Consume.img.xml", []).append((candidate, string_node, string_source.name))

    files: list[dict] = []
    for relative, records in item_groups.items():
        source = donor_root / relative
        source_root = ET.parse(source).getroot()
        out = output_root / relative
        write_fragment(source_root.attrib.get("name", source.stem), [record[1] for record in records], out)
        files.append({
            "path": relative,
            "kind": "item-fragment",
            "contentIds": [str(record[0]["contentId"]) for record in records],
            "sha256": sha256_file(out),
        })

    for relative, records in string_groups.items():
        source = string_root / relative
        source_root = ET.parse(source).getroot()
        out = output_root / relative
        write_fragment(source_root.attrib.get("name", source.stem), [record[1] for record in records], out)
        files.append({
            "path": relative,
            "kind": "string-fragment",
            "contentIds": [str(record[0]["contentId"]) for record in records],
            "sha256": sha256_file(out),
        })

    manifest = {
        "schemaVersion": 1,
        "batchId": batch["batchId"],
        "mode": "isolated-patch-artifact",
        "applyAllowed": False,
        "approved": False,
        "sourceBatchApproved": False,
        "candidateIds": [str(candidate["contentId"]) for candidate in candidates],
        "files": sorted(files, key=lambda item: item["path"]),
        "note": "Patch fragments are for parity/staging review only. They are not a canonical WZ tree and must not be imported automatically.",
    }
    manifest_path = output_root / "PATCH_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Build an isolated, non-applying WZ patch artifact from a frozen review batch.")
    parser.add_argument("batch", type=Path)
    parser.add_argument("--donor", type=Path, required=True)
    parser.add_argument("--strings", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    batch = load_json(args.batch)
    args.output.mkdir(parents=True, exist_ok=True)
    manifest = build(batch, args.donor, args.strings, args.output)
    print(f"Patch artifact built for {manifest['batchId']}")
    print("Candidates: " + ", ".join(manifest["candidateIds"]))
    print("applyAllowed=false / approved=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

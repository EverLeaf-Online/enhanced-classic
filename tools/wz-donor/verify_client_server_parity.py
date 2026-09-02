#!/usr/bin/env python3
"""Fail-closed verification for a raw-client WZ candidate against a pinned parity contract."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def verify(contract: dict[str, Any], manifest: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []

    if contract.get("kind") != "client-server-parity-contract":
        fail(errors, "contract kind is not client-server-parity-contract")
    if manifest.get("kind") != "isolated-client-wz-candidate":
        fail(errors, "manifest kind is not isolated-client-wz-candidate")
    if manifest.get("schemaVersion", 0) < 2:
        fail(errors, "client manifest schemaVersion must be >= 2 with reparsed semantics")

    batch_id = contract.get("batchId")
    if manifest.get("batchId") != batch_id:
        fail(errors, f"batchId mismatch: expected {batch_id!r}, got {manifest.get('batchId')!r}")

    if contract.get("approved") is not False or contract.get("productionApplyAllowed") is not False:
        fail(errors, "parity contract itself must remain unapproved and non-applying")
    if manifest.get("approved") is not False:
        fail(errors, "client manifest approved must remain false")
    if manifest.get("productionApplyAllowed") is not False:
        fail(errors, "client manifest productionApplyAllowed must remain false")

    expected_ids = contract.get("candidateIds")
    actual_ids = manifest.get("candidateIds")
    if actual_ids != expected_ids:
        fail(errors, f"candidateIds mismatch: expected {expected_ids!r}, got {actual_ids!r}")

    for section in ("sourceClient", "donor"):
        expected_section = contract.get(section, {})
        actual_section = manifest.get(section, {})
        for family in ("item", "string"):
            expected = expected_section.get(family, {})
            actual = actual_section.get(family, {})
            for field in ("version", "sha256"):
                if actual.get(field) != expected.get(field):
                    fail(
                        errors,
                        f"{section}.{family}.{field} mismatch: expected {expected.get(field)!r}, got {actual.get(field)!r}",
                    )

    source = manifest.get("sourceClient", {})
    output = manifest.get("output", {})
    for family in ("item", "string"):
        source_hash = source.get(family, {}).get("sha256")
        output_hash = output.get(family, {}).get("sha256")
        if not isinstance(output_hash, str) or len(output_hash) != 64:
            fail(errors, f"output.{family}.sha256 is missing or invalid")
        elif output_hash == source_hash:
            fail(errors, f"output.{family}.sha256 unexpectedly equals source hash")
        size = output.get(family, {}).get("size")
        if not isinstance(size, int) or size <= 0:
            fail(errors, f"output.{family}.size must be a positive integer")

    validation = manifest.get("validation", {})
    required_validation = (
        "sourceClientUnchanged",
        "outputReparsed",
        "exactCandidateIds",
        "donorNodesDeepCloned",
        "iconCanvasesPreserved",
        "semanticValuesReadAfterReparse",
    )
    for field in required_validation:
        if validation.get(field) is not True:
            fail(errors, f"validation.{field} must be true")

    expected_semantics = {
        candidate["contentId"]: candidate for candidate in contract.get("candidates", [])
    }
    actual_semantics_list = manifest.get("semantics", [])
    if not isinstance(actual_semantics_list, list):
        fail(errors, "manifest semantics must be a list")
        actual_semantics_list = []
    actual_semantics: dict[int, dict[str, Any]] = {}
    for entry in actual_semantics_list:
        if not isinstance(entry, dict) or not isinstance(entry.get("contentId"), int):
            fail(errors, f"invalid semantics entry: {entry!r}")
            continue
        content_id = entry["contentId"]
        if content_id in actual_semantics:
            fail(errors, f"duplicate semantics entry for {content_id}")
        actual_semantics[content_id] = entry

    if set(actual_semantics) != set(expected_semantics):
        fail(
            errors,
            f"semantic ID set mismatch: expected {sorted(expected_semantics)}, got {sorted(actual_semantics)}",
        )

    semantic_fields = ("name", "description", "hp", "mp", "price", "slotMax")
    for content_id, expected in expected_semantics.items():
        actual = actual_semantics.get(content_id)
        if actual is None:
            continue
        for field in semantic_fields:
            if actual.get(field) != expected.get(field):
                fail(
                    errors,
                    f"{content_id} {field} mismatch: expected {expected.get(field)!r}, got {actual.get(field)!r}",
                )
        if expected.get("requiresCanvasIcons"):
            for field in ("iconPropertyType", "iconRawPropertyType"):
                value = actual.get(field)
                if not isinstance(value, str) or "canvas" not in value.lower():
                    fail(errors, f"{content_id} {field} is not a canvas property: {value!r}")

    return {
        "schemaVersion": 1,
        "kind": "client-server-parity-verification",
        "batchId": batch_id,
        "passed": not errors,
        "approved": False,
        "productionApplyAllowed": False,
        "candidateIds": expected_ids,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("contract", type=Path)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    report = verify(load_json(args.contract), load_json(args.manifest))
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

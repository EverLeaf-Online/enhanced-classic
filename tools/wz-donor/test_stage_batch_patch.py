#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("stage_batch_patch.py")
SPEC = importlib.util.spec_from_file_location("stage_batch_patch", MODULE_PATH)
assert SPEC and SPEC.loader
stager = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = stager
SPEC.loader.exec_module(stager)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def make_fixture(root: Path) -> tuple[Path, Path]:
    canonical = root / "canonical"
    patch = root / "patch"
    write(
        canonical / "Item.wz/Consume/0202.img.xml",
        '<imgdir name="0202.img"><imgdir name="02020000"><imgdir name="spec"><int name="hp" value="1"/></imgdir></imgdir></imgdir>',
    )
    write(
        canonical / "String.wz/Consume.img.xml",
        '<imgdir name="Consume.img"><imgdir name="2020000"><string name="name" value="Existing"/></imgdir></imgdir>',
    )
    write(canonical / "Other.wz/keep.xml", '<imgdir name="keep"/>')
    write(
        patch / "Item.wz/Consume/0202.img.xml",
        '<imgdir name="0202.img"><imgdir name="02022711"/><imgdir name="02022712"/></imgdir>',
    )
    write(
        patch / "String.wz/Consume.img.xml",
        '<imgdir name="Consume.img"><imgdir name="2022711"/><imgdir name="2022712"/></imgdir>',
    )
    manifest = {
        "mode": "isolated-patch-artifact",
        "applyAllowed": False,
        "approved": False,
        "candidateIds": ["2022711", "2022712"],
    }
    write(patch / "PATCH_MANIFEST.json", json.dumps(manifest))
    return canonical, patch


class StageBatchPatchTest(unittest.TestCase):
    def test_stages_only_copy_and_preserves_canonical(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            canonical, patch = make_fixture(root)
            before = stager.tree_digest(canonical)
            staging = root / "staging"
            report = stager.stage(canonical, patch, staging)
            after = stager.tree_digest(canonical)

            self.assertEqual(before, after)
            self.assertFalse(report["canonicalMutated"])
            self.assertFalse(report["productionApplyAllowed"])
            self.assertFalse(report["approved"])
            self.assertEqual(["2022711", "2022712"], report["candidateIds"])
            self.assertEqual('<imgdir name="keep"/>', (staging / "Other.wz/keep.xml").read_text())

            item = ET.parse(staging / "Item.wz/Consume/0202.img.xml").getroot()
            ids = stager.direct_ids(item)
            self.assertEqual(["2020000", "2022711", "2022712"], ids)
            self.assertTrue((staging / "STAGING_MERGE_REPORT.json").exists())

    def test_existing_target_id_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            canonical, patch = make_fixture(root)
            write(
                canonical / "Item.wz/Consume/0202.img.xml",
                '<imgdir name="0202.img"><imgdir name="02022711"/></imgdir>',
            )
            with self.assertRaisesRegex(ValueError, "refusing existing target IDs"):
                stager.stage(canonical, patch, root / "staging")

    def test_broadened_or_approved_patch_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            canonical, patch = make_fixture(root)
            manifest_path = patch / "PATCH_MANIFEST.json"
            manifest = json.loads(manifest_path.read_text())
            manifest["candidateIds"].append("2022999")
            manifest_path.write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError, "unexpected candidate IDs"):
                stager.stage(canonical, patch, root / "staging1")

            canonical, patch = make_fixture(root / "second")
            manifest_path = patch / "PATCH_MANIFEST.json"
            manifest = json.loads(manifest_path.read_text())
            manifest["approved"] = True
            manifest_path.write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError, "non-applying and unapproved"):
                stager.stage(canonical, patch, root / "staging2")


if __name__ == "__main__":
    unittest.main()

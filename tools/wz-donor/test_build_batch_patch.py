#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("build_batch_patch.py")
SPEC = importlib.util.spec_from_file_location("build_batch_patch", MODULE_PATH)
assert SPEC and SPEC.loader
builder = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = builder
SPEC.loader.exec_module(builder)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def batch() -> dict:
    return {
        "batchId": "gms-v95-consume-batch-001",
        "mode": "review-only",
        "automaticImport": False,
        "approved": False,
        "candidates": [
            {
                "contentId": "2022711",
                "name": "Carbonated Drink",
                "sourcePath": "Item.wz/Consume/0202.img.xml",
                "approved": False,
            },
            {
                "contentId": "2022712",
                "name": "Acorn",
                "sourcePath": "Item.wz/Consume/0202.img.xml",
                "approved": False,
            },
        ],
    }


class PatchBuilderTest(unittest.TestCase):
    def make_fixture(self, root: Path) -> tuple[Path, Path]:
        donor = root / "donor"
        strings = root / "strings"
        write(
            donor / "Item.wz/Consume/0202.img.xml",
            '''<imgdir name="0202.img">
              <imgdir name="02022711"><imgdir name="info"><canvas name="icon"/></imgdir><imgdir name="spec"><int name="hp" value="1000"/><int name="mp" value="1000"/></imgdir></imgdir>
              <imgdir name="02022712"><imgdir name="info"><canvas name="icon"/></imgdir><imgdir name="spec"><int name="hp" value="70"/><int name="mp" value="70"/></imgdir></imgdir>
              <imgdir name="02029999"><imgdir name="spec"><int name="hp" value="1"/></imgdir></imgdir>
            </imgdir>''',
        )
        write(
            strings / "String.wz/Consume.img.xml",
            '''<imgdir name="Consume.img">
              <imgdir name="2022711"><string name="name" value="Carbonated Drink"/><string name="desc" value="Drink"/></imgdir>
              <imgdir name="2022712"><string name="name" value="Acorn"/><string name="desc" value="Acorn"/></imgdir>
              <imgdir name="2029999"><string name="name" value="Unselected"/></imgdir>
            </imgdir>''',
        )
        return donor, strings

    def test_builds_only_selected_item_and_string_nodes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            donor, strings = self.make_fixture(root)
            out = root / "out"
            manifest = builder.build(batch(), donor, strings, out)

            self.assertFalse(manifest["applyAllowed"])
            self.assertFalse(manifest["approved"])
            self.assertEqual(["2022711", "2022712"], manifest["candidateIds"])

            item_root = ET.parse(out / "Item.wz/Consume/0202.img.xml").getroot()
            item_ids = [builder.canonical_id(node.attrib.get("name")) for node in list(item_root)]
            self.assertEqual(["2022711", "2022712"], item_ids)

            string_root = ET.parse(out / "String.wz/Consume.img.xml").getroot()
            string_ids = [builder.canonical_id(node.attrib.get("name")) for node in list(string_root)]
            self.assertEqual(["2022711", "2022712"], string_ids)
            self.assertTrue((out / "PATCH_MANIFEST.json").exists())

    def test_name_mismatch_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            donor, strings = self.make_fixture(root)
            altered = batch()
            altered["candidates"][0]["name"] = "Wrong Name"
            with self.assertRaisesRegex(ValueError, "String.wz name mismatch"):
                builder.build(altered, donor, strings, root / "out")

    def test_approved_batch_or_candidate_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            donor, strings = self.make_fixture(root)
            approved_batch = batch()
            approved_batch["approved"] = True
            with self.assertRaisesRegex(ValueError, "review-only"):
                builder.build(approved_batch, donor, strings, root / "out1")

            approved_candidate = batch()
            approved_candidate["candidates"][0]["approved"] = True
            with self.assertRaisesRegex(ValueError, "candidate approved"):
                builder.build(approved_candidate, donor, strings, root / "out2")


if __name__ == "__main__":
    unittest.main()

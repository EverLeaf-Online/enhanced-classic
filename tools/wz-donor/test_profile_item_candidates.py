#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("profile_item_candidates.py")
SPEC = importlib.util.spec_from_file_location("profile_item_candidates", MODULE_PATH)
assert SPEC and SPEC.loader
profiler = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = profiler
SPEC.loader.exec_module(profiler)


def write_xml(root: Path, relative: str, body: str) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def candidate(content_id: str, path: str, risk: str = "low", missing: list | None = None) -> dict:
    return {
        "category": "items",
        "contentId": content_id,
        "sourcePath": path,
        "risk": risk,
        "missingDependencies": missing or [],
    }


class ItemProfilerTest(unittest.TestCase):
    def test_plain_restore_consume_is_first_batch_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            donor = root / "donor"
            strings = root / "strings"
            write_xml(
                donor,
                "Item.wz/Consume/0200.img.xml",
                '''<imgdir name="0200.img">
                  <imgdir name="02001500">
                    <imgdir name="info"><int name="price" value="100"/></imgdir>
                    <imgdir name="spec"><int name="hp" value="500"/><int name="mp" value="500"/></imgdir>
                  </imgdir>
                </imgdir>''',
            )
            write_xml(
                strings,
                "String.wz/Consume.img.xml",
                '''<imgdir name="Consume.img">
                  <imgdir name="02001500"><string name="name" value="Test Potion"/><string name="desc" value="Restores HP and MP."/></imgdir>
                </imgdir>''',
            )
            manifest = {"donorId": "test", "candidates": [candidate("2001500", "Item.wz/Consume/0200.img.xml")]}
            report = profiler.build_profiles(manifest, donor, strings)
            profile = report["profiles"][0]
            self.assertEqual("simple-consume", profile["classification"])
            self.assertEqual("Test Potion", profile["name"])
            self.assertEqual(["hp", "mp"], profile["specProperties"])
            self.assertFalse(profile["approved"])

    def test_buff_consume_stays_manual_review(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            donor = Path(tmp) / "donor"
            write_xml(
                donor,
                "Item.wz/Consume/0202.img.xml",
                '''<imgdir name="0202.img">
                  <imgdir name="02020001"><imgdir name="spec"><int name="time" value="300"/><int name="pad" value="10"/></imgdir></imgdir>
                </imgdir>''',
            )
            manifest = {"candidates": [candidate("2020001", "Item.wz/Consume/0202.img.xml")]}
            profile = profiler.build_profiles(manifest, donor)["profiles"][0]
            self.assertEqual("manual-review", profile["classification"])
            self.assertIn("non-restore-spec:pad,time", profile["reasons"])

    def test_non_consume_and_blocked_candidates_never_become_simple(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            donor = Path(tmp) / "donor"
            write_xml(
                donor,
                "Item.wz/Etc/0400.img.xml",
                '<imgdir name="0400.img"><imgdir name="04000001"><imgdir name="spec"><int name="hp" value="1"/></imgdir></imgdir></imgdir>',
            )
            write_xml(
                donor,
                "Item.wz/Consume/0200.img.xml",
                '<imgdir name="0200.img"><imgdir name="02001501"><imgdir name="spec"><int name="hp" value="1"/></imgdir></imgdir></imgdir>',
            )
            manifest = {
                "candidates": [
                    candidate("4000001", "Item.wz/Etc/0400.img.xml"),
                    candidate("2001501", "Item.wz/Consume/0200.img.xml", risk="blocked", missing=[{"target_id": "1"}]),
                ]
            }
            profiles = {
                profile["contentId"]: profile
                for profile in profiler.build_profiles(manifest, donor)["profiles"]
            }
            self.assertEqual("manual-review", profiles["4000001"]["classification"])
            self.assertEqual("blocked", profiles["2001501"]["classification"])

    def test_string_index_requires_direct_name_string(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            strings = Path(tmp)
            write_xml(
                strings,
                "String.wz/Consume.img.xml",
                '''<imgdir name="Consume.img">
                  <imgdir name="02001500"><string name="name" value="Potion"/></imgdir>
                  <imgdir name="123"><imgdir name="0"><string name="name" value="Nested frame"/></imgdir></imgdir>
                </imgdir>''',
            )
            index = profiler.build_string_index(strings)
            self.assertEqual("Potion", index["2001500"]["name"])
            self.assertNotIn("123", index)


if __name__ == "__main__":
    unittest.main()

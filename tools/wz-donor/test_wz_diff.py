#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("wz_diff.py")
SPEC = importlib.util.spec_from_file_location("wz_diff", MODULE_PATH)
assert SPEC and SPEC.loader
wz_diff = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = wz_diff
SPEC.loader.exec_module(wz_diff)


def write_xml(root: Path, relative: str, body: str) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


class WzDiffTest(unittest.TestCase):
    def test_detects_new_and_changed_ids(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            baseline = workspace / "baseline"
            donor = workspace / "donor"

            write_xml(baseline, "Mob.wz/0100100.img.xml", '<imgdir name="0100100.img"><int name="level" value="1"/></imgdir>')
            write_xml(donor, "Mob.wz/0100100.img.xml", '<imgdir name="0100100.img"><int name="level" value="2"/></imgdir>')
            write_xml(donor, "Mob.wz/0100101.img.xml", '<imgdir name="0100101.img"><int name="level" value="3"/></imgdir>')

            report = wz_diff.compare(wz_diff.inventory(baseline), wz_diff.inventory(donor))
            mobs = report["categories"]["mobs"]

            self.assertEqual(["100101"], mobs["newIds"])
            self.assertEqual(["100100"], mobs["collisionIds"])
            self.assertEqual(["100100"], mobs["changedCollisionIds"])

    def test_extracts_map_life_and_portal_dependencies(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            baseline = workspace / "baseline"
            donor = workspace / "donor"

            write_xml(baseline, "Map.wz/Map/Map0/100000000.img.xml", '<imgdir name="100000000.img"/>')
            write_xml(baseline, "Mob.wz/0100100.img.xml", '<imgdir name="0100100.img"/>')
            write_xml(
                donor,
                "Map.wz/Map/Map1/200000000.img.xml",
                '''<imgdir name="200000000.img">
                  <imgdir name="portal">
                    <imgdir name="0"><int name="tm" value="100000000"/></imgdir>
                  </imgdir>
                  <imgdir name="life">
                    <imgdir name="0"><string name="type" value="m"/><string name="id" value="0100100"/></imgdir>
                    <imgdir name="1"><string name="type" value="n"/><string name="id" value="9000000"/></imgdir>
                  </imgdir>
                </imgdir>''',
            )

            baseline_inventory = wz_diff.inventory(baseline)
            donor_inventory = wz_diff.inventory(donor)
            dependencies = wz_diff.analyze_dependencies(donor, baseline_inventory, donor_inventory)

            self.assertEqual(3, dependencies["referenceCount"])
            self.assertEqual(1, dependencies["missingReferenceCount"])
            missing = dependencies["missingReferences"][0]
            self.assertEqual("npcs", missing["target_category"])
            self.assertEqual("9000000", missing["target_id"])

    def test_grouped_item_files_inventory_real_child_ids(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            baseline = workspace / "baseline"
            donor = workspace / "donor"

            write_xml(
                baseline,
                "Item.wz/Consume/0200.img.xml",
                '''<imgdir name="0200.img">
                  <imgdir name="02000000"><imgdir name="info"><int name="price" value="25"/></imgdir></imgdir>
                </imgdir>''',
            )
            write_xml(
                donor,
                "Item.wz/Consume/0200.img.xml",
                '''<imgdir name="0200.img">
                  <imgdir name="02000000"><imgdir name="info"><int name="price" value="25"/></imgdir></imgdir>
                  <imgdir name="02000001"><imgdir name="info"><int name="price" value="80"/></imgdir></imgdir>
                </imgdir>''',
            )

            report = wz_diff.compare(wz_diff.inventory(baseline), wz_diff.inventory(donor))
            items = report["categories"]["items"]

            self.assertEqual(["2000001"], items["newIds"])
            self.assertEqual(["2000000"], items["collisionIds"])
            self.assertEqual([], items["changedCollisionIds"])
            self.assertNotIn("200", items["newIds"])

    def test_grouped_item_dependency_scan_is_scoped_to_item(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            donor = workspace / "donor"

            write_xml(
                donor,
                "Item.wz/Etc/0400.img.xml",
                '''<imgdir name="0400.img">
                  <imgdir name="04000000"><int name="itemid" value="02000000"/></imgdir>
                  <imgdir name="04000001"><int name="itemid" value="02000001"/></imgdir>
                </imgdir>''',
            )
            write_xml(
                donor,
                "Item.wz/Consume/0200.img.xml",
                '''<imgdir name="0200.img">
                  <imgdir name="02000000"/>
                  <imgdir name="02000001"/>
                </imgdir>''',
            )

            inventory = wz_diff.inventory(donor)
            refs = wz_diff.references_for_entry(donor, inventory["items"]["4000000"])

            self.assertEqual(1, len(refs))
            ref = next(iter(refs))
            self.assertEqual("4000000", ref.source_id)
            self.assertEqual("2000000", ref.target_id)

    def test_single_item_file_falls_back_to_filename_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tree = Path(tmp)
            write_xml(
                tree,
                "Item.wz/Pet/5000038.img.xml",
                '<imgdir name="5000038.img"><imgdir name="info"><int name="life" value="90"/></imgdir></imgdir>',
            )

            inventory = wz_diff.inventory(tree)
            self.assertEqual({"5000038"}, set(inventory["items"]))

    def test_root_level_item_system_metadata_is_not_inventory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tree = Path(tmp)
            write_xml(
                tree,
                "Item.wz/ItemOption.img.xml",
                '''<imgdir name="ItemOption.img">
                  <imgdir name="000001"><int name="optionType" value="1"/></imgdir>
                  <imgdir name="000901"><int name="optionType" value="2"/></imgdir>
                </imgdir>''',
            )
            write_xml(
                tree,
                "Item.wz/Consume/0200.img.xml",
                '''<imgdir name="0200.img">
                  <imgdir name="02000000"/>
                </imgdir>''',
            )

            inventory = wz_diff.inventory(tree)
            self.assertEqual({"2000000"}, set(inventory["items"]))
            self.assertNotIn("1", inventory["items"])
            self.assertNotIn("901", inventory["items"])

    def test_quest_nested_ids_are_inventoried(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tree = Path(tmp)
            write_xml(
                tree,
                "Quest.wz/QuestInfo.img.xml",
                '<imgdir name="QuestInfo.img"><imgdir name="1000"><string name="name" value="A"/></imgdir><imgdir name="1001"><string name="name" value="B"/></imgdir></imgdir>',
            )

            inventory = wz_diff.inventory(tree)
            self.assertEqual({"1000", "1001"}, set(inventory["quests"]))


if __name__ == "__main__":
    unittest.main()

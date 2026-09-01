#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("wz_diff.py")
SPEC = importlib.util.spec_from_file_location("wz_diff", MODULE_PATH)
wz_diff = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
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

            self.assertEqual(["0100101"], mobs["newIds"])
            self.assertEqual(["0100100"], mobs["collisionIds"])
            self.assertEqual(["0100100"], mobs["changedCollisionIds"])

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

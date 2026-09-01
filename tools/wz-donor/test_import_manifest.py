#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("build_import_manifest.py")
SPEC = importlib.util.spec_from_file_location("build_import_manifest", MODULE_PATH)
assert SPEC and SPEC.loader
module = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = module
SPEC.loader.exec_module(module)


class ImportManifestTest(unittest.TestCase):
    def test_candidates_default_to_unapproved_and_missing_dependencies_block(self) -> None:
        report = {
            "donorId": "gms-v95",
            "baseline": "wz",
            "donor": "/tmp/v95",
            "categories": {
                "maps": {
                    "newEntries": [
                        {
                            "category": "maps",
                            "content_id": "200000000",
                            "relative_path": "Map.wz/Map/Map2/200000000.img.xml",
                            "sha256": "abc",
                        }
                    ]
                },
                "items": {
                    "newEntries": [
                        {
                            "category": "items",
                            "content_id": "4000000",
                            "relative_path": "Item.wz/Etc/0400.img.xml",
                            "sha256": "def",
                        }
                    ]
                },
            },
            "dependencies": {
                "missingBySource": {
                    "maps:200000000": [
                        {
                            "source_category": "maps",
                            "source_id": "200000000",
                            "target_category": "npcs",
                            "target_id": "9000000",
                            "property_name": "life.n.id",
                            "relative_path": "Map.wz/Map/Map2/200000000.img.xml",
                        }
                    ]
                }
            },
        }

        manifest = module.build_manifest(report)
        self.assertEqual(2, manifest["candidateCount"])
        self.assertTrue(all(candidate["approved"] is False for candidate in manifest["candidates"]))

        by_id = {candidate["contentId"]: candidate for candidate in manifest["candidates"]}
        self.assertEqual("blocked", by_id["200000000"]["risk"])
        self.assertEqual("low", by_id["4000000"]["risk"])
        self.assertEqual(1, manifest["riskCounts"]["blocked"])


if __name__ == "__main__":
    unittest.main()

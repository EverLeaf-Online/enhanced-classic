#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("render_review_report.py")
SPEC = importlib.util.spec_from_file_location("render_review_report", MODULE_PATH)
assert SPEC and SPEC.loader
render_review_report = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = render_review_report
SPEC.loader.exec_module(render_review_report)


class RenderReviewReportTest(unittest.TestCase):
    def test_renders_risk_breakdown_and_samples(self) -> None:
        diff = {
            "donorId": "gms-v95",
            "totals": {"baseline": 100, "donor": 104, "new": 4, "collisions": 2, "changed": 1},
            "dependencies": {"missingReferenceCount": 1},
        }
        manifest = {
            "donorId": "gms-v95",
            "candidateCount": 3,
            "riskCounts": {"low": 1, "medium": 1, "high": 0, "blocked": 1},
            "candidates": [
                {
                    "category": "items",
                    "contentId": "2000000",
                    "sourcePath": "Item.wz/Consume/0200.img.xml",
                    "risk": "low",
                    "approved": False,
                    "missingDependencies": [],
                },
                {
                    "category": "mobs",
                    "contentId": "9300000",
                    "sourcePath": "Mob.wz/9300000.img.xml",
                    "risk": "medium",
                    "approved": False,
                    "missingDependencies": [],
                },
                {
                    "category": "maps",
                    "contentId": "200000000",
                    "sourcePath": "Map.wz/Map/Map2/200000000.img.xml",
                    "risk": "blocked",
                    "approved": False,
                    "missingDependencies": [
                        {"target_category": "npcs", "target_id": "9000000"}
                    ],
                },
            ],
        }

        text = render_review_report.render(diff, manifest)
        self.assertIn("# EverLeaf WZ donor review — gms-v95", text)
        self.assertIn("Candidates: **3**", text)
        self.assertIn("New IDs: **4**", text)
        self.assertIn("Collisions: **2**", text)
        self.assertIn("Changed collisions: **1**", text)
        self.assertIn("| items | 1 | 0 | 0 | 0 | 1 |", text)
        self.assertIn("`maps:200000000` — npcs:9000000", text)
        self.assertIn("[ ] `items:2000000`", text)
        self.assertIn("approved=false", text)

    def test_sample_limit_can_hide_examples(self) -> None:
        diff = {"totals": {}, "dependencies": {}}
        manifest = {
            "donorId": "test",
            "candidateCount": 1,
            "riskCounts": {"low": 1},
            "candidates": [
                {
                    "category": "items",
                    "contentId": "1",
                    "sourcePath": "Item.wz/1.xml",
                    "risk": "low",
                    "missingDependencies": [],
                }
            ],
        }
        text = render_review_report.render(diff, manifest, sample_limit=0)
        self.assertNotIn("`items:1`", text)
        self.assertIn("…and 1 more low-risk candidates", text)


if __name__ == "__main__":
    unittest.main()

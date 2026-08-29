#!/usr/bin/env python3
import importlib.util
import os
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("everleaf_runtime_qa.py")
spec = importlib.util.spec_from_file_location("everleaf_runtime_qa", MODULE_PATH)
mod = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(mod)


class RuntimeQATests(unittest.TestCase):
    def setUp(self):
        os.environ.pop("EVERLEAF_QA_RUNTIME", None)
        os.environ.pop("EVERLEAF_QA_ACCOUNT_PREFIX", None)

    def test_production_environment_is_refused(self):
        results = mod.safety_gate("production", "qa_bot", False)
        self.assertTrue(any(r.check == "environment" and r.status == "FAIL" for r in results))

    def test_non_qa_account_is_refused(self):
        results = mod.safety_gate("staging", "realplayer", False)
        self.assertTrue(any(r.check == "qa-account" and r.status == "FAIL" for r in results))

    def test_actions_need_arm_token(self):
        results = mod.safety_gate("staging", "qa_bot", True)
        self.assertTrue(any(r.check == "runtime-arm" and r.status == "FAIL" for r in results))

    def test_armed_staging_qa_account_passes(self):
        os.environ["EVERLEAF_QA_RUNTIME"] = mod.ARM_TOKEN
        results = mod.safety_gate("staging", "qa_bot", True)
        self.assertFalse(any(r.status == "FAIL" for r in results))

    def test_persistence_equal_passes(self):
        snap = {"level": 10, "exp": 100, "mesos": 500, "inventory": {"2000000": 3}}
        results = mod.compare_snapshots(snap, dict(snap), "persistence")
        self.assertEqual(results[0].status, "PASS")

    def test_persistence_delta_fails(self):
        before = {"level": 10, "exp": 100}
        after = {"level": 10, "exp": 101}
        results = mod.compare_snapshots(before, after, "persistence")
        self.assertEqual(results[0].status, "FAIL")

    def test_conservation_passes(self):
        before = {"assets": {"mesos": 1000, "item_count": 5}}
        after = {"assets": {"mesos": 1000, "item_count": 5}}
        results = mod.compare_snapshots(before, after, "conservation", ["assets.mesos", "assets.item_count"])
        self.assertEqual(results[0].status, "PASS")

    def test_conservation_detects_dupe_or_loss(self):
        before = {"assets": {"mesos": 1000, "item_count": 5}}
        after = {"assets": {"mesos": 1100, "item_count": 6}}
        results = mod.compare_snapshots(before, after, "conservation", ["assets.mesos", "assets.item_count"])
        self.assertEqual(results[0].status, "FAIL")
        self.assertIn("assets.mesos", results[0].evidence)
        self.assertIn("assets.item_count", results[0].evidence)


if __name__ == "__main__":
    unittest.main()

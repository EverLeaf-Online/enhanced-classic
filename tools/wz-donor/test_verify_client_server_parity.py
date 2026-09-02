#!/usr/bin/env python3

import copy
import importlib.util
import pathlib
import unittest

MODULE_PATH = pathlib.Path(__file__).with_name("verify_client_server_parity.py")
spec = importlib.util.spec_from_file_location("verify_client_server_parity", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


class VerifyClientServerParityTest(unittest.TestCase):
    def setUp(self):
        self.contract = {
            "schemaVersion": 1,
            "kind": "client-server-parity-contract",
            "batchId": "gms-v95-consume-batch-001",
            "approved": False,
            "productionApplyAllowed": False,
            "sourceClient": {
                "item": {"version": 83, "sha256": "a" * 64},
                "string": {"version": 83, "sha256": "b" * 64},
            },
            "donor": {
                "item": {"version": 95, "sha256": "c" * 64},
                "string": {"version": 95, "sha256": "d" * 64},
            },
            "candidateIds": [2022711, 2022712],
            "candidates": [
                {
                    "contentId": 2022711,
                    "name": "Carbonated Drink",
                    "description": "drink desc",
                    "hp": 1000,
                    "mp": 1000,
                    "price": None,
                    "slotMax": None,
                    "requiresCanvasIcons": True,
                },
                {
                    "contentId": 2022712,
                    "name": "Acorn",
                    "description": "acorn desc",
                    "hp": 70,
                    "mp": 70,
                    "price": 10,
                    "slotMax": 20,
                    "requiresCanvasIcons": True,
                },
            ],
        }
        self.manifest = {
            "schemaVersion": 2,
            "kind": "isolated-client-wz-candidate",
            "batchId": "gms-v95-consume-batch-001",
            "candidateIds": [2022711, 2022712],
            "approved": False,
            "productionApplyAllowed": False,
            "sourceClient": {
                "item": {"version": 83, "sha256": "a" * 64, "size": 1},
                "string": {"version": 83, "sha256": "b" * 64, "size": 1},
            },
            "donor": {
                "item": {"version": 95, "sha256": "c" * 64, "size": 1},
                "string": {"version": 95, "sha256": "d" * 64, "size": 1},
            },
            "output": {
                "item": {"sha256": "e" * 64, "size": 2},
                "string": {"sha256": "f" * 64, "size": 2},
            },
            "semantics": [
                {
                    "contentId": 2022711,
                    "name": "Carbonated Drink",
                    "description": "drink desc",
                    "hp": 1000,
                    "mp": 1000,
                    "price": None,
                    "slotMax": None,
                    "iconPropertyType": "WzCanvasProperty",
                    "iconRawPropertyType": "WzCanvasProperty",
                },
                {
                    "contentId": 2022712,
                    "name": "Acorn",
                    "description": "acorn desc",
                    "hp": 70,
                    "mp": 70,
                    "price": 10,
                    "slotMax": 20,
                    "iconPropertyType": "WzCanvasProperty",
                    "iconRawPropertyType": "WzCanvasProperty",
                },
            ],
            "validation": {
                "sourceClientUnchanged": True,
                "outputReparsed": True,
                "exactCandidateIds": True,
                "donorNodesDeepCloned": True,
                "iconCanvasesPreserved": True,
                "semanticValuesReadAfterReparse": True,
            },
        }

    def test_valid_manifest_passes(self):
        report = module.verify(self.contract, self.manifest)
        self.assertTrue(report["passed"])
        self.assertEqual([], report["errors"])

    def test_semantic_drift_fails(self):
        manifest = copy.deepcopy(self.manifest)
        manifest["semantics"][1]["hp"] = 71
        report = module.verify(self.contract, manifest)
        self.assertFalse(report["passed"])
        self.assertTrue(any("2022712 hp mismatch" in error for error in report["errors"]))

    def test_source_hash_drift_fails(self):
        manifest = copy.deepcopy(self.manifest)
        manifest["sourceClient"]["item"]["sha256"] = "9" * 64
        report = module.verify(self.contract, manifest)
        self.assertFalse(report["passed"])
        self.assertTrue(any("sourceClient.item.sha256 mismatch" in error for error in report["errors"]))

    def test_approval_flip_fails(self):
        manifest = copy.deepcopy(self.manifest)
        manifest["approved"] = True
        report = module.verify(self.contract, manifest)
        self.assertFalse(report["passed"])
        self.assertIn("client manifest approved must remain false", report["errors"])

    def test_non_canvas_icon_fails(self):
        manifest = copy.deepcopy(self.manifest)
        manifest["semantics"][0]["iconPropertyType"] = "WzStringProperty"
        report = module.verify(self.contract, manifest)
        self.assertFalse(report["passed"])
        self.assertTrue(any("iconPropertyType is not a canvas" in error for error in report["errors"]))


if __name__ == "__main__":
    unittest.main()

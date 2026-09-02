#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("verify_batch_manifest.py")
SPEC = importlib.util.spec_from_file_location("verify_batch_manifest", MODULE_PATH)
assert SPEC and SPEC.loader
verifier = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = verifier
SPEC.loader.exec_module(verifier)


def batch_candidate(cid: str, name: str, hp: float, mp: float, source_sha: str) -> dict:
    return {
        "category": "items",
        "contentId": cid,
        "name": name,
        "description": f"{name} description",
        "sourcePath": "Item.wz/Consume/0202.img.xml",
        "sourceSha256": source_sha,
        "family": "Consume",
        "classification": "simple-consume",
        "manifestRisk": "low",
        "restoreValues": {"hp": hp, "mp": mp},
        "infoProperties": ["icon", "iconraw"],
        "specProperties": ["hp", "mp"],
        "missingDependencies": [],
        "duplicateOf": [],
        "approved": False,
    }


def profile_entry(candidate: dict) -> dict:
    return {
        "contentId": candidate["contentId"],
        "sourcePath": candidate["sourcePath"],
        "family": candidate["family"],
        "classification": candidate["classification"],
        "name": candidate["name"],
        "description": candidate["description"],
        "infoProperties": candidate["infoProperties"],
        "specProperties": candidate["specProperties"],
        "restoreValues": candidate["restoreValues"],
        "duplicateOf": candidate["duplicateOf"],
        "approved": False,
    }


def manifest_entry(candidate: dict) -> dict:
    return {
        "category": "items",
        "contentId": candidate["contentId"],
        "sourcePath": candidate["sourcePath"],
        "sourceSha256": candidate["sourceSha256"],
        "risk": candidate["manifestRisk"],
        "approved": False,
        "missingDependencies": [],
    }


class BatchVerifierTest(unittest.TestCase):
    def setUp(self) -> None:
        self.a = batch_candidate("2022711", "Carbonated Drink", 1000.0, 1000.0, "a" * 64)
        self.b = batch_candidate("2022712", "Acorn", 70.0, 70.0, "b" * 64)
        self.batch = {
            "batchId": "gms-v95-consume-batch-001",
            "mode": "review-only",
            "automaticImport": False,
            "approved": False,
            "candidates": [self.a, self.b],
        }
        self.profile = {"profiles": [profile_entry(self.a), profile_entry(self.b)]}
        self.manifest = {"candidates": [manifest_entry(self.a), manifest_entry(self.b)]}

    def test_exact_review_only_batch_passes(self) -> None:
        self.assertEqual([], verifier.verify(self.batch, self.profile, self.manifest))

    def test_source_hash_drift_fails(self) -> None:
        self.manifest["candidates"][0]["sourceSha256"] = "c" * 64
        errors = verifier.verify(self.batch, self.profile, self.manifest)
        self.assertIn("2022711: import manifest mismatch for sourceSha256", errors)

    def test_new_simple_candidate_fails_closed(self) -> None:
        extra = batch_candidate("2022999", "Unexpected", 1.0, 1.0, "d" * 64)
        self.profile["profiles"].append(profile_entry(extra))
        errors = verifier.verify(self.batch, self.profile, self.manifest)
        self.assertTrue(any("current simple-consume set drifted" in error for error in errors))

    def test_approval_or_negative_restore_fails(self) -> None:
        self.batch["approved"] = True
        self.a["restoreValues"]["hp"] = -1.0
        errors = verifier.verify(self.batch, self.profile, self.manifest)
        self.assertIn("batch approved must be false", errors)
        self.assertIn("2022711: restore value hp must be positive", errors)


if __name__ == "__main__":
    unittest.main()

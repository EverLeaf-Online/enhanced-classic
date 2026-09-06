import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("audit", Path(__file__).with_name("audit-native-package.py"))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class PackageAuditTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name) / "base"
        self.candidate = Path(self.temp.name) / "candidate"
        for root in (self.base, self.candidate):
            root.mkdir()
            for name in module.REQUIRED:
                (root / name).write_bytes(b"production")

    def run_audit(self):
        return module.audit(self.candidate, self.base)

    def test_ui_only_change_passes_but_is_not_release_approval(self):
        (self.candidate / "ui.wz").write_bytes(b"donor UI")
        report = self.run_audit()
        self.assertTrue(report["structuralAndPreservationChecksPassed"])
        self.assertFalse(report["releaseReady"])

    def test_v95_data_change_blocks(self):
        (self.candidate / "mob.wz").write_bytes(b"old donor mobs")
        self.assertIn("Protected production file differs: mob.wz", self.run_audit()["errors"])

    def test_donor_runtime_blocks_case_insensitively(self):
        (self.candidate / "YuNaMs.DLL").write_bytes(b"runtime")
        self.assertTrue(any("Forbidden donor" in x for x in self.run_audit()["errors"]))

    def test_missing_protected_data_blocks(self):
        (self.candidate / "skill.wz").unlink()
        self.assertTrue(any("skill.wz" in x for x in self.run_audit()["errors"]))

    def test_windows_name_collision_blocks(self):
        (self.candidate / "UI.WZ").write_bytes(b"collision")
        self.assertTrue(any("collision" in x for x in self.run_audit()["errors"]))

    def test_symlink_blocks(self):
        (self.candidate / "linked").symlink_to(self.base / "ui.wz")
        self.assertTrue(any("non-regular" in x for x in self.run_audit()["errors"]))

    def test_chunk_boundary_and_utf16_matches_are_review_only(self):
        payload = b"x" * (module.CHUNK - 2) + b"YuNa" + "MAPLEEZORSIA".encode("utf-16le")
        for root in (self.base, self.candidate):
            (root / "map.wz").write_bytes(payload)
        report = self.run_audit()
        self.assertTrue(report["structuralAndPreservationChecksPassed"])
        match = report["rawBrandingMatchesForReview"][0]
        self.assertEqual(match["tokens"], ["ezorsia", "mapleezorsia", "yuna"])
        self.assertTrue(match["sameAsBaseline"])

if __name__ == "__main__":
    unittest.main()

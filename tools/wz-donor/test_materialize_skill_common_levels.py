#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).resolve().parent
MODULE_PATH = HERE / "materialize_skill_common_levels.py"
spec = importlib.util.spec_from_file_location("materialize_skill_common_levels", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


def assert_eq(actual, expected, message=""):
    if actual != expected:
        raise AssertionError(f"{message} expected={expected!r} actual={actual!r}")


def formula_tests() -> None:
    cases = [
        ("16+2*d(x/4)", 1, 16),
        ("16+2*d(x/4)", 4, 18),
        ("16+2*d(x/4)", 7, 18),
        ("u(x/2)", 1, 1),
        ("u(x/2)", 2, 1),
        ("u(x/2)", 3, 2),
        ("260-40*d(x/4)", 20, 60),
        ("-(x/2)", 1, -1),  # -0.5 rounds away from zero
        ("x/2", 1, 1),      # +0.5 rounds away from zero
        ("2*(3+x)", 4, 14),
    ]
    for expression, level, expected in cases:
        assert_eq(module.evaluate_formula(expression, level), expected, expression)


def integration_test() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        source = tmp / "source"
        out = tmp / "out"
        source.mkdir()
        (source / "100.img.xml").write_text(
            '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<imgdir name="100.img">
  <imgdir name="skill">
    <imgdir name="1001000">
      <imgdir name="common">
        <int name="maxLevel" value="3" />
        <string name="mpCon" value="10+2*d(x/2)" />
        <string name="damage" value="100+5*x" />
        <vector name="lt" x="-50" y="-20" />
        <int name="range" value="400" />
      </imgdir>
    </imgdir>
    <imgdir name="1001001">
      <imgdir name="common">
        <string name="maxLevel" value="2" />
        <string name="x" value="u(x/2)" />
      </imgdir>
    </imgdir>
  </imgdir>
</imgdir>
''',
            encoding="utf-8",
        )
        deferred = tmp / "deferred.json"
        deferred.write_text(
            json.dumps(
                {
                    "deferredModernCommonSkillIds": 2,
                    "rows": [{"deferredSkillIds": ["1001000", "1001001"]}],
                }
            ),
            encoding="utf-8",
        )

        manifest = module.materialize(source, deferred, out)
        assert_eq(manifest["requestedSkillCount"], 2)
        assert_eq(manifest["materializedSkillCount"], 2)
        assert_eq(manifest["generatedLevelCount"], 5)
        assert_eq(manifest["filesWritten"], 1)
        assert manifest["approved"] is False
        assert manifest["productionApplyAllowed"] is False

        root = ET.parse(out / "100.img.xml").getroot()
        skill_root = module.get_named_child(root, "skill")
        first = module.get_named_child(skill_root, "1001000")
        levels = module.get_named_child(first, "level")
        assert_eq([node.attrib["name"] for node in levels], ["1", "2", "3"])
        level1 = levels[0]
        level2 = levels[1]
        level3 = levels[2]
        assert_eq(module.get_named_child(level1, "mpCon").attrib["value"], "10")
        assert_eq(module.get_named_child(level2, "mpCon").attrib["value"], "12")
        assert_eq(module.get_named_child(level3, "mpCon").attrib["value"], "12")
        assert_eq(module.get_named_child(level3, "damage").attrib["value"], "115")
        assert_eq(module.get_named_child(level1, "range").attrib["value"], "400")
        assert_eq(module.get_named_child(level1, "lt").attrib["x"], "-50")

        second = module.get_named_child(skill_root, "1001001")
        second_levels = module.get_named_child(second, "level")
        assert_eq(module.get_named_child(second_levels[0], "x").attrib["value"], "1")
        assert_eq(module.get_named_child(second_levels[1], "x").attrib["value"], "1")

        output_manifest = json.loads((out / "MANIFEST.json").read_text(encoding="utf-8"))
        assert output_manifest["validation"]["allMaterializedSkillsReparsed"] is True
        assert output_manifest["validation"]["allGeneratedLevelsContiguous"] is True


def main() -> int:
    formula_tests()
    integration_test()
    print("PASS materialize_skill_common_levels")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

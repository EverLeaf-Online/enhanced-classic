#!/usr/bin/env python3
"""Materialize v180 Skill.wz common formulas into v83-style level nodes.

GMS v180 stores many skill values as compact formulas under ``common`` while
EverLeaf's v83 SkillFactory expects an explicit ``level/<n>`` property tree.
This staging tool expands only an explicit allowlist of deferred skill IDs and
never mutates the source tree.

Formula semantics follow HaCreator's SkillDataLoader:
- x = requested skill level
- d(expr) = floor(expr)
- u(expr) = ceil(expr)
- arithmetic operators: +, -, *, / and parentheses
- final numeric values are rounded to nearest integer, midpoint away from zero

The output remains review-only. The generated manifest always sets
approved=false and productionApplyAllowed=false.
"""

from __future__ import annotations

import argparse
import json
import math
import shutil
import xml.etree.ElementTree as ET
from collections import Counter
from copy import deepcopy
from pathlib import Path


class FormulaError(ValueError):
    pass


class FormulaParser:
    def __init__(self, expression: str, x_value: int):
        self.expression = expression or ""
        self.x_value = x_value
        self.index = 0

    def parse(self) -> float:
        value = self._parse_expression()
        self._skip_whitespace()
        if self.index != len(self.expression):
            raise FormulaError(
                f"unexpected token {self.expression[self.index]!r} at {self.index} in {self.expression!r}"
            )
        if not math.isfinite(value):
            raise FormulaError(f"non-finite result for {self.expression!r}")
        return value

    def _parse_expression(self) -> float:
        value = self._parse_term()
        while True:
            self._skip_whitespace()
            if self._match("+"):
                value += self._parse_term()
            elif self._match("-"):
                value -= self._parse_term()
            else:
                return value

    def _parse_term(self) -> float:
        value = self._parse_factor()
        while True:
            self._skip_whitespace()
            if self._match("*"):
                value *= self._parse_factor()
            elif self._match("/"):
                divisor = self._parse_factor()
                if divisor == 0:
                    raise FormulaError(f"division by zero in {self.expression!r}")
                value /= divisor
            else:
                return value

    def _parse_factor(self) -> float:
        self._skip_whitespace()
        if self._match("+"):
            return self._parse_factor()
        if self._match("-"):
            return -self._parse_factor()
        if self._match("("):
            value = self._parse_expression()
            self._expect(")")
            return value

        identifier = self._try_identifier()
        if identifier is not None:
            lowered = identifier.lower()
            if lowered == "x":
                return float(self.x_value)
            if lowered in {"u", "d"}:
                self._expect("(")
                inner = self._parse_expression()
                self._expect(")")
                return float(math.ceil(inner) if lowered == "u" else math.floor(inner))
            raise FormulaError(f"unsupported identifier {identifier!r} in {self.expression!r}")

        return self._parse_number()

    def _parse_number(self) -> float:
        self._skip_whitespace()
        start = self.index
        seen_dot = False
        while self.index < len(self.expression):
            ch = self.expression[self.index]
            if ch.isdigit():
                self.index += 1
                continue
            if ch == "." and not seen_dot:
                seen_dot = True
                self.index += 1
                continue
            break
        if start == self.index:
            raise FormulaError(f"expected number at {self.index} in {self.expression!r}")
        token = self.expression[start : self.index]
        try:
            return float(token)
        except ValueError as exc:
            raise FormulaError(f"invalid number {token!r} in {self.expression!r}") from exc

    def _try_identifier(self) -> str | None:
        self._skip_whitespace()
        start = self.index
        while self.index < len(self.expression) and self.expression[self.index].isalpha():
            self.index += 1
        if start == self.index:
            return None
        return self.expression[start : self.index]

    def _skip_whitespace(self) -> None:
        while self.index < len(self.expression) and self.expression[self.index].isspace():
            self.index += 1

    def _match(self, char: str) -> bool:
        self._skip_whitespace()
        if self.index >= len(self.expression) or self.expression[self.index] != char:
            return False
        self.index += 1
        return True

    def _expect(self, char: str) -> None:
        if not self._match(char):
            raise FormulaError(f"expected {char!r} at {self.index} in {self.expression!r}")


def round_away_from_zero(value: float) -> int:
    if value >= 0:
        return math.floor(value + 0.5)
    return math.ceil(value - 0.5)


def evaluate_formula(expression: str, level: int) -> int:
    return round_away_from_zero(FormulaParser(expression, level).parse())


def deferred_ids_from_manifest(path: Path) -> set[str]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    ids: set[str] = set()
    for row in data.get("rows", []):
        for value in row.get("deferredSkillIds", []):
            skill_id = str(value).strip()
            if not skill_id.isdigit():
                raise ValueError(f"invalid deferred skill id: {value!r}")
            if skill_id in ids:
                raise ValueError(f"duplicate deferred skill id: {skill_id}")
            ids.add(skill_id)
    expected = data.get("deferredModernCommonSkillIds")
    if expected is not None and len(ids) != int(expected):
        raise ValueError(f"deferred manifest count mismatch: {len(ids)} != {expected}")
    if not ids:
        raise ValueError("deferred skill manifest is empty")
    return ids


def get_named_child(parent: ET.Element, name: str) -> ET.Element | None:
    for child in parent:
        if child.attrib.get("name") == name:
            return child
    return None


def parse_max_level(common: ET.Element, skill_id: str) -> int:
    node = get_named_child(common, "maxLevel")
    if node is None:
        raise ValueError(f"skill {skill_id} common/maxLevel missing")
    raw = node.attrib.get("value", "")
    if node.tag == "string":
        value = evaluate_formula(raw, 1)
    elif node.tag in {"int", "short", "long"}:
        value = int(raw)
    else:
        raise ValueError(f"skill {skill_id} unsupported maxLevel tag {node.tag}")
    if value <= 0 or value > 255:
        raise ValueError(f"skill {skill_id} invalid maxLevel {value}")
    return value


def materialize_level_property(source: ET.Element, level: int, skill_id: str) -> ET.Element:
    name = source.attrib.get("name", "")
    if source.tag == "string":
        expression = source.attrib.get("value", "")
        value = evaluate_formula(expression, level)
        return ET.Element("int", {"name": name, "value": str(value)})
    if source.tag in {"int", "short", "long"}:
        value = int(source.attrib.get("value", "0"))
        return ET.Element("int", {"name": name, "value": str(value)})
    if source.tag == "vector":
        return deepcopy(source)
    raise ValueError(f"skill {skill_id} common/{name}: unsupported tag {source.tag}")


def indent_xml(root: ET.Element) -> None:
    ET.indent(root, space="  ")


def write_xml(path: Path, root: ET.Element) -> None:
    indent_xml(root)
    body = ET.tostring(root, encoding="unicode", short_empty_elements=True)
    path.write_text(
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n' + body + "\n",
        encoding="utf-8",
        newline="\n",
    )


def materialize(source_root: Path, deferred_manifest: Path, out_dir: Path) -> dict:
    requested = deferred_ids_from_manifest(deferred_manifest)
    remaining = set(requested)
    rows: list[dict] = []
    function_counts: Counter[str] = Counter()
    formula_count = 0
    generated_level_nodes = 0
    files_written = 0

    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)

    for source_file in sorted(source_root.glob("*.img.xml")):
        root = ET.parse(source_file).getroot()
        skill_root = get_named_child(root, "skill")
        if skill_root is None:
            continue

        changed_ids: list[str] = []
        file_level_count = 0
        for skill in list(skill_root):
            skill_id = skill.attrib.get("name", "")
            if skill_id not in requested:
                continue
            if skill_id not in remaining:
                raise ValueError(f"skill {skill_id} appears more than once")
            common = get_named_child(skill, "common")
            if common is None:
                raise ValueError(f"skill {skill_id} has no common node")
            if get_named_child(skill, "level") is not None:
                raise ValueError(f"skill {skill_id} already has a level node")

            max_level = parse_max_level(common, skill_id)
            level_root = ET.Element("imgdir", {"name": "level"})
            for level in range(1, max_level + 1):
                level_node = ET.SubElement(level_root, "imgdir", {"name": str(level)})
                for prop in common:
                    if prop.attrib.get("name") == "maxLevel":
                        continue
                    if prop.tag == "string":
                        formula_count += 1
                        expression = prop.attrib.get("value", "")
                        # Record the only supported WZ formula functions while the
                        # parser itself remains the authoritative syntax check.
                        for fn in ("d", "u"):
                            function_counts[fn] += expression.lower().count(fn + "(")
                    level_node.append(materialize_level_property(prop, level, skill_id))
                generated_level_nodes += 1
                file_level_count += 1

            # Keep the donor common node as provenance and add the v83-compatible
            # explicit level table immediately after it.
            insert_at = list(skill).index(common) + 1
            skill.insert(insert_at, level_root)
            remaining.remove(skill_id)
            changed_ids.append(skill_id)

        if not changed_ids:
            continue
        output_file = out_dir / source_file.name
        write_xml(output_file, root)
        files_written += 1
        rows.append(
            {
                "image": source_file.name,
                "materializedSkillCount": len(changed_ids),
                "generatedLevelCount": file_level_count,
                "skillIds": changed_ids,
            }
        )

    if remaining:
        raise ValueError(f"deferred skills missing from source XML: {sorted(remaining)[:30]}")

    # Reparse output and prove every requested skill now has exactly maxLevel
    # explicit level entries numbered 1..N.
    verified: set[str] = set()
    verified_levels = 0
    for output_file in sorted(out_dir.glob("*.img.xml")):
        root = ET.parse(output_file).getroot()
        skill_root = get_named_child(root, "skill")
        if skill_root is None:
            continue
        for skill in skill_root:
            skill_id = skill.attrib.get("name", "")
            if skill_id not in requested:
                continue
            common = get_named_child(skill, "common")
            level_root = get_named_child(skill, "level")
            if common is None or level_root is None:
                raise ValueError(f"output skill {skill_id} lost common/level")
            max_level = parse_max_level(common, skill_id)
            names = [child.attrib.get("name") for child in level_root]
            expected_names = [str(i) for i in range(1, max_level + 1)]
            if names != expected_names:
                raise ValueError(f"output skill {skill_id} level numbering mismatch")
            verified.add(skill_id)
            verified_levels += len(names)

    if verified != requested:
        raise ValueError(f"verification coverage mismatch: {len(verified)} != {len(requested)}")
    if verified_levels != generated_level_nodes:
        raise ValueError(f"generated level verification mismatch: {verified_levels} != {generated_level_nodes}")

    manifest = {
        "schemaVersion": 1,
        "kind": "everleaf-v180-common-skill-v83-level-materialization",
        "approved": False,
        "productionApplyAllowed": False,
        "sourceRoot": str(source_root),
        "deferredManifest": str(deferred_manifest),
        "requestedSkillCount": len(requested),
        "materializedSkillCount": len(verified),
        "generatedLevelCount": generated_level_nodes,
        "formulaPropertyEvaluationCount": formula_count,
        "formulaFunctionOccurrences": dict(sorted(function_counts.items())),
        "filesWritten": files_written,
        "formulaSemantics": {
            "x": "skill level",
            "d": "floor",
            "u": "ceil",
            "finalRounding": "nearest integer, midpoint away from zero",
            "operators": ["+", "-", "*", "/", "unary +", "unary -", "parentheses"],
        },
        "validation": {
            "allRequestedSkillsFound": True,
            "allMaterializedSkillsReparsed": True,
            "allGeneratedLevelsContiguous": True,
            "sourceTreeMutated": False,
            "productionApplyAllowed": False,
        },
        "rows": rows,
    }
    (out_dir / "MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    (out_dir / "README.txt").write_text(
        "EverLeaf v180 modern Skill.wz common-formula materialization for the v83 server. "
        "STAGING/REVIEW ONLY. No production apply.\n",
        encoding="utf-8",
    )
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--deferred-manifest", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()

    manifest = materialize(args.source_root, args.deferred_manifest, args.out_dir)
    print(
        json.dumps(
            {key: value for key, value in manifest.items() if key != "rows"},
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

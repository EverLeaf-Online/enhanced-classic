#!/usr/bin/env python3

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from cross_reference_item_shortlist import build_report


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main() -> int:
    shortlist = {
        "donorId": "gms-v95-core7",
        "candidates": [
            {"contentId": "4001001", "name": "Quest Drop", "approved": False},
            {"contentId": "4001002", "name": "Mob Drop", "approved": False},
            {"contentId": "4001003", "name": "Standalone", "approved": False},
        ],
    }

    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        donor = root / "donor"
        baseline = root / "baseline"

        write(donor / "Quest.wz" / "Check.img.xml", '<int name="item" value="4001001"/>\n')
        write(donor / "Mob.wz" / "9300000.img.xml", '<string name="drop" value="4001002"/>\n')
        write(donor / "Map.wz" / "Map0" / "100000000.img.xml", '<string name="noise" value="14001001"/>\n')
        write(baseline / "scripts" / "npc" / "test.js", 'var existing = 4001002;\n')
        write(baseline / "src" / "main" / "Example.java", 'int unrelated = 40010030;\n')

        report = build_report(shortlist, donor, baseline, sample_limit=1)

    assert report["candidateCount"] == 3
    assert report["crossReferencedCandidateCount"] == 2
    assert report["donorQuestReferencedCandidateCount"] == 1
    assert report["uncoupledCandidateCount"] == 1
    assert report["approved"] is False
    assert report["automaticImport"] is False

    rows = {row["contentId"]: row for row in report["candidates"]}
    quest = rows["4001001"]
    mob = rows["4001002"]
    standalone = rows["4001003"]

    assert quest["donorReferences"]["referenceCount"] == 1
    assert quest["donorReferences"]["byRoot"] == {"Quest.wz": 1}
    assert quest["hasDonorQuestReference"] is True
    assert quest["approved"] is False and quest["importAllowed"] is False

    assert mob["donorReferences"]["byRoot"] == {"Mob.wz": 1}
    assert mob["baselineReferences"]["referenceCount"] == 1
    assert mob["hasAnyCrossReference"] is True
    assert mob["hasDonorQuestReference"] is False

    assert standalone["donorReferences"]["referenceCount"] == 0
    assert standalone["baselineReferences"]["referenceCount"] == 0
    assert standalone["hasAnyCrossReference"] is False

    print(json.dumps({
        "candidateCount": report["candidateCount"],
        "crossReferencedCandidateCount": report["crossReferencedCandidateCount"],
        "donorQuestReferencedCandidateCount": report["donorQuestReferencedCandidateCount"],
        "uncoupledCandidateCount": report["uncoupledCandidateCount"],
    }, sort_keys=True))
    print("cross-reference shortlist regression: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

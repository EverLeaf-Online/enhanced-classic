#!/usr/bin/env python3
from __future__ import annotations

import tempfile
from pathlib import Path

from preview_drop_contract import build_report, read_snapshot


def main() -> int:
    contract = {
        "contractId": "fixture",
        "chanceScale": 999999,
        "rows": [
            {"dropperId": 9400400, "itemId": 4000337, "minimumQuantity": 1, "maximumQuantity": 1, "questId": 0, "chance": 400000},
            {"dropperId": 9400401, "itemId": 4000338, "minimumQuantity": 1, "maximumQuantity": 1, "questId": 0, "chance": 400000},
        ],
        "unresolvedItems": [4000339],
        "approved": False,
        "applyAllowed": False,
        "automaticApply": False,
    }

    with tempfile.TemporaryDirectory() as temp:
        snapshot = Path(temp) / "rows.tsv"
        snapshot.write_text(
            "9400400\t4000337\t1\t1\t0\t400000\n"
            "9400410\t4000339\t1\t1\t0\t100000\n",
            encoding="utf-8",
        )
        report = build_report(contract, read_snapshot(snapshot))

    assert report["counts"]["contractRows"] == 2
    assert report["counts"]["alreadyPresentRows"] == 1
    assert report["counts"]["missingRows"] == 1
    assert report["counts"]["unresolvedRowsAlreadyInProduction"] == 1
    assert report["comparisons"][0]["status"] == "already-present"
    assert report["comparisons"][1]["status"] == "missing"
    assert report["proposedSql"] == [
        "INSERT INTO drop_data (dropperid,itemid,minimum_quantity,maximum_quantity,questid,chance) VALUES (9400401,4000338,1,1,0,400000);"
    ]
    assert report["applyReady"] is False
    assert report["databaseWritePerformed"] is False
    assert report["approved"] is False and report["applyAllowed"] is False and report["automaticApply"] is False

    clean = build_report(contract, [])
    assert clean["counts"]["missingRows"] == 2
    assert clean["counts"]["conflictingPairs"] == 0
    assert clean["applyReady"] is True
    assert len(clean["proposedSql"]) == 2

    conflict = build_report(contract, [{
        "dropperId": 9400400,
        "itemId": 4000337,
        "minimumQuantity": 1,
        "maximumQuantity": 1,
        "questId": 0,
        "chance": 123,
    }])
    assert conflict["counts"]["conflictingPairs"] == 1
    assert conflict["applyReady"] is False
    assert any("conflict" in x for x in conflict["errors"])

    print("drop contract preview regression: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

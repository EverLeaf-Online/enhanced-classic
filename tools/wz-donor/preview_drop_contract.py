#!/usr/bin/env python3
"""Compare a frozen drop contract to a read-only drop_data snapshot and emit preview-only SQL."""
from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

COLUMNS = ("dropperid", "itemid", "minimum_quantity", "maximum_quantity", "questid", "chance")


def normalize_row(row):
    return {
        "dropperId": int(row["dropperid"]),
        "itemId": int(row["itemid"]),
        "minimumQuantity": int(row["minimum_quantity"]),
        "maximumQuantity": int(row["maximum_quantity"]),
        "questId": int(row["questid"]),
        "chance": int(row["chance"]),
    }


def contract_row(row):
    return {
        "dropperId": int(row["dropperId"]),
        "itemId": int(row["itemId"]),
        "minimumQuantity": int(row["minimumQuantity"]),
        "maximumQuantity": int(row["maximumQuantity"]),
        "questId": int(row["questId"]),
        "chance": int(row["chance"]),
    }


def row_tuple(row):
    return tuple(row[k] for k in ("dropperId", "itemId", "minimumQuantity", "maximumQuantity", "questId", "chance"))


def read_snapshot(path: Path):
    rows = []
    if not path.exists() or path.stat().st_size == 0:
        return rows
    with path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh, fieldnames=COLUMNS, delimiter="\t")
        for raw in reader:
            if not raw.get("dropperid"):
                continue
            rows.append(normalize_row(raw))
    return rows


def insert_sql(row):
    return (
        "INSERT INTO drop_data (dropperid,itemid,minimum_quantity,maximum_quantity,questid,chance) "
        f"VALUES ({row['dropperId']},{row['itemId']},{row['minimumQuantity']},{row['maximumQuantity']},{row['questId']},{row['chance']});"
    )


def build_report(contract, snapshot_rows):
    errors = []
    if contract.get("approved") is not False:
        errors.append("contract approved must remain false")
    if contract.get("applyAllowed") is not False:
        errors.append("contract applyAllowed must remain false")
    if contract.get("automaticApply") is not False:
        errors.append("contract automaticApply must remain false")

    desired = [contract_row(row) for row in contract.get("rows", [])]
    unresolved = {int(x) for x in contract.get("unresolvedItems", [])}
    desired_items = {row["itemId"] for row in desired}
    if unresolved & desired_items:
        errors.append("unresolved items must not appear in proposed rows")

    by_pair = defaultdict(list)
    for row in snapshot_rows:
        by_pair[(row["dropperId"], row["itemId"])].append(row)

    comparisons = []
    proposed_sql = []
    conflict_count = 0
    duplicate_count = 0
    already_present = 0
    missing = 0

    for expected in desired:
        pair = (expected["dropperId"], expected["itemId"])
        current = by_pair.get(pair, [])
        if not current:
            status = "missing"
            missing += 1
            proposed_sql.append(insert_sql(expected))
        elif len(current) > 1:
            status = "duplicate-conflict"
            duplicate_count += 1
            conflict_count += 1
        elif row_tuple(current[0]) == row_tuple(expected):
            status = "already-present"
            already_present += 1
        else:
            status = "value-conflict"
            conflict_count += 1
        comparisons.append({"expected": expected, "current": current, "status": status})

    unresolved_existing = []
    for row in snapshot_rows:
        if row["itemId"] in unresolved:
            unresolved_existing.append(row)

    if unresolved_existing:
        errors.append("production already contains unresolved Ninja Castle item rows; manual review required")
    if conflict_count:
        errors.append("one or more frozen drop pairs conflict with current production rows")

    return {
        "schemaVersion": 1,
        "kind": "read-only-drop-contract-preview",
        "contractId": contract.get("contractId"),
        "chanceScale": contract.get("chanceScale"),
        "counts": {
            "contractRows": len(desired),
            "missingRows": missing,
            "alreadyPresentRows": already_present,
            "conflictingPairs": conflict_count,
            "duplicatePairs": duplicate_count,
            "unresolvedItems": len(unresolved),
            "unresolvedRowsAlreadyInProduction": len(unresolved_existing),
        },
        "comparisons": comparisons,
        "unresolvedItems": sorted(unresolved),
        "unresolvedProductionRows": unresolved_existing,
        "proposedSql": proposed_sql,
        "applyReady": not errors and len(proposed_sql) >= 0,
        "errors": errors,
        "approved": False,
        "applyAllowed": False,
        "automaticApply": False,
        "databaseWritePerformed": False,
        "note": "Preview only. SQL text is evidence for review and is never executed by this tool or its workflow.",
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("contract", type=Path)
    p.add_argument("--snapshot", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--sql-output", type=Path, required=True)
    a = p.parse_args()

    contract = json.loads(a.contract.read_text(encoding="utf-8"))
    report = build_report(contract, read_snapshot(a.snapshot))
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    a.sql_output.write_text("\n".join(report["proposedSql"]) + ("\n" if report["proposedSql"] else ""), encoding="utf-8")
    print(json.dumps(report["counts"], sort_keys=True))
    print("approved=false / applyAllowed=false / databaseWritePerformed=false")
    return 1 if report["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())

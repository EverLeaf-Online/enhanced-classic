#!/usr/bin/env python3
"""Static integrity audit for canonical NPC shop mappings and listings.

The audit evaluates the base database seed, EverLeaf's shop-update SQL, and the
shop-integrity cleanup migration in execution order. It catches undefined
shops, empty shops, duplicate positions, duplicate item listings, invalid
price/pitch rows, and shop NPCs with no WZ asset. Zero-meso rows are valid when
`pitch` is positive.
"""
from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SQL_FILES = [
    ROOT / "database/sql/1-db_database.sql",
    ROOT / "database/sql/3-db_shopupdate.sql",
    ROOT / "database/sql/migration/everleaf_npc_shop_cleanup.sql",
]
NPC_ROOT = ROOT / "wz/Npc.wz"


def clean_columns(raw: str) -> list[str]:
    return [part.strip().strip("`") for part in raw.split(",")]


def parse_tuple(raw: str) -> list[str]:
    # Current shop seed values are scalar numerics. Keep this intentionally
    # strict so a future expression/string does not get silently misread.
    return [part.strip() for part in raw.split(",")]


def apply_sql(shops: dict[int, int], rows: list[dict[str, int]], text: str) -> None:
    for stmt in text.split(";"):
        delete = re.search(
            r"DELETE\s+FROM\s+`?shopitems`?.*?`?shopid`?\s*=\s*(\d+)",
            stmt,
            re.I | re.S,
        )
        if delete:
            shop_id = int(delete.group(1))
            rows[:] = [row for row in rows if row["shopid"] != shop_id]
            continue

        # Model targeted/idempotent shop-item position migrations so the audit
        # represents the effective canonical schema after maintained migrations.
        update_position = re.search(
            r"UPDATE\s+`?shopitems`?\s+SET\s+`?position`?\s*=\s*(\d+)\s+"
            r"WHERE\s+`?shopid`?\s*=\s*(\d+)\s+AND\s+`?itemid`?\s*=\s*(\d+)\s+"
            r"AND\s+`?position`?\s*=\s*(\d+)",
            stmt,
            re.I | re.S,
        )
        if update_position:
            new_position, shop_id, item_id, old_position = map(int, update_position.groups())
            for row in rows:
                if (
                    row["shopid"] == shop_id
                    and row["itemid"] == item_id
                    and row["position"] == old_position
                ):
                    row["position"] = new_position
            continue

        shop_insert = re.search(
            r"INSERT(?:\s+IGNORE)?\s+INTO\s+`?shops`?\s*\(([^)]*)\)\s*VALUES\s*(.*)",
            stmt,
            re.I | re.S,
        )
        if shop_insert:
            columns = clean_columns(shop_insert.group(1))
            for tuple_body in re.findall(r"\(([^()]*)\)", shop_insert.group(2)):
                values = parse_tuple(tuple_body)
                if len(values) != len(columns):
                    continue
                record = dict(zip(columns, values))
                try:
                    shops[int(record["shopid"])] = int(record["npcid"])
                except (KeyError, ValueError):
                    pass
            continue

        item_insert = re.search(
            r"INSERT(?:\s+IGNORE)?\s+INTO\s+`?shopitems`?\s*\(([^)]*)\)\s*VALUES\s*(.*)",
            stmt,
            re.I | re.S,
        )
        if item_insert:
            columns = clean_columns(item_insert.group(1))
            for tuple_body in re.findall(r"\(([^()]*)\)", item_insert.group(2)):
                values = parse_tuple(tuple_body)
                if len(values) != len(columns):
                    continue
                record = dict(zip(columns, values))
                try:
                    rows.append(
                        {
                            "shopid": int(record["shopid"]),
                            "itemid": int(record["itemid"]),
                            "price": int(record["price"]),
                            "pitch": int(record.get("pitch", "0")),
                            "position": int(record["position"]),
                        }
                    )
                except (KeyError, ValueError):
                    pass


def npc_assets() -> set[int]:
    found: set[int] = set()
    for path in NPC_ROOT.glob("*.img.xml"):
        try:
            found.add(int(path.name.split(".", 1)[0]))
        except ValueError:
            continue
    return found


def main() -> int:
    shops: dict[int, int] = {}
    rows: list[dict[str, int]] = []
    for path in SQL_FILES:
        apply_sql(shops, rows, path.read_text(encoding="utf-8", errors="ignore"))

    by_shop: dict[int, list[dict[str, int]]] = defaultdict(list)
    for row in rows:
        by_shop[row["shopid"]].append(row)

    failures: list[str] = []
    reviews: list[str] = []

    for shop_id in sorted(set(shops) - set(by_shop)):
        failures.append(f"shop {shop_id} / NPC {shops[shop_id]} has no listings")
    for shop_id in sorted(set(by_shop) - set(shops)):
        failures.append(f"shopitems reference undefined shop {shop_id}")

    assets = npc_assets()
    for shop_id, npc_id in sorted(shops.items()):
        if npc_id not in assets:
            failures.append(f"shop {shop_id} references missing NPC asset {npc_id}")

    for shop_id, listings in sorted(by_shop.items()):
        positions: dict[int, list[int]] = defaultdict(list)
        items: dict[int, list[int]] = defaultdict(list)
        for row in listings:
            positions[row["position"]].append(row["itemid"])
            items[row["itemid"]].append(row["position"])
            if row["price"] <= 0 and row["pitch"] <= 0:
                failures.append(
                    f"shop {shop_id} item {row['itemid']} has no valid meso or pitch cost"
                )
        for position, item_ids in positions.items():
            if len(item_ids) > 1:
                failures.append(
                    f"shop {shop_id} position {position} is reused by items {item_ids}"
                )
        for item_id, positions_for_item in items.items():
            if len(positions_for_item) > 1:
                reviews.append(
                    f"shop {shop_id} lists item {item_id} more than once at positions {positions_for_item}"
                )

    print(
        f"EverLeaf NPC shop audit: shops={len(shops)} listings={len(rows)} "
        f"failures={len(failures)} reviews={len(reviews)}"
    )
    for finding in failures:
        print(f"[FAIL] {finding}")
    for finding in reviews:
        print(f"[REVIEW] {finding}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Probe the disposable EverLeaf QA Docker stack.

No production paths/services are referenced. Accounts must use the qa_ prefix.
The snapshot command is read-only; restart-game only restarts the qa-game container.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
QA_DIR = ROOT / "deploy" / "qa"
ENV_FILE = QA_DIR / ".env.qa"
COMPOSE_FILE = QA_DIR / "docker-compose.qa.yml"
ACCOUNT_RE = re.compile(r"^qa_[A-Za-z0-9_]{1,24}$")


def validate_account(account: str) -> None:
    prefix = os.environ.get("EVERLEAF_QA_ACCOUNT_PREFIX", "qa_")
    if not account.startswith(prefix) or not ACCOUNT_RE.fullmatch(account):
        raise SystemExit("Refusing non-QA or malformed account name")


def compose(*args: str, capture: bool = True) -> subprocess.CompletedProcess[str]:
    if not ENV_FILE.is_file():
        raise SystemExit(f"Missing {ENV_FILE}; staging stack is not configured")
    cmd = [
        "docker", "compose", "--env-file", str(ENV_FILE),
        "-f", str(COMPOSE_FILE), "-p", "everleaf-qa", *args,
    ]
    return subprocess.run(cmd, cwd=ROOT, text=True, capture_output=capture, check=False)


def mysql_tsv(sql: str) -> list[dict[str, str]]:
    proc = compose(
        "exec", "-T", "qa-db", "sh", "-lc",
        'exec mysql -uroot -p"$MYSQL_ROOT_PASSWORD" --batch --raw cosmic -e "$1"',
        "qa-sql", sql,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or f"mysql probe failed rc={proc.returncode}")
    text = proc.stdout.strip()
    if not text:
        return []
    return list(csv.DictReader(io.StringIO(text), delimiter="\t"))


def snapshot(account: str) -> dict:
    validate_account(account)
    escaped = account.replace("'", "''")
    accounts = mysql_tsv(f"SELECT * FROM accounts WHERE name='{escaped}' LIMIT 1")
    if not accounts:
        raise RuntimeError(f"QA account {account!r} does not exist in disposable DB")
    aid = accounts[0].get("id")
    if not aid or not aid.isdigit():
        raise RuntimeError("QA account row has no numeric id")

    characters = mysql_tsv(f"SELECT * FROM characters WHERE accountid={aid} ORDER BY id")
    character_ids = [row["id"] for row in characters if row.get("id", "").isdigit()]
    cid_sql = ",".join(character_ids) if character_ids else "0"

    inventory_items = mysql_tsv(
        f"SELECT * FROM inventoryitems "
        f"WHERE accountid={aid} OR characterid IN ({cid_sql}) "
        f"ORDER BY COALESCE(characterid,0), inventorytype, position, inventoryitemid"
    )
    item_ids = [row["inventoryitemid"] for row in inventory_items if row.get("inventoryitemid", "").isdigit()]
    iid_sql = ",".join(item_ids) if item_ids else "0"

    equipment = mysql_tsv(
        f"SELECT * FROM inventoryequipment "
        f"WHERE inventoryitemid IN ({iid_sql}) "
        f"ORDER BY inventoryitemid, inventoryequipmentid"
    )
    quest_status = mysql_tsv(
        f"SELECT * FROM queststatus "
        f"WHERE characterid IN ({cid_sql}) "
        f"ORDER BY characterid, quest, queststatusid"
    )
    quest_status_ids = [row["queststatusid"] for row in quest_status if row.get("queststatusid", "").isdigit()]
    qsid_sql = ",".join(quest_status_ids) if quest_status_ids else "0"
    quest_progress = mysql_tsv(
        f"SELECT * FROM questprogress "
        f"WHERE characterid IN ({cid_sql}) OR queststatusid IN ({qsid_sql}) "
        f"ORDER BY characterid, queststatusid, progressid, id"
    )
    storages = mysql_tsv(f"SELECT * FROM storages WHERE accountid={aid} ORDER BY world, storageid")
    storage_inventory = mysql_tsv(
        f"SELECT * FROM inventoryitems "
        f"WHERE accountid={aid} AND characterid IS NULL "
        f"ORDER BY inventorytype, position, inventoryitemid"
    )

    # Exclude credentials and volatile login/session state from persistence
    # equality while retaining durable gameplay/account state.
    account_row = dict(accounts[0])
    for key in (
        "password", "pin", "pic", "loggedin", "lastlogin", "lastip",
        "lastknownip", "sessionip", "tempban", "macs", "hwid", "ip",
    ):
        account_row.pop(key, None)

    # These character timestamps are expected to move during legitimate logout,
    # reconnect, or forced shutdown boundaries. They are not durable gameplay state.
    normalized_characters = []
    for row in characters:
        clean = dict(row)
        for key in ("lastLogoutTime", "lastExpGainTime"):
            clean.pop(key, None)
        normalized_characters.append(clean)

    return {
        "account": account_row,
        "characters": normalized_characters,
        "inventory_items": inventory_items,
        "equipment": equipment,
        "quest_status": quest_status,
        "quest_progress": quest_progress,
        "storages": storages,
        "storage_inventory": storage_inventory,
    }


def restart_game() -> None:
    proc = compose("restart", "qa-game")
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or f"qa-game restart failed rc={proc.returncode}")


def status() -> dict:
    proc = compose("ps", "--format", "json")
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or f"compose ps failed rc={proc.returncode}")
    lines = [line for line in proc.stdout.splitlines() if line.strip()]
    rows = []
    for line in lines:
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    return {"project": "everleaf-qa", "services": rows}


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("snapshot")
    p.add_argument("--account", required=True)
    sub.add_parser("restart-game")
    sub.add_parser("status")
    args = ap.parse_args()

    try:
        if args.cmd == "snapshot":
            print(json.dumps(snapshot(args.account), sort_keys=True))
        elif args.cmd == "restart-game":
            restart_game()
        else:
            print(json.dumps(status(), sort_keys=True))
        return 0
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

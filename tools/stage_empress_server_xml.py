#!/usr/bin/env python3
"""Stage only the approved EverLeaf Empress/Gate-to-the-Future server XML.

Usage:
    python3 tools/stage_empress_server_xml.py /path/to/wz.zip

The source archive is never modified. Files are copied into the repository's
existing wz/ tree. This script intentionally does NOT stage client .IMG/WZ
assets and does NOT enable Empress content.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]

MAP_IDS = [
    271000000, 271000100, 271000200, 271000210, 271000300,
    271010000, 271010001, 271010100, 271010200, 271010300, 271010301,
    271010400, 271010500, 271020000, 271020100, 271030000, 271030010,
    271030100, 271030101, 271030102, 271030200, 271030201, 271030202,
    271030203, 271030204, 271030205, 271030300, 271030310, 271030320,
    271030400, 271030410, 271030500, 271030510, 271030520, 271030530,
    271030540, 271030600, 271040000, 271040100, 271040200, 271040210,
    271040300,
]

MOB_IDS = [
    *range(8600000, 8600007),
    *range(8610000, 8610015),
    *range(8850000, 8850012),
]

# Direct map references discovered from the selected 2710xxxx package.
NPC_IDS = [
    2142000, 2142001, 2142002, 2142003, 2142004, 2142005, 2142006,
    2142007, 2142008, 2142009, 2142010, 2143000, 2143001, 2143003,
    2143004,
]


def approved_members() -> dict[str, Path]:
    out: dict[str, Path] = {}
    for map_id in MAP_IDS:
        src = f"wz/Map.wz/Map/Map2/{map_id}.img.xml"
        out[src] = ROOT / "wz" / "Map.wz" / "Map" / "Map2" / f"{map_id}.img.xml"
    for mob_id in MOB_IDS:
        src = f"wz/Mob.wz/{mob_id}.img.xml"
        out[src] = ROOT / "wz" / "Mob.wz" / f"{mob_id}.img.xml"
    for npc_id in NPC_IDS:
        src = f"wz/Npc.wz/{npc_id}.img.xml"
        out[src] = ROOT / "wz" / "Npc.wz" / f"{npc_id}.img.xml"
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("archive", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    archive = args.archive.expanduser().resolve()
    if not archive.is_file():
        raise SystemExit(f"Archive not found: {archive}")

    approved = approved_members()
    with zipfile.ZipFile(archive) as zf:
        names = set(zf.namelist())
        missing = [name for name in approved if name not in names]
        if missing:
            print("Missing required source members:")
            for name in missing:
                print(f"  - {name}")
            return 2

        print(f"Approved server XML files: {len(approved)}")
        print(f"  maps: {len(MAP_IDS)}")
        print(f"  mobs: {len(MOB_IDS)}")
        print(f"  NPCs: {len(NPC_IDS)}")

        if args.dry_run:
            for src, dst in approved.items():
                state = "replace" if dst.exists() else "add"
                print(f"[{state}] {src} -> {dst.relative_to(ROOT)}")
            return 0

        with tempfile.TemporaryDirectory(prefix="everleaf-empress-") as td:
            temp_root = Path(td)
            for src, dst in approved.items():
                extracted = Path(zf.extract(src, temp_root))
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(extracted, dst)

    print("Empress server XML staged. Content remains disabled until client assets and scripts are validated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Patch the v83 StringPool hook with the one known Evan action alias mismatch.

The authorized Evan backport source expects `recoveryAura`, while the original
v83 client StringPool uses `dragonAura` for that action slot. We normalize the
returned string by value instead of hardcoding a StringPool numeric index so
the patch remains independent of old community address/index tables.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TARGET = ROOT / "client/ezorsia/ezorsia/ReplacementFuncs.h"

OLD = '''\tauto ret = _sub_79E993(pThis, nullptr, result, nIdx, formal);//_StringPool__GetString_t\n\tEverLeafPinStringPoolEntry(pThis, nIdx);\n\tswitch (nIdx)\n'''
NEW = '''\tauto ret = _sub_79E993(pThis, nullptr, result, nIdx, formal);//_StringPool__GetString_t\n\tEverLeafPinStringPoolEntry(pThis, nIdx);\n\t// Evan v83 backport compatibility: the source Skill.wz uses recoveryAura,\n\t// while the original v83 StringPool exposes dragonAura for this action.\n\t// Match by returned value rather than a fragile StringPool numeric index.\n\tif (ret && ret->Compare("dragonAura"))\n\t{\n\t\t*ret = ("recoveryAura");\n\t}\n\tswitch (nIdx)\n'''


def main() -> int:
    text = TARGET.read_text(encoding="utf-8")
    if NEW in text:
        print("OK already fixed: Evan dragonAura -> recoveryAura StringPool alias")
    elif OLD in text:
        text = text.replace(OLD, NEW, 1)
        TARGET.write_text(text, encoding="utf-8")
        print("FIXED: Evan dragonAura -> recoveryAura StringPool alias")
    else:
        raise SystemExit("ERROR expected EverLeaf StringPool hook insertion point not found")

    final = TARGET.read_text(encoding="utf-8")
    required = (
        'if (ret && ret->Compare("dragonAura"))',
        '*ret = ("recoveryAura");',
        'Match by returned value rather than a fragile StringPool numeric index.',
    )
    for marker in required:
        if marker not in final:
            raise SystemExit(f"ERROR missing Evan action alias invariant: {marker}")

    if final.count('ret->Compare("dragonAura")') != 1:
        raise SystemExit("ERROR Evan action alias transform is duplicated")

    print("EverLeaf Evan action alias transform: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

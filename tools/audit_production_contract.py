#!/usr/bin/env python3
from pathlib import Path
import re
config=Path("config.yaml").read_text(encoding="utf-8-sig")
worlds=config.split("worlds:",1)[1].split("\nserver:",1)[0]
first=worlds.split("\n  - flag:",2)[1]
required={"channels":"20","exp_rate":"5","meso_rate":"3","drop_rate":"2","boss_drop_rate":"2","quest_rate":"1","fishing_rate":"2","travel_rate":"2"}
for key,value in required.items():
    if not re.search(rf"(?m)^\s*{key}:\s*{re.escape(value)}\s*(?:#.*)?$", first):
        raise SystemExit(f"production contract mismatch: {key} != {value}")
for pattern,label in ((r"(?m)^\s*HOST:\s*132\.145\.141\.79\s*(?:#.*)?$","HOST"),(r"(?m)^\s*AUTOMATIC_REGISTER:\s*false\s*(?:#.*)?$","automatic registration"),(r"(?m)^\s*USE_SUPPLY_RATE_COUPONS:\s*false\s*(?:#.*)?$","rate coupons")):
    if not re.search(pattern,config): raise SystemExit(f"production contract mismatch: {label}")
if "7575-7594:7575-7594" not in Path("docker-compose.yml").read_text(): raise SystemExit("production contract mismatch: Docker channel exposure")
contract=Path("docs/PRODUCTION_CONTRACT.md").read_text()
for marker in ("20 channels","5x","3x","2x","1x","132.145.141.79"):
    if marker not in contract: raise SystemExit(f"production contract document missing {marker}")
print("EverLeaf production contract: PASS")

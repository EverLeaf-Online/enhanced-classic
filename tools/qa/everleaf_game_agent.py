#!/usr/bin/env python3
"""Database-observed EverLeaf gameplay QA agent.

Run this on the Windows machine that has the EverLeaf client open and the QA SSH
tunnel active. The agent drives the local QA client through
windows_client_bridge.py, queries the disposable server through SSH, and judges
progress from database snapshots rather than trusting screen coordinates.

This first gameplay driver deliberately focuses on robust smoke behaviours:
- clear modal/tutorial UI
- move/jump through maps and portals
- probe NPC interaction and quest acceptance
- attack/loot and verify progression/inventory changes
- record every before/after snapshot and action in a reproducible JSON report

It never targets production. The bridge itself refuses to operate unless
127.0.0.1:8484 is listening, and remote snapshots still require a qa_ account.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[2]
BRIDGE = ROOT / "tools" / "qa" / "windows_client_bridge.py"
REMOTE_ROOT = "/opt/everleaf/qa-agent-hub"


@dataclass
class StepResult:
    name: str
    status: str
    message: str
    evidence: dict[str, Any] | None = None


def run(cmd: list[str], timeout: int = 60) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, text=True, capture_output=True, timeout=timeout, shell=False)


def bridge(*args: str, timeout: int = 30) -> dict[str, Any]:
    proc = run([sys.executable, str(BRIDGE), *args], timeout=timeout)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or f"bridge failed rc={proc.returncode}")
    text = proc.stdout.strip()
    return json.loads(text) if text else {}


def remote_snapshot(ssh_host: str, ssh_key: str, account: str) -> dict[str, Any]:
    remote = (
        f"cd {REMOTE_ROOT} && sudo python3 tools/qa/staging_probe.py "
        f"snapshot --account {account}"
    )
    proc = run(["ssh", "-i", ssh_key, "-o", "BatchMode=yes", ssh_host, remote], timeout=60)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or f"remote snapshot failed rc={proc.returncode}")
    data = json.loads(proc.stdout)
    if not isinstance(data, dict):
        raise RuntimeError("remote snapshot did not return an object")
    return data


def char(snapshot: dict[str, Any]) -> dict[str, str]:
    rows = snapshot.get("characters") or []
    if not rows:
        raise RuntimeError("QA account has no character")
    return rows[0]


def metrics(snapshot: dict[str, Any]) -> dict[str, Any]:
    c = char(snapshot)
    return {
        "map": int(c.get("map", 0)),
        "level": int(c.get("level", 0)),
        "exp": int(c.get("exp", 0)),
        "meso": int(c.get("meso", 0)),
        "hp": int(c.get("hp", 0)),
        "mp": int(c.get("mp", 0)),
        "inventory_count": len(snapshot.get("inventory_items") or []),
        "quest_count": len(snapshot.get("quest_status") or []),
        "quest_progress_count": len(snapshot.get("quest_progress") or []),
    }


def changed(before: dict[str, Any], after: dict[str, Any], keys: list[str]) -> dict[str, dict[str, Any]]:
    b = metrics(before)
    a = metrics(after)
    return {k: {"before": b[k], "after": a[k]} for k in keys if b[k] != a[k]}


def tap(key: str, count: int = 1, interval: float = 0.08) -> None:
    bridge("tap", key, "--count", str(count), "--interval", str(interval))


def hold(key: str, seconds: float) -> None:
    bridge("hold", key, str(seconds), timeout=max(30, int(seconds) + 10))


def settle(seconds: float = 0.8) -> None:
    time.sleep(seconds)


def smoke_ui() -> StepResult:
    # Escape/enter are safe modal-clearing inputs. Neither mutates durable state by itself.
    tap("esc", 2)
    tap("enter", 1)
    settle(0.4)
    return StepResult("clear-ui", "PASS", "Sent conservative modal-clearing input sequence.")


def traversal_probe(get_snapshot: Callable[[], dict[str, Any]]) -> StepResult:
    before = get_snapshot()
    start = metrics(before)
    # Simple Maple Island traversal policy: move right, jump periodically, try up at portals.
    for _ in range(4):
        hold("right", 1.25)
        tap("alt", 2, 0.12)
        hold("right", 0.7)
        tap("up", 2, 0.12)
        settle(0.35)
        now = get_snapshot()
        if metrics(now)["map"] != start["map"]:
            delta = changed(before, now, ["map", "exp", "meso", "inventory_count", "quest_count"])
            return StepResult("traversal", "PASS", "Agent crossed a map boundary.", delta)
    after = get_snapshot()
    return StepResult(
        "traversal",
        "REVIEW",
        "No map transition observed after bounded movement/portal probe.",
        {"start": start, "end": metrics(after)},
    )


def npc_quest_probe(get_snapshot: Callable[[], dict[str, Any]]) -> StepResult:
    before = get_snapshot()
    start = metrics(before)
    # Sweep a bounded area and try the standard NPC interaction key. Dialog advance is Enter.
    for _ in range(6):
        tap("z", 1)
        tap("enter", 4, 0.16)
        settle(0.35)
        now = get_snapshot()
        if metrics(now)["quest_count"] > start["quest_count"]:
            delta = changed(before, now, ["quest_count", "quest_progress_count", "inventory_count", "exp", "meso"])
            return StepResult("npc-quest", "PASS", "Quest state increased after autonomous NPC interaction.", delta)
        hold("right", 0.6)
    after = get_snapshot()
    return StepResult(
        "npc-quest",
        "REVIEW",
        "No new quest row observed during bounded NPC interaction sweep.",
        {"start": start, "end": metrics(after)},
    )


def combat_loot_probe(get_snapshot: Callable[[], dict[str, Any]]) -> StepResult:
    before = get_snapshot()
    start = metrics(before)
    # Beginner-safe combat loop: short lateral movement, attack, then loot.
    for _ in range(12):
        tap("ctrl", 3, 0.12)
        tap("z", 2, 0.10)
        hold("right", 0.35)
        if _ % 3 == 0:
            tap("alt", 1)
        settle(0.15)
        if _ % 3 == 2:
            now = get_snapshot()
            nm = metrics(now)
            if nm["exp"] > start["exp"] or nm["meso"] > start["meso"] or nm["inventory_count"] > start["inventory_count"]:
                delta = changed(before, now, ["level", "exp", "meso", "inventory_count", "hp", "mp"])
                return StepResult("combat-loot", "PASS", "Combat/loot progression detected in database state.", delta)
    after = get_snapshot()
    return StepResult(
        "combat-loot",
        "REVIEW",
        "No EXP/meso/inventory gain detected during bounded combat sweep.",
        {"start": start, "end": metrics(after)},
    )


def run_smoke(ssh_host: str, ssh_key: str, account: str) -> dict[str, Any]:
    def snap() -> dict[str, Any]:
        return remote_snapshot(ssh_host, ssh_key, account)

    bridge_status = bridge("status")
    if not bridge_status.get("qa_tunnel"):
        raise RuntimeError("Local QA tunnel is not active")
    if not bridge_status.get("window_found"):
        raise RuntimeError("EverLeaf client window is not open")

    baseline = snap()
    results: list[StepResult] = [
        StepResult("safety", "PASS", "QA tunnel and EverLeaf window verified.", bridge_status),
        StepResult("baseline", "PASS", "Captured disposable QA database baseline.", metrics(baseline)),
    ]

    for fn in (smoke_ui,):
        results.append(fn())
    for fn in (npc_quest_probe, traversal_probe, combat_loot_probe):
        try:
            results.append(fn(snap))
        except Exception as exc:
            results.append(StepResult(fn.__name__.replace("_probe", ""), "FAIL", str(exc)))

    final = snap()
    summary = {s: sum(r.status == s for r in results) for s in ("PASS", "REVIEW", "FAIL")}
    return {
        "schema_version": 1,
        "account": account,
        "mode": "autonomous-smoke",
        "summary": summary,
        "baseline": metrics(baseline),
        "final": metrics(final),
        "results": [asdict(r) for r in results],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="EverLeaf autonomous gameplay QA agent")
    ap.add_argument("--ssh-host", required=True, help="e.g. ubuntu@132.145.141.79")
    ap.add_argument("--ssh-key", required=True)
    ap.add_argument("--account", default="qa_runner")
    ap.add_argument("--json", default="build/game-agent-report.json")
    args = ap.parse_args()

    if not args.account.startswith("qa_"):
        print("Refusing non-QA account", file=sys.stderr)
        return 2
    key = Path(args.ssh_key)
    if not key.is_file():
        print(f"SSH key not found: {key}", file=sys.stderr)
        return 2

    try:
        report = run_smoke(args.ssh_host, str(key), args.account)
        out = Path(args.json)
        if not out.is_absolute():
            out = ROOT / out
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(report["summary"], sort_keys=True))
        print(str(out))
        return 1 if report["summary"]["FAIL"] else 0
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""EverLeaf staging-only runtime QA harness.

This harness is intentionally environment-agnostic: operators provide JSON
commands/adapters for snapshots and actions. Runtime actions are refused unless
all safety gates pass. It is suitable for QA-only accounts on staging or a
disposable clone, not production.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

ARM_TOKEN = "I_UNDERSTAND_STAGING_ONLY"
DEFAULT_QA_PREFIX = "qa_"
ALLOWED_ENVS = {"staging", "disposable", "local-qa"}


@dataclass
class Result:
    check: str
    status: str
    message: str
    evidence: dict[str, Any] | None = None


def load_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path: str | Path, data: Any) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def safety_gate(environment: str, account: str, allow_actions: bool) -> list[Result]:
    out: list[Result] = []
    prefix = os.environ.get("EVERLEAF_QA_ACCOUNT_PREFIX", DEFAULT_QA_PREFIX)
    if environment not in ALLOWED_ENVS:
        out.append(Result("environment", "FAIL", f"Runtime QA refuses environment={environment!r}; allowed={sorted(ALLOWED_ENVS)}"))
    else:
        out.append(Result("environment", "PASS", f"Authorized QA environment: {environment}"))
    if not account.startswith(prefix):
        out.append(Result("qa-account", "FAIL", f"Account {account!r} does not start with required QA prefix {prefix!r}."))
    else:
        out.append(Result("qa-account", "PASS", f"QA-only account prefix verified: {account}"))
    if allow_actions:
        if os.environ.get("EVERLEAF_QA_RUNTIME") != ARM_TOKEN:
            out.append(Result("runtime-arm", "FAIL", "Runtime actions requested without explicit EVERLEAF_QA_RUNTIME arming token."))
        else:
            out.append(Result("runtime-arm", "PASS", "Staging runtime action gate armed."))
    else:
        out.append(Result("runtime-arm", "PASS", "Dry-run/read-only mode; no actions will execute."))
    return out


def command_from(value: Any) -> list[str]:
    if not isinstance(value, list) or not value or not all(isinstance(x, str) and x for x in value):
        raise ValueError("adapter command must be a non-empty JSON array of strings")
    return value


def run_command(cmd: list[str], timeout: int = 60) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, text=True, capture_output=True, timeout=timeout, check=False, shell=False)


def snapshot(adapter: dict[str, Any], account: str) -> dict[str, Any]:
    cmd = [part.replace("{account}", account) for part in command_from(adapter["snapshot_command"])]
    proc = run_command(cmd, int(adapter.get("snapshot_timeout", 60)))
    if proc.returncode != 0:
        raise RuntimeError(f"snapshot command failed rc={proc.returncode}: {proc.stderr.strip()}")
    data = json.loads(proc.stdout)
    if not isinstance(data, dict):
        raise ValueError("snapshot command must emit one JSON object")
    return data


def action(adapter: dict[str, Any], name: str, account: str) -> None:
    actions = adapter.get("actions", {})
    if name not in actions:
        raise KeyError(f"adapter has no action named {name!r}")
    cmd = [part.replace("{account}", account) for part in command_from(actions[name])]
    proc = run_command(cmd, int(adapter.get("action_timeout", 120)))
    if proc.returncode != 0:
        raise RuntimeError(f"action {name!r} failed rc={proc.returncode}: {proc.stderr.strip()}")


def flatten_numbers(value: Any, prefix: str = "") -> dict[str, float]:
    out: dict[str, float] = {}
    if isinstance(value, bool):
        return out
    if isinstance(value, (int, float)):
        out[prefix or "$root"] = float(value)
    elif isinstance(value, dict):
        for k, v in value.items():
            key = f"{prefix}.{k}" if prefix else str(k)
            out.update(flatten_numbers(v, key))
    return out


def compare_snapshots(before: dict[str, Any], after: dict[str, Any], mode: str, conserved: list[str] | None = None) -> list[Result]:
    results: list[Result] = []
    if mode == "persistence":
        if before == after:
            results.append(Result("persistence-equality", "PASS", "Snapshot is identical before/after persistence boundary."))
        else:
            keys = sorted(set(before) | set(after))
            changed = [k for k in keys if before.get(k) != after.get(k)]
            results.append(Result("persistence-equality", "FAIL", f"Persistence snapshot changed in {len(changed)} top-level fields.", {"changed": changed}))
        return results

    bnums = flatten_numbers(before)
    anums = flatten_numbers(after)
    fields = conserved or sorted(set(bnums) & set(anums))
    mismatches = {}
    for field in fields:
        b = bnums.get(field)
        a = anums.get(field)
        if b is None or a is None:
            mismatches[field] = {"before": b, "after": a, "reason": "missing"}
        elif a != b:
            mismatches[field] = {"before": b, "after": a, "delta": a - b}
    if mismatches:
        results.append(Result("asset-conservation", "FAIL", f"{len(mismatches)} conserved numeric fields changed unexpectedly.", mismatches))
    else:
        results.append(Result("asset-conservation", "PASS", f"All {len(fields)} conserved numeric fields remained constant."))
    return results


def make_report(results: list[Result], environment: str, account: str, scenario: str) -> dict[str, Any]:
    summary = {s: sum(r.status == s for r in results) for s in ("PASS", "REVIEW", "FAIL")}
    return {
        "schema_version": 1,
        "environment": environment,
        "account": account,
        "scenario": scenario,
        "summary": summary,
        "results": [asdict(r) for r in results],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="EverLeaf staging-only runtime QA")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_compare = sub.add_parser("compare", help="compare two already-captured snapshots")
    p_compare.add_argument("--before", required=True)
    p_compare.add_argument("--after", required=True)
    p_compare.add_argument("--mode", choices=("persistence", "conservation"), required=True)
    p_compare.add_argument("--conserved", nargs="*")
    p_compare.add_argument("--json")

    p_run = sub.add_parser("run", help="run a guarded staging scenario")
    p_run.add_argument("--environment", required=True)
    p_run.add_argument("--account", required=True)
    p_run.add_argument("--adapter", required=True)
    p_run.add_argument("--scenario", required=True, help="action name in adapter")
    p_run.add_argument("--mode", choices=("persistence", "conservation"), required=True)
    p_run.add_argument("--conserved", nargs="*")
    p_run.add_argument("--allow-actions", action="store_true")
    p_run.add_argument("--json", required=True)

    args = ap.parse_args()

    if args.cmd == "compare":
        results = compare_snapshots(load_json(args.before), load_json(args.after), args.mode, args.conserved)
        report = make_report(results, "offline", "offline", "compare")
        if args.json:
            write_json(args.json, report)
        print(json.dumps(report["summary"], sort_keys=True))
        return 1 if report["summary"]["FAIL"] else 0

    results = safety_gate(args.environment, args.account, args.allow_actions)
    if any(r.status == "FAIL" for r in results):
        report = make_report(results, args.environment, args.account, args.scenario)
        write_json(args.json, report)
        print(json.dumps(report["summary"], sort_keys=True))
        return 2

    adapter = load_json(args.adapter)
    if not args.allow_actions:
        results.append(Result("scenario", "REVIEW", f"Dry-run validated scenario {args.scenario!r}; no snapshot/action command executed."))
    else:
        try:
            before = snapshot(adapter, args.account)
            action(adapter, args.scenario, args.account)
            after = snapshot(adapter, args.account)
            results.extend(compare_snapshots(before, after, args.mode, args.conserved))
        except Exception as exc:
            results.append(Result("scenario-execution", "FAIL", str(exc)))

    report = make_report(results, args.environment, args.account, args.scenario)
    write_json(args.json, report)
    print(json.dumps(report["summary"], sort_keys=True))
    return 1 if report["summary"]["FAIL"] else 0


if __name__ == "__main__":
    raise SystemExit(main())

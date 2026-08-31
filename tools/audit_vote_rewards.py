#!/usr/bin/env python3
"""Fail CI if EverLeaf's verified vote flow drifts from queued NX rewards.

The web callback must use a secret, reward only successful provider callbacks,
and enqueue an idempotent account/provider/day reward for the game to claim.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
MIGRATION = ROOT / "database/sql/migration/everleaf_nx_rewards.sql"
WEB_ROUTE = ROOT / "web/src/routes/vote.js"
WEB_SERVICE = ROOT / "web/src/services/gameService.js"
WEB_ENV = ROOT / "web/src/config/env.js"
VOTE_COMMAND = ROOT / "src/main/java/client/command/commands/gm0/VoteCommand.java"
BUILD_TRANSFORM = ROOT / "tools/apply_level_cap_250.py"


def fail(message: str) -> None:
    raise SystemExit(f"[FAIL] {message}")


def read(path: Path) -> str:
    if not path.is_file():
        fail(f"Missing vote integration file: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8")


def main() -> None:
    migration = read(MIGRATION)
    route = read(WEB_ROUTE)
    service = read(WEB_SERVICE)
    env = read(WEB_ENV)
    command = read(VOTE_COMMAND)
    transform = read(BUILD_TRANSFORM)

    required_migration = [
        "everleaf_vote_rewards",
        "account_id",
        "provider",
        "external_vote_id",
        "nx_amount",
        "UNIQUE KEY uq_everleaf_vote_provider_external",
        "FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE",
    ]
    for marker in required_migration:
        if marker not in migration:
            fail(f"Vote reward migration lost required invariant: {marker}")

    route_markers = [
        "GTOP100_PINGBACK_KEY",
        "secretEqual(parsed.key, env.vote.gtopPingbackKey)",
        "vote.success !== 0",
        "game.queueVerifiedVoteNx({",
        'provider: env.vote.provider',
        'nxReward: true',
    ]
    for marker in route_markers:
        if marker not in route:
            fail(f"Vote pingback route lost required guard: {marker}")

    service_markers = [
        "beginTransaction()",
        "FOR UPDATE",
        "INSERT IGNORE INTO everleaf_vote_rewards",
        "affectedRows !== 1",
        "const externalVoteId = `${provider}:${account.id}:${voteDate}`;",
        "nx_amount",
        "await con.commit()",
    ]
    for marker in service_markers:
        if marker not in service:
            fail(f"Verified vote reward transaction lost invariant: {marker}")

    forbidden = {
        "web vote route": (route, ["rewardPoints", "nxReward: false"]),
        "vote command": (command, ["Vote Points only", "@points vp"]),
    }
    for label, (text, markers) in forbidden.items():
        for marker in markers:
            if marker.lower() in text.lower():
                fail(f"{label} contains forbidden NX-vote marker: {marker}")

    if 'rewardNx: Math.max(1, Math.min(100000, Number(process.env.VOTE_NX_REWARD || 1500)))' not in env:
        fail("Default verified vote reward must remain 1,500 NX and bounded")

    web_match = re.search(r'gtop100\.com/MapleStory/server-(\d+)\?vote=1', env)
    java_match = re.search(r'gtop100\.com/MapleStory/server-(\d+)\?vote=1', command)
    if not web_match or not java_match:
        fail("Could not verify matching GTop100 listing IDs in web and in-game vote links")
    if web_match.group(1) != java_match.group(1):
        fail(f"GTop100 listing ID drift: web={web_match.group(1)} java={java_match.group(1)}")

    if 'addCommand("vote", VoteCommand.class);' not in transform:
        fail("@vote is not registered by the EverLeaf build transform")
    if 'VoteShopCommand.class' not in transform:
        fail("@voteshop is not registered by the EverLeaf build transform")

    print("[PASS] Verified NX reward policy audit")
    print(f"       GTop100 listing id={web_match.group(1)} (configuration still requires pre-production dashboard verification)")
    print("       reward=1,500 pending NX default; no direct balance mutation")
    print("       duplicate window=account/provider/UTC day")
    print("       callback=secret-gated + provider-success-only + transactional")


if __name__ == "__main__":
    main()

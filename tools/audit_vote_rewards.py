#!/usr/bin/env python3
"""Fail CI if EverLeaf's verified vote flow drifts into P2W/NX rewards.

Voting is account-level convenience currency only. The web callback must use a
secret, reward only successful provider callbacks, and rely on the idempotent
account/provider/day ledger before mutating Vote Points.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
MIGRATION = ROOT / "database/sql/migration/everleaf_vote_rewards.sql"
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
        "everleaf_vote_reward_ledger",
        "account_id",
        "provider",
        "vote_date_utc",
        "UNIQUE KEY `uq_everleaf_vote_reward_window`",
        "FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`) ON DELETE CASCADE",
    ]
    for marker in required_migration:
        if marker not in migration:
            fail(f"Vote reward migration lost required invariant: {marker}")

    route_markers = [
        "GTOP100_PINGBACK_KEY",
        "secretEqual(parsed.key, env.vote.gtopPingbackKey)",
        "vote.success !== 0",
        "game.rewardVerifiedVote({",
        'provider: env.vote.provider',
        'nxReward: false',
    ]
    for marker in route_markers:
        if marker not in route:
            fail(f"Vote pingback route lost required guard: {marker}")

    service_markers = [
        "beginTransaction()",
        "FOR UPDATE",
        "INSERT IGNORE INTO everleaf_vote_reward_ledger",
        "affectedRows !== 1",
        "accountVotePoints",
        "await con.commit()",
    ]
    for marker in service_markers:
        if marker not in service:
            fail(f"Verified vote reward transaction lost invariant: {marker}")

    forbidden = {
        "web vote route": (route, ["nxCredit", "VOTE_NX_REWARD", "NxRewardService"]),
        "web vote service": (service, ["nxCredit", "VOTE_NX_REWARD", "NxRewardService"]),
        "vote command": (command, ["earn 1,500 NX", "earn NX", "@points nx"]),
    }
    for label, (text, markers) in forbidden.items():
        for marker in markers:
            if marker.lower() in text.lower():
                fail(f"{label} contains forbidden NX-vote marker: {marker}")

    if 'rewardPoints: Math.max(1, Math.min(10, Number(process.env.VOTE_POINTS_REWARD || 1)))' not in env:
        fail("Default verified vote reward must remain 1 Vote Point and bounded")

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

    print("[PASS] Verified Vote Point reward policy audit")
    print(f"       GTop100 listing id={web_match.group(1)} (configuration still requires pre-production dashboard verification)")
    print("       reward=1 VP default; no vote NX")
    print("       duplicate window=account/provider/UTC day")
    print("       callback=secret-gated + provider-success-only + transactional")


if __name__ == "__main__":
    main()

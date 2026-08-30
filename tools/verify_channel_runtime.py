#!/usr/bin/env python3
"""Verify that the running EverLeaf server matches the configured channel count.

This is intentionally dependency-free so it can run on a clean deployment host.
It reads the primary world's `channels` value from config.yaml, checks the login
port plus the corresponding channel ports, prints a small JSON report, and exits
non-zero when the runtime does not match configuration.
"""

from __future__ import annotations

import argparse
import json
import re
import socket
from pathlib import Path


def configured_channels(config_path: Path) -> int:
    text = config_path.read_text(encoding="utf-8-sig")
    worlds_match = re.search(r"(?m)^worlds:\s*$", text)
    if not worlds_match:
        raise ValueError("config.yaml does not contain a worlds section")

    server_match = re.search(r"(?m)^server:\s*$", text[worlds_match.end():])
    section_end = worlds_match.end() + (server_match.start() if server_match else len(text))
    worlds_section = text[worlds_match.end():section_end]

    channel_match = re.search(r"(?m)^\s+channels:\s*(\d+)\s*(?:#.*)?$", worlds_section)
    if not channel_match:
        raise ValueError("primary world channel count was not found in config.yaml")

    count = int(channel_match.group(1))
    if count < 1:
        raise ValueError(f"invalid configured channel count: {count}")
    return count


def port_open(host: str, port: int, timeout: float) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="config.yaml", help="Path to EverLeaf config.yaml")
    parser.add_argument("--host", default="127.0.0.1", help="Server host to probe")
    parser.add_argument("--login-port", type=int, default=8484)
    parser.add_argument("--channel-base-port", type=int, default=7575)
    parser.add_argument("--timeout", type=float, default=0.75)
    args = parser.parse_args()

    expected = configured_channels(Path(args.config))
    channel_ports = [args.channel_base_port + i for i in range(expected)]
    channel_states = {str(port): port_open(args.host, port, args.timeout) for port in channel_ports}
    live_ports = [int(port) for port, is_open in channel_states.items() if is_open]
    missing_ports = [int(port) for port, is_open in channel_states.items() if not is_open]
    login_online = port_open(args.host, args.login_port, args.timeout)

    healthy = login_online and len(live_ports) == expected
    report = {
        "healthy": healthy,
        "host": args.host,
        "login": {"port": args.login_port, "online": login_online},
        "configuredChannels": expected,
        "liveChannels": len(live_ports),
        "channelPorts": channel_ports,
        "liveChannelPorts": live_ports,
        "missingChannelPorts": missing_ports,
    }
    print(json.dumps(report, indent=2, sort_keys=True))

    if not login_online:
        print("ERROR: EverLeaf login server is not reachable.")
        return 2
    if missing_ports:
        print(
            "ERROR: EverLeaf runtime channel count does not match config.yaml; "
            f"expected {expected}, found {len(live_ports)}."
        )
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

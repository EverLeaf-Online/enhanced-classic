#!/usr/bin/env python3
"""Run the EverLeaf local v83 character renderer on loopback only.

The renderer implementation is supplied by the pinned MIT-licensed
Leonana69/wz-python checkout installed by deploy-web.yml.  We deliberately
run Flask single-threaded because the legacy WZ reader owns shared file/cipher
state; serial rendering is safer than letting simultaneous ranking requests
seek through Character.wz concurrently.
"""

from __future__ import annotations

import os
import sys

WZPY_ROOT = os.environ.get("EVERLEAF_WZPY_ROOT", "/opt/everleaf/wz-python")
CHARACTER_WZ = os.environ.get(
    "EVERLEAF_CHARACTER_WZ",
    "/opt/everleaf/patches/files/Character.wz",
)
HOST = os.environ.get("EVERLEAF_WZ_AVATAR_HOST", "127.0.0.1")
PORT = int(os.environ.get("EVERLEAF_WZ_AVATAR_PORT", "3011"))

sys.path.insert(0, WZPY_ROOT)

from server.app import create_app  # noqa: E402


def main() -> None:
    if not os.path.isfile(CHARACTER_WZ) or os.path.getsize(CHARACTER_WZ) <= 0:
        raise SystemExit(f"Character.wz is missing or empty: {CHARACTER_WZ}")

    app = create_app(CHARACTER_WZ, region="GMS", version=83)
    app.run(host=HOST, port=PORT, debug=False, threaded=False, use_reloader=False)


if __name__ == "__main__":
    main()

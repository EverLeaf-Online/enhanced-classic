#!/usr/bin/env python3
"""Serve EverLeaf character portraits from the production v83 Character.wz.

This is intentionally a tiny loopback-only Flask sidecar instead of the full
wz-python editor application.  The production Character.wz is opened with
``writable=False`` and systemd mounts it read-only, so a rankings request can
never mutate the client archive.  Flask is also single-threaded because the
legacy WZ reader owns shared file/cipher state.
"""

from __future__ import annotations

import io
import os
import re
import sys

WZPY_ROOT = os.environ.get("EVERLEAF_WZPY_ROOT", "/opt/everleaf/wz-python")
CHARACTER_WZ = os.environ.get(
    "EVERLEAF_CHARACTER_WZ",
    "/opt/everleaf/patches/files/Character.wz",
)
HOST = os.environ.get("EVERLEAF_WZ_AVATAR_HOST", "127.0.0.1")
PORT = int(os.environ.get("EVERLEAF_WZ_AVATAR_PORT", "3011"))

sys.path.insert(0, WZPY_ROOT)

from flask import Flask, Response, abort, request  # noqa: E402
from PIL import Image  # noqa: E402
from wzpy.character import CharacterRenderer  # noqa: E402
from wzpy.wz_file import WzFile  # noqa: E402

_ID_RE = re.compile(r"^\d{8}$")


def _integer_arg(name: str, default: int, minimum: int, maximum: int) -> int:
    raw = request.args.get(name, str(default))
    try:
        value = int(raw)
    except (TypeError, ValueError):
        abort(400, f"invalid {name}")
    return max(minimum, min(maximum, value))


def build_app() -> Flask:
    if not os.path.isfile(CHARACTER_WZ) or os.path.getsize(CHARACTER_WZ) <= 0:
        raise SystemExit(f"Character.wz is missing or empty: {CHARACTER_WZ}")

    # Critical production invariant: never give the website renderer a
    # writable handle to the launcher/game client's Character.wz.
    wz = WzFile.open(CHARACTER_WZ, region="GMS", version=83, writable=False)
    renderer = CharacterRenderer(wz, region="GMS")
    app = Flask("everleaf-wz-avatar")

    @app.get("/healthz")
    def healthz() -> Response:
        return Response("ok\n", mimetype="text/plain")

    @app.get("/api/character/compose")
    def compose() -> Response:
        raw_ids = request.args.get("ids", "")
        ids = [part.strip() for part in raw_ids.split(",") if part.strip()]
        if not ids or len(ids) > 40 or any(not _ID_RE.fullmatch(part) for part in ids):
            abort(400, "ids must contain 1-40 eight-digit WZ ids")

        pose = request.args.get("pose", "stand1") or "stand1"
        frame = _integer_arg("frame", 0, 0, 255)
        scale = _integer_arg("scale", 2, 1, 8)

        try:
            image = renderer.compose(ids, pose=pose, frame=frame)
        except Exception as exc:
            app.logger.warning("Character compose failed: %s", exc)
            abort(422, "character composition failed")

        if scale != 1:
            image = image.resize(
                (image.width * scale, image.height * scale),
                Image.Resampling.NEAREST,
            )

        output = io.BytesIO()
        image.save(output, format="PNG", optimize=False)
        data = output.getvalue()
        if len(data) < 100 or data[:8] != b"\x89PNG\r\n\x1a\n":
            abort(500, "renderer produced an invalid PNG")
        return Response(
            data,
            mimetype="image/png",
            headers={"Cache-Control": "no-store", "X-EverLeaf-WZ": "v83-local"},
        )

    return app


def main() -> None:
    app = build_app()
    app.run(host=HOST, port=PORT, debug=False, threaded=False, use_reloader=False)


if __name__ == "__main__":
    main()

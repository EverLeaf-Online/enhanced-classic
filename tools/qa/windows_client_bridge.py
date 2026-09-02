#!/usr/bin/env python3
"""Windows-only input bridge for the disposable EverLeaf QA client.

This bridge intentionally refuses to operate unless the local QA SSH tunnel is
reachable on 127.0.0.1:8484. It drives only the foreground EverLeaf window and
never connects to production directly.

The higher-level agent uses this as the motor layer while database snapshots on
the disposable QA stack provide deterministic observations.
"""
from __future__ import annotations

import argparse
import ctypes
import json
import os
import socket
import sys
import time
from ctypes import wintypes
from pathlib import Path

if sys.platform != "win32":
    raise SystemExit("windows_client_bridge.py must run on Windows")

QA_HOST = "127.0.0.1"
QA_LOGIN_PORT = 8484
WINDOW_TOKEN = "EverLeaf"

user32 = ctypes.WinDLL("user32", use_last_error=True)

WM_KEYDOWN = 0x0100
WM_KEYUP = 0x0101
SW_RESTORE = 9

VK = {
    "backspace": 0x08,
    "tab": 0x09,
    "enter": 0x0D,
    "shift": 0x10,
    "ctrl": 0x11,
    "alt": 0x12,
    "esc": 0x1B,
    "space": 0x20,
    "left": 0x25,
    "up": 0x26,
    "right": 0x27,
    "down": 0x28,
    "insert": 0x2D,
    "delete": 0x2E,
    "home": 0x24,
    "end": 0x23,
    "pageup": 0x21,
    "pagedown": 0x22,
    "0": 0x30,
    "1": 0x31,
    "2": 0x32,
    "3": 0x33,
    "4": 0x34,
    "5": 0x35,
    "6": 0x36,
    "7": 0x37,
    "8": 0x38,
    "9": 0x39,
}
for ch in "abcdefghijklmnopqrstuvwxyz":
    VK[ch] = ord(ch.upper())


def tunnel_ready(timeout: float = 1.0) -> bool:
    try:
        with socket.create_connection((QA_HOST, QA_LOGIN_PORT), timeout=timeout):
            return True
    except OSError:
        return False


def find_everleaf_window() -> int:
    found: list[int] = []
    callback_t = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)

    @callback_t
    def callback(hwnd: int, _lparam: int) -> bool:
        if not user32.IsWindowVisible(hwnd):
            return True
        length = user32.GetWindowTextLengthW(hwnd)
        if length <= 0:
            return True
        buf = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buf, len(buf))
        title = buf.value
        if WINDOW_TOKEN.lower() in title.lower():
            found.append(int(hwnd))
            return False
        return True

    user32.EnumWindows(callback, 0)
    if not found:
        raise RuntimeError("No visible EverLeaf window found")
    return found[0]


def focus(hwnd: int) -> None:
    user32.ShowWindow(hwnd, SW_RESTORE)
    if not user32.SetForegroundWindow(hwnd):
        raise RuntimeError("Could not focus EverLeaf window")
    time.sleep(0.12)


def key_code(name: str) -> int:
    normalized = name.lower().strip()
    if normalized not in VK:
        raise ValueError(f"Unsupported key {name!r}; supported={sorted(VK)}")
    return VK[normalized]


def post_key(hwnd: int, key: str, down: bool) -> None:
    code = key_code(key)
    msg = WM_KEYDOWN if down else WM_KEYUP
    if not user32.PostMessageW(hwnd, msg, code, 0):
        raise RuntimeError(f"PostMessage failed for key={key!r}")


def tap(hwnd: int, key: str, delay: float = 0.05) -> None:
    post_key(hwnd, key, True)
    time.sleep(delay)
    post_key(hwnd, key, False)


def hold(hwnd: int, key: str, seconds: float) -> None:
    if seconds <= 0 or seconds > 10:
        raise ValueError("hold duration must be >0 and <=10 seconds")
    post_key(hwnd, key, True)
    try:
        time.sleep(seconds)
    finally:
        post_key(hwnd, key, False)


def status() -> dict[str, object]:
    out: dict[str, object] = {
        "platform": sys.platform,
        "qa_tunnel": tunnel_ready(),
        "qa_target": f"{QA_HOST}:{QA_LOGIN_PORT}",
    }
    try:
        hwnd = find_everleaf_window()
        length = user32.GetWindowTextLengthW(hwnd)
        buf = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buf, len(buf))
        out.update({"window_found": True, "window_title": buf.value, "hwnd": hwnd})
    except Exception as exc:
        out.update({"window_found": False, "window_error": str(exc)})
    return out


def ensure_safe() -> int:
    if not tunnel_ready():
        raise RuntimeError(
            "QA tunnel 127.0.0.1:8484 is not reachable; refusing to drive the client"
        )
    hwnd = find_everleaf_window()
    focus(hwnd)
    return hwnd


def main() -> int:
    ap = argparse.ArgumentParser(description="EverLeaf Windows QA client bridge")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status")
    sub.add_parser("focus")
    p_tap = sub.add_parser("tap")
    p_tap.add_argument("key")
    p_tap.add_argument("--count", type=int, default=1)
    p_tap.add_argument("--interval", type=float, default=0.08)
    p_hold = sub.add_parser("hold")
    p_hold.add_argument("key")
    p_hold.add_argument("seconds", type=float)
    args = ap.parse_args()

    try:
        if args.cmd == "status":
            print(json.dumps(status(), sort_keys=True))
            return 0
        hwnd = ensure_safe()
        if args.cmd == "focus":
            print(json.dumps({"focused": True, "hwnd": hwnd}, sort_keys=True))
        elif args.cmd == "tap":
            if args.count < 1 or args.count > 100:
                raise ValueError("count must be between 1 and 100")
            for i in range(args.count):
                tap(hwnd, args.key)
                if i + 1 < args.count:
                    time.sleep(max(0.0, args.interval))
            print(json.dumps({"key": args.key, "taps": args.count}, sort_keys=True))
        elif args.cmd == "hold":
            hold(hwnd, args.key, args.seconds)
            print(json.dumps({"key": args.key, "held_seconds": args.seconds}, sort_keys=True))
        return 0
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

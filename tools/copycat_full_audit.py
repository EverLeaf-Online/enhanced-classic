#!/usr/bin/env python3
"""Read-only whole-folder audit for the EverLeaf copycat client snapshot.

Every regular file is streamed through SHA-256. The same streaming pass also
checks high-value ASCII/UTF-16 indicators, URLs, and IPv4 addresses. Multi-GB
WZ files are never loaded into memory.

The source tree is never modified and no source file is executed.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import shutil
import stat
import struct
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

DEFAULT_SOURCE = Path("/home/ubuntu/everleafms copycat")
CHUNK_SIZE = 4 * 1024 * 1024
OVERLAP_SIZE = 2048
MAX_FINDINGS_PER_FILE = 200
MAX_URLS_PER_FILE = 100
MAX_IPS_PER_FILE = 100
MAX_TEXT_COPY_BYTES = 16 * 1024 * 1024
MAX_PE_BYTES = 128 * 1024 * 1024

TEXT_EXTENSIONS = {
    ".txt", ".md", ".ini", ".cfg", ".conf", ".json", ".xml", ".yaml",
    ".yml", ".bat", ".cmd", ".ps1", ".sh", ".log", ".manifest", ".data",
}
PE_EXTENSIONS = {".exe", ".dll", ".ocx", ".cpl", ".scr"}
WZ_EXTENSIONS = {".wz"}

DEFAULT_KEYWORDS = [
    "everleaf", "everleafms", "yuna", "yunams", "mapleezorsia", "ezorsia",
    "redly", "discord", "discord_game_sdk", "gameguard", "hackshield", "hshield",
    "nprotect", "dinput8", "borderless", "resolution", "widescreen", "wasd",
    "fps", "quickslot", "widget", "overlay", "crash", "launcher", "patch", "update",
    "registry", "regedit", "http://", "https://", "132.145.141.79", "8484",
]

URL_RE = re.compile(rb"https?://[A-Za-z0-9._~:/?#\[\]@!$&'()*+,;=%-]{4,512}", re.I)
IP_RE = re.compile(rb"(?<!\d)(?:\d{1,3}\.){3}\d{1,3}(?::\d{1,5})?(?!\d)")

MACHINE_NAMES = {
    0x014C: "x86",
    0x8664: "x64",
    0x01C0: "ARM",
    0xAA64: "ARM64",
}
SUBSYSTEM_NAMES = {
    1: "native",
    2: "windows-gui",
    3: "windows-console",
    9: "windows-ce",
    10: "efi-application",
}


def utc_iso(ts: float) -> str:
    return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()


def dump_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False), encoding="utf-8")


def classify(path: Path) -> str:
    ext = path.suffix.lower()
    if ext in WZ_EXTENSIONS:
        return "wz"
    if ext in PE_EXTENSIONS:
        return "pe"
    if ext in TEXT_EXTENSIONS:
        return "text"
    return "other"


def valid_ipv4(value: str) -> bool:
    host = value.split(":", 1)[0]
    parts = host.split(".")
    if len(parts) != 4:
        return False
    try:
        return all(0 <= int(part) <= 255 for part in parts)
    except ValueError:
        return False


def context_for(blob: bytes, start: int, length: int, encoding: str) -> str:
    if encoding == "utf16le":
        left = max(0, start - 192)
        left -= left % 2
        right = min(len(blob), start + length + 320)
        right -= right % 2
        try:
            return blob[left:right].decode("utf-16le", "replace").replace("\x00", "")
        except UnicodeDecodeError:
            pass
    left = max(0, start - 96)
    right = min(len(blob), start + length + 160)
    sample = blob[left:right]
    return "".join(chr(b) if 32 <= b < 127 else "." for b in sample)


@dataclass(frozen=True)
class KeywordMatcher:
    ascii_pattern: re.Pattern[bytes] | None
    utf16_pattern: re.Pattern[bytes] | None
    ascii_labels: dict[bytes, str]
    utf16_labels: dict[bytes, str]


def build_keyword_matcher(keywords: list[str]) -> KeywordMatcher:
    ascii_labels: dict[bytes, str] = {}
    utf16_labels: dict[bytes, str] = {}
    for keyword in keywords:
        normalized = keyword.strip()
        if not normalized:
            continue
        ascii_key = normalized.lower().encode("utf-8", "ignore")
        utf16_key = normalized.lower().encode("utf-16le", "ignore")
        if ascii_key:
            ascii_labels.setdefault(ascii_key, normalized)
        if utf16_key:
            utf16_labels.setdefault(utf16_key, normalized)

    def pattern(keys: Iterable[bytes]) -> re.Pattern[bytes] | None:
        ordered = sorted(set(keys), key=len, reverse=True)
        if not ordered:
            return None
        return re.compile(b"(?:" + b"|".join(re.escape(key) for key in ordered) + b")")

    return KeywordMatcher(
        ascii_pattern=pattern(ascii_labels.keys()),
        utf16_pattern=pattern(utf16_labels.keys()),
        ascii_labels=ascii_labels,
        utf16_labels=utf16_labels,
    )


@dataclass
class StreamAnalysis:
    sha256: str
    findings: list[dict[str, Any]]
    urls: list[str]
    ips: list[str]


def stream_analyze(path: Path, matcher: KeywordMatcher) -> StreamAnalysis:
    digest = hashlib.sha256()
    findings: list[dict[str, Any]] = []
    urls: list[str] = []
    ips: list[str] = []
    seen_findings: set[tuple[str, str, int]] = set()
    seen_urls: set[str] = set()
    seen_ips: set[str] = set()

    tail = b""
    absolute = 0
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(CHUNK_SIZE)
            if not chunk:
                break
            digest.update(chunk)
            scan = tail + chunk
            scan_base = max(0, absolute - len(tail))
            lower = scan.lower()

            if len(findings) < MAX_FINDINGS_PER_FILE:
                for encoding, compiled, labels in (
                    ("ascii", matcher.ascii_pattern, matcher.ascii_labels),
                    ("utf16le", matcher.utf16_pattern, matcher.utf16_labels),
                ):
                    if compiled is None:
                        continue
                    for match in compiled.finditer(lower):
                        matched = match.group(0)
                        label = labels.get(matched, matched.decode("latin1", "replace"))
                        offset = scan_base + match.start()
                        key = (encoding, label.lower(), offset)
                        if key in seen_findings:
                            continue
                        seen_findings.add(key)
                        findings.append({
                            "keyword": label,
                            "encoding": encoding,
                            "offset": offset,
                            "context": context_for(scan, match.start(), len(matched), encoding),
                        })
                        if len(findings) >= MAX_FINDINGS_PER_FILE:
                            break

            if len(urls) < MAX_URLS_PER_FILE:
                for match in URL_RE.finditer(scan):
                    value = match.group(0).decode("ascii", "replace")
                    if value in seen_urls:
                        continue
                    seen_urls.add(value)
                    urls.append(value)
                    if len(urls) >= MAX_URLS_PER_FILE:
                        break

            if len(ips) < MAX_IPS_PER_FILE:
                for match in IP_RE.finditer(scan):
                    value = match.group(0).decode("ascii", "replace")
                    if not valid_ipv4(value) or value in seen_ips:
                        continue
                    seen_ips.add(value)
                    ips.append(value)
                    if len(ips) >= MAX_IPS_PER_FILE:
                        break

            tail = scan[-OVERLAP_SIZE:]
            absolute += len(chunk)

    return StreamAnalysis(digest.hexdigest(), findings, urls, ips)


def rva_to_offset(rva: int, sections: list[dict[str, int]]) -> int | None:
    for section in sections:
        va = section["virtual_address"]
        span = max(section["virtual_size"], section["raw_size"])
        if va <= rva < va + span:
            delta = rva - va
            if delta >= section["raw_size"]:
                return None
            return section["raw_ptr"] + delta
    return rva if rva >= 0 else None


def c_string(data: bytes, offset: int, max_len: int = 512) -> str | None:
    if offset < 0 or offset >= len(data):
        return None
    end = data.find(b"\0", offset, min(len(data), offset + max_len))
    if end < 0:
        end = min(len(data), offset + max_len)
    return data[offset:end].decode("latin1", "replace")


def parse_pe(path: Path) -> dict[str, Any] | None:
    try:
        size = path.stat().st_size
        if size <= 0 or size > MAX_PE_BYTES:
            return {"error": f"PE file size outside parser bound: {size}"}
        data = path.read_bytes()
    except OSError as exc:
        return {"error": f"read failed: {exc}"}

    try:
        if len(data) < 0x40 or data[:2] != b"MZ":
            return None
        pe_off = struct.unpack_from("<I", data, 0x3C)[0]
        if pe_off + 24 > len(data) or data[pe_off:pe_off + 4] != b"PE\0\0":
            return None

        coff = pe_off + 4
        machine, section_count, timestamp, _, _, opt_size, characteristics = struct.unpack_from(
            "<HHIIIHH", data, coff
        )
        opt = coff + 20
        if opt + opt_size > len(data):
            raise ValueError("optional header exceeds file")

        magic = struct.unpack_from("<H", data, opt)[0]
        if magic == 0x10B:
            pe_format = "PE32"
            image_base = struct.unpack_from("<I", data, opt + 28)[0]
            data_dir = opt + 96
        elif magic == 0x20B:
            pe_format = "PE32+"
            image_base = struct.unpack_from("<Q", data, opt + 24)[0]
            data_dir = opt + 112
        else:
            raise ValueError(f"unknown optional-header magic 0x{magic:04X}")

        entry_point = struct.unpack_from("<I", data, opt + 16)[0]
        size_of_image = struct.unpack_from("<I", data, opt + 56)[0]
        subsystem = struct.unpack_from("<H", data, opt + 68)[0]
        dll_characteristics = struct.unpack_from("<H", data, opt + 70)[0]

        sections: list[dict[str, Any]] = []
        sec_off = opt + opt_size
        for index in range(section_count):
            off = sec_off + index * 40
            if off + 40 > len(data):
                break
            name = data[off:off + 8].split(b"\0", 1)[0].decode("ascii", "replace")
            virtual_size, virtual_address, raw_size, raw_ptr = struct.unpack_from("<IIII", data, off + 8)
            sec_flags = struct.unpack_from("<I", data, off + 36)[0]
            sections.append({
                "name": name,
                "virtual_size": virtual_size,
                "virtual_address": virtual_address,
                "raw_size": raw_size,
                "raw_ptr": raw_ptr,
                "characteristics": f"0x{sec_flags:08X}",
            })

        imports: list[str] = []
        if data_dir + 16 <= opt + opt_size:
            import_rva, _ = struct.unpack_from("<II", data, data_dir + 8)
            import_off = rva_to_offset(import_rva, sections) if import_rva else None
            if import_off is not None and import_off < len(data):
                for index in range(4096):
                    desc = import_off + index * 20
                    if desc + 20 > len(data):
                        break
                    values = struct.unpack_from("<IIIII", data, desc)
                    if not any(values):
                        break
                    name_rva = values[3]
                    name_off = rva_to_offset(name_rva, sections)
                    if name_off is None:
                        continue
                    name = c_string(data, name_off)
                    if name and name not in imports:
                        imports.append(name)

        return {
            "machine": f"0x{machine:04X}",
            "machine_name": MACHINE_NAMES.get(machine, "unknown"),
            "section_count": section_count,
            "coff_timestamp": timestamp,
            "coff_timestamp_utc": utc_iso(timestamp) if timestamp else None,
            "characteristics": f"0x{characteristics:04X}",
            "large_address_aware": bool(characteristics & 0x0020),
            "is_dll": bool(characteristics & 0x2000),
            "pe_format": pe_format,
            "entry_point_rva": f"0x{entry_point:08X}",
            "image_base": f"0x{image_base:X}",
            "size_of_image": size_of_image,
            "subsystem": subsystem,
            "subsystem_name": SUBSYSTEM_NAMES.get(subsystem, "unknown"),
            "dll_characteristics": f"0x{dll_characteristics:04X}",
            "dynamic_base": bool(dll_characteristics & 0x0040),
            "nx_compat": bool(dll_characteristics & 0x0100),
            "imports": imports,
            "sections": sections,
        }
    except (struct.error, ValueError, OverflowError) as exc:
        return {"error": f"PE parse failed: {exc}"}


def copy_text_evidence(source: Path, output_root: Path, rel: str, size: int) -> dict[str, Any] | None:
    if source.suffix.lower() not in TEXT_EXTENSIONS:
        return None
    target = output_root / "text" / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        if size <= MAX_TEXT_COPY_BYTES:
            shutil.copyfile(source, target)
            return {"copied": True, "truncated": False, "path": str(target.relative_to(output_root))}
        with source.open("rb") as src, target.open("wb") as dst:
            dst.write(src.read(256 * 1024))
            dst.write(b"\n\n--- EVERLEAF AUDIT REPORT COPY: MIDDLE OMITTED ---\n\n")
            src.seek(max(0, size - 256 * 1024))
            dst.write(src.read(256 * 1024))
        return {"copied": True, "truncated": True, "path": str(target.relative_to(output_root))}
    except OSError as exc:
        return {"copied": False, "error": str(exc)}


def iter_tree(source_root: Path) -> Iterable[Path]:
    for root, dirs, files in os.walk(source_root, topdown=True, followlinks=False):
        dirs.sort(key=str.lower)
        files.sort(key=str.lower)
        root_path = Path(root)
        for name in files:
            yield root_path / name
        for name in dirs:
            candidate = root_path / name
            if candidate.is_symlink():
                yield candidate


def build_summary(
    source: Path,
    records: list[dict[str, Any]],
    duplicates: list[dict[str, Any]],
    pe_records: list[dict[str, Any]],
    wz_records: list[dict[str, Any]],
) -> str:
    regular = [record for record in records if record.get("type") == "file"]
    total_bytes = sum(record.get("size", 0) for record in regular)
    by_ext = Counter((Path(record["path"]).suffix.lower() or "<none>") for record in regular)
    largest = sorted(regular, key=lambda record: record.get("size", 0), reverse=True)[:20]
    evidence_files = [
        record for record in regular
        if record.get("finding_count", 0) or record.get("urls") or record.get("ips")
    ]

    lines = [
        "# Copycat client full-folder audit",
        "",
        f"- Source: `{source}`",
        f"- Generated UTC: `{datetime.now(timezone.utc).isoformat()}`",
        f"- Regular files: **{len(regular)}**",
        f"- Total bytes hashed/scanned: **{total_bytes:,}**",
        f"- PE files parsed: **{len(pe_records)}**",
        f"- WZ files: **{len(wz_records)}**",
        f"- Duplicate hash groups: **{len(duplicates)}**",
        f"- Files with indicators: **{len(evidence_files)}**",
        "",
        "Every regular file was read through SHA-256 and the streaming indicator scanner. No source file was executed or modified.",
        "",
        "## Largest files",
        "",
        "| Size | Path | SHA-256 |",
        "|---:|---|---|",
    ]
    for record in largest:
        lines.append(f"| {record['size']:,} | `{record['path']}` | `{record.get('sha256', '')}` |")

    lines.extend(["", "## File types", "", "| Extension | Count |", "|---|---:|"])
    for ext, count in by_ext.most_common():
        lines.append(f"| `{ext}` | {count} |")

    lines.extend(["", "## PE executables / DLLs", "", "| Path | Arch | LAA | NX | ASLR | Imports |", "|---|---|---:|---:|---:|---:|"])
    for record in pe_records:
        pe = record.get("pe") or {}
        lines.append(
            f"| `{record['path']}` | {pe.get('machine_name', '?')} | "
            f"{pe.get('large_address_aware', '?')} | {pe.get('nx_compat', '?')} | "
            f"{pe.get('dynamic_base', '?')} | {len(pe.get('imports', []))} |"
        )

    lines.extend(["", "## WZ inventory", "", "| Path | Size | SHA-256 |", "|---|---:|---|"])
    for record in wz_records:
        lines.append(f"| `{record['path']}` | {record['size']:,} | `{record.get('sha256', '')}` |")

    lines.extend([
        "",
        "## Evidence files",
        "",
        "- `inventory.json` / `inventory.csv`: complete metadata and hashes",
        "- `pe-analysis.json`: PE headers, security flags, sections and imported DLLs",
        "- `duplicates.json`: byte-identical files grouped by SHA-256",
        "- `wz-inventory.json`: every WZ size/hash/timestamp",
        "- `findings.json`: keyword, URL and IP evidence with offsets",
        "- `text/`: safe copies of human-readable scripts/configs/docs",
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Read-only full-folder EverLeaf copycat client auditor")
    parser.add_argument("source", nargs="?", default=str(DEFAULT_SOURCE), help="client folder to audit")
    parser.add_argument("--output", help="report output directory")
    parser.add_argument("--keyword", action="append", default=[], help="additional case-insensitive indicator")
    args = parser.parse_args()

    source = Path(args.source).expanduser().resolve()
    if not source.is_dir():
        print(f"ERROR: source directory not found: {source}", file=sys.stderr)
        return 2

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%SZ")
    output = (
        Path(args.output).expanduser().resolve()
        if args.output
        else Path.home() / f"copycat-audit-{timestamp}"
    )
    if output == source or source in output.parents:
        print("ERROR: output must not be inside the source tree", file=sys.stderr)
        return 2
    output.mkdir(parents=True, exist_ok=False)

    keywords = list(dict.fromkeys(DEFAULT_KEYWORDS + args.keyword))
    matcher = build_keyword_matcher(keywords)

    records: list[dict[str, Any]] = []
    pe_records: list[dict[str, Any]] = []
    wz_records: list[dict[str, Any]] = []
    finding_records: list[dict[str, Any]] = []
    hashes: defaultdict[str, list[str]] = defaultdict(list)

    print(f"Auditing: {source}")
    print(f"Report:   {output}")

    for index, path in enumerate(iter_tree(source), start=1):
        rel = str(path.relative_to(source)).replace("\\", "/")
        try:
            lst = path.lstat()
        except OSError as exc:
            records.append({"path": rel, "type": "error", "error": str(exc)})
            continue

        if stat.S_ISLNK(lst.st_mode):
            try:
                target = os.readlink(path)
            except OSError as exc:
                target = f"<unreadable: {exc}>"
            records.append({
                "path": rel,
                "type": "symlink",
                "target": target,
                "mtime_utc": utc_iso(lst.st_mtime),
                "mode": oct(stat.S_IMODE(lst.st_mode)),
            })
            continue

        if not stat.S_ISREG(lst.st_mode):
            records.append({"path": rel, "type": "other", "size": lst.st_size})
            continue

        print(f"[{index}] {rel} ({lst.st_size:,} bytes)")
        try:
            analysis = stream_analyze(path, matcher)
        except OSError as exc:
            records.append({
                "path": rel,
                "type": "file",
                "size": lst.st_size,
                "error": str(exc),
            })
            continue

        record: dict[str, Any] = {
            "path": rel,
            "type": "file",
            "class": classify(path),
            "extension": path.suffix.lower(),
            "size": lst.st_size,
            "mtime_utc": utc_iso(lst.st_mtime),
            "mode": oct(stat.S_IMODE(lst.st_mode)),
            "sha256": analysis.sha256,
            "finding_count": len(analysis.findings),
            "urls": analysis.urls,
            "ips": analysis.ips,
        }

        text_evidence = copy_text_evidence(path, output, rel, lst.st_size)
        if text_evidence:
            record["text_evidence"] = text_evidence

        records.append(record)
        hashes[analysis.sha256].append(rel)

        if analysis.findings or analysis.urls or analysis.ips:
            finding_records.append({
                "path": rel,
                "sha256": analysis.sha256,
                "keywords": analysis.findings,
                "urls": analysis.urls,
                "ips": analysis.ips,
            })

        if path.suffix.lower() in PE_EXTENSIONS:
            pe_records.append({
                "path": rel,
                "size": lst.st_size,
                "sha256": analysis.sha256,
                "pe": parse_pe(path),
            })

        if path.suffix.lower() in WZ_EXTENSIONS:
            wz_records.append({
                "path": rel,
                "size": lst.st_size,
                "mtime_utc": utc_iso(lst.st_mtime),
                "sha256": analysis.sha256,
                "finding_count": len(analysis.findings),
            })

    duplicates = [
        {
            "sha256": digest,
            "size": next(
                (record.get("size") for record in records if record.get("sha256") == digest),
                None,
            ),
            "paths": paths,
        }
        for digest, paths in sorted(hashes.items())
        if len(paths) > 1
    ]

    dump_json(output / "inventory.json", records)
    dump_json(output / "pe-analysis.json", pe_records)
    dump_json(output / "duplicates.json", duplicates)
    dump_json(output / "wz-inventory.json", wz_records)
    dump_json(output / "findings.json", finding_records)

    with (output / "inventory.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "path", "type", "class", "extension", "size", "mtime_utc",
                "mode", "sha256", "finding_count",
            ],
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(records)

    (output / "SUMMARY.md").write_text(
        build_summary(source, records, duplicates, pe_records, wz_records),
        encoding="utf-8",
    )

    print("\nAudit complete.")
    print(f"Summary:   {output / 'SUMMARY.md'}")
    print(f"Inventory: {output / 'inventory.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
import hashlib
import json
import shutil
import sys
import tempfile
from pathlib import Path
from urllib.parse import unquote, urlparse

patch_root = Path(sys.argv[1]).resolve()
baseline = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
manifest = json.loads((patch_root / "manifest.json").read_text(encoding="utf-8"))
files = manifest.get("files")
assert isinstance(files, list) and files, "manifest is empty"
expected = {entry["path"].lower() for entry in baseline["managedFiles"]}
assert {entry["path"].lower() for entry in files} == expected, "manifest does not exactly cover baseline"

for entry in files:
    assert isinstance(entry["size"], int) and entry["size"] > 0
    assert len(entry["sha256"]) == 64 and all(c in "0123456789abcdef" for c in entry["sha256"])
    parsed = urlparse(entry["url"])
    assert not parsed.scheme and not parsed.netloc and parsed.path.startswith("/patches/")
    source = patch_root / "files" / entry["path"]
    digest = hashlib.sha256()
    with source.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    assert source.stat().st_size == entry["size"] and digest.hexdigest() == entry["sha256"]

with tempfile.TemporaryDirectory() as temp:
    client = Path(temp)
    victim = files[0]
    destination = client / victim["path"]
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(b"deliberately corrupted")
    assert hashlib.sha256(destination.read_bytes()).hexdigest() != victim["sha256"]
    temporary = destination.with_name(destination.name + ".everleaf-new")
    shutil.copyfile(patch_root / "files" / victim["path"], temporary)
    assert temporary.stat().st_size == victim["size"]
    assert hashlib.sha256(temporary.read_bytes()).hexdigest() == victim["sha256"]
    temporary.replace(destination)
    assert hashlib.sha256(destination.read_bytes()).hexdigest() == victim["sha256"]

print(f"Managed repair fixture passed for {len(files)} files; corrupted {files[0]['path']} was repaired.")

# Native EverLeaf candidate verification

Run from the repository root on Linux (Python 3.9+):

```sh
python3 client/scripts/test-native-package.py
python3 client/scripts/audit-native-package.py \
  --candidate /path/to/staged/client \
  --baseline /path/to/production/payload \
  --report /path/outside/both/directories/native-client-audit.json
```

The audit reads both directories without modifying them and streams file contents
to bound memory usage. Use a stable baseline and candidate while it runs.
It records SHA-256 for every candidate file and its production counterpart.
Only UI.wz may differ in this UI-only migration; native runtime files,
EverLeaf_UI.wz, and all game data must match production. Unexpected files,
missing files, symlinks, subdirectories, case collisions, and known donor runtime
files block the structural gate. Keep reports and source outside the payload.

ASCII and UTF-16LE donor-token matches are review evidence, not automatic proof
of visible branding. Short words can occur coincidentally in compressed data.
Matching hashes identify occurrences already present in the production baseline.
A raw scan cannot inspect encrypted/compressed WZ text or artwork.

A successful exit means structural and preservation checks passed only.
The report always leaves releaseReady false. Separate required work remains:
decoded WZ branding/panorama review, native Discord integration/configuration,
and real Windows login -> world -> character -> channel -> map testing.
This tool does not deploy or update launcher manifests.

The regression tests use Linux filesystem semantics to exercise Windows filename
collisions and symbolic-link rejection.

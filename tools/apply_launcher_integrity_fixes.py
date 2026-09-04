#!/usr/bin/env python3
"""Apply release-time EverLeaf launcher integrity fixes idempotently."""
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
path=ROOT/'launcher/EverLeaf.Launcher/LauncherServices.cs'
text=path.read_text(encoding='utf-8')
changed=False

# Production signs the manifest with RSA-PSS (saltLength=32). The launcher must
# verify the same padding scheme; PKCS#1 v1.5 verification rejects valid live manifests.
if 'RSASignaturePadding.Pkcs1' in text:
    text=text.replace('RSASignaturePadding.Pkcs1','RSASignaturePadding.Pss')
    changed=True

# Make stale-download cleanup directly testable. A prior interrupted download must
# never be mistaken for a verified managed client file on the next run. Modern
# source already contains the internal helper; in that case this transform must be
# a true no-op rather than rewriting the compatibility TryDelete wrapper into a
# duplicate method declaration.
if 'internal static void RemoveStaleDownload(string path)' in text:
    pass
elif 'TryDelete(' in text:
    text=text.replace('TryDelete(', 'RemoveStaleDownload(')
    text=text.replace('private static void RemoveStaleDownload(string path)',
                      'internal static void RemoveStaleDownload(string path)')
    changed=True
elif 'private static void RemoveStaleDownload(string path)' in text:
    text=text.replace('private static void RemoveStaleDownload(string path)',
                      'internal static void RemoveStaleDownload(string path)')
    changed=True

path.write_text(text,encoding='utf-8')

out=path.read_text(encoding='utf-8')
assert 'RSASignaturePadding.Pss' in out
assert 'RSASignaturePadding.Pkcs1' not in out
assert 'internal static void RemoveStaleDownload(string path)' in out
print('EverLeaf launcher integrity transform: PASS' + (' (updated)' if changed else ' (already applied)'))

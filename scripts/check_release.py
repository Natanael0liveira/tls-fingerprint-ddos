#!/usr/bin/env python3
"""Verify the immutable manuscript and figure sources."""
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1] / 'papers/http-session-noms'
manifest = json.loads((root / 'freeze.json').read_text())
failures = []
for name, expected in manifest['sha256'].items():
    path = root / name
    if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
        failures.append(name)
if failures:
    raise SystemExit('Frozen files changed: ' + ', '.join(failures))
print(f"r53 freeze verified: {len(manifest['sha256'])} files")

#!/usr/bin/env python3
"""Refresh public artifact checksums without copying a full manuscript."""
import json
from check_release import ROOT, PUBLIC_FILES, DELIVERY, manuscript_paths, sha256


def main():
    found = manuscript_paths()
    if found:
        raise SystemExit('Move full manuscript files to the private freeze before packaging:\n'
                         + '\n'.join(str(p.relative_to(ROOT)) for p in found))
    for name in PUBLIC_FILES:
        if not (ROOT / name).is_file():
            raise SystemExit(f'Missing public artifact input: {name}')
    report = json.loads((DELIVERY / 'verification.json').read_text())
    for name in ('tables.json', 'audit.json'):
        data = json.loads((ROOT / 'experiments/sprint-6-noms/results/manuscript' / name).read_text())
        if data['source_sha256'] != report['source_sha256']:
            raise SystemExit(f'{name} does not identify the recorded submitted source')
    (DELIVERY / 'SHA256SUMS').write_text(''.join(
        f'{sha256(ROOT / name)}  {name}\n' for name in sorted(PUBLIC_FILES)))
    print(f'Public artifact manifest refreshed: {len(PUBLIC_FILES)} files; no manuscript copied')


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Verify the public artifact; optionally verify a separate private paper freeze.

Public checks use committed table snapshots and reductions, without a manuscript.
The historical Git tag still identifies the submitted source; removing current
files does not erase published history.
"""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / 'papers/http-session-noms'
DELIVERY = ROOT / 'submissions/noms2027'
TABLES = ROOT / 'experiments/sprint-6-noms/results/manuscript'
PUBLIC_FILES = (
    'submissions/noms2027/README.md',
    'submissions/noms2027/verification.json',
    'archive/noms2027/r53/freeze.json',
    'papers/http-session-noms/references.bib',
    *(f'papers/http-session-noms/figures/{name}' for name in (
        'fig1_scoping.png', 'fig6_stops.png', 'fig1_r48.py', 'make_figures_en.r13.py')),
    'experiments/sprint-6-noms/results/manuscript/tables.json',
    'experiments/sprint-6-noms/results/manuscript/audit.json',
    *(f'experiments/sprint-6-noms/results/manuscript/table-{i}.csv' for i in range(1, 9)),
)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_hashes(directory, entries):
    failures = []
    for name, expected in entries.items():
        path = directory / name
        if Path(name).is_absolute() or '..' in Path(name).parts:
            failures.append(f'Invalid checksum path: {name}')
            continue
        if not path.is_file() or sha256(path) != expected:
            failures.append(str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path))
    return failures


def manuscript_paths():
    """Find full manuscript files in the public tree, excluding private history."""
    found = []
    for directory in (PAPER, DELIVERY, ROOT / 'archive/noms2027/r53'):
        if directory.exists():
            found.extend(p for p in directory.rglob('*')
                         if p.is_file() and p.suffix.lower() in {'.tex', '.pdf', '.diff', '.zip'})
    return found


def verify_private(directory, report):
    frozen = json.loads((directory / 'freeze.json').read_text())
    entries = frozen['sha256']
    failures = verify_hashes(directory, entries)
    if not entries:
        failures.append('Private freeze has no file checksums')
    if frozen['source_sha256'] != report['source_sha256']:
        failures.append('Private freeze identifies a different submitted source')
    if frozen['submitted_commit'] != report['submission']['frozen_commit']:
        failures.append('Private freeze identifies a different submitted commit')
    for name, key in [('paper/article.tex', 'source_sha256'),
                      ('submission/latex/article.tex', 'source_sha256'),
                      ('paper/article.pdf', 'pdf_sha256'),
                      ('submission/article.pdf', 'pdf_sha256')]:
        path = directory / name
        if name not in entries or not path.is_file() or sha256(path) != report[key]:
            failures.append(f'Private submitted file differs: {name}')
    return failures


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--private', type=Path, help='Also verify this local frozen paper directory')
    args = parser.parse_args()
    failures = []
    entries = {}
    for line in (DELIVERY / 'SHA256SUMS').read_text().splitlines():
        expected, name = line.split('  ', 1)
        if name in entries:
            raise SystemExit(f'Duplicate checksum entry: {name}')
        entries[name] = expected
    if set(entries) != set(PUBLIC_FILES):
        failures.append('Public checksum manifest has missing or unexpected entries')
    failures += verify_hashes(ROOT, entries)
    failures += [f'Full manuscript file in public tree: {p.relative_to(ROOT)}'
                 for p in manuscript_paths()]
    report = json.loads((DELIVERY / 'verification.json').read_text())
    for name in ('tables.json', 'audit.json'):
        snapshot = json.loads((TABLES / name).read_text())
        if snapshot['source_sha256'] != report['source_sha256']:
            failures.append(f'{name} identifies a different manuscript source')
    if sha256(PAPER / 'references.bib') != report['bibliography_sha256']:
        failures.append('Bibliography differs from its recorded hash')
    if args.private:
        failures += verify_private(args.private.resolve(), report)
    if failures:
        raise SystemExit('Artifact verification failed:\n- ' + '\n- '.join(failures))
    print(f'Public artifact verified: {len(entries)} checksums; no full manuscript in current tree')
    print('Table snapshots identify submitted source: ' + report['source_sha256'])
    if args.private:
        print('Private manuscript freeze verified separately')
    else:
        print('Full source/PDF verification requires the separate private freeze (--private)')


if __name__ == '__main__':
    main()

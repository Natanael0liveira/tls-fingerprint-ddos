#!/usr/bin/env python3
"""Verify the current delivery, its canonical source and the frozen r53 archive.

Current PDFs are local build products and may be absent in a public checkout.
When present, both copies must match the recorded PDF hash. All source files and
the archived r53 PDF are required in every checkout.
"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / 'papers/http-session-noms'
DELIVERY = ROOT / 'submissions/noms2027'
BASELINE = ROOT / 'archive/noms2027/r53'
COPIES = {
    'latex/article.tex': 'article.tex',
    'latex/references.bib': 'references.bib',
    'latex/IEEEtran.cls': 'IEEEtran.cls',
    'latex/IEEEtran.bst': 'IEEEtran.bst',
    'latex/stfloats.sty': 'stfloats.sty',
    'latex/figures/fig1_scoping.png': 'figures/fig1_scoping.png',
    'latex/figures/fig6_stops.png': 'figures/fig6_stops.png',
    'figure-sources/fig1_r48.py': 'figures/fig1_r48.py',
    'figure-sources/make_figures_en.r13.py': 'figures/make_figures_en.r13.py',
}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_hashes(directory, entries, optional=()):
    failures = []
    for name, expected in entries.items():
        path = directory / name
        if name in optional and not path.exists():
            continue
        if not path.is_file() or sha256(path) != expected:
            failures.append(str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path))
    return failures


def main():
    frozen = json.loads((BASELINE / 'freeze.json').read_text())
    failures = verify_hashes(BASELINE, frozen['sha256'])
    entries = {}
    for line in (DELIVERY / 'SHA256SUMS').read_text().splitlines():
        expected, name = line.split('  ', 1)
        if name in entries:
            raise SystemExit(f'Duplicate checksum entry: {name}')
        entries[name] = expected
    required = set(COPIES) | {'README.md', 'verification.json', 'changes-from-r53.diff', 'article.pdf'}
    if set(entries) != required:
        failures.append('submission checksum manifest has missing or unexpected entries')
    failures += verify_hashes(DELIVERY, entries, optional={'article.pdf'})
    for copy, source in COPIES.items():
        a, b = DELIVERY / copy, PAPER / source
        if not a.is_file() or not b.is_file() or sha256(a) != sha256(b):
            failures.append(f'submission copy differs from canonical source: {copy}')
    verification = json.loads((DELIVERY / 'verification.json').read_text())
    for key, path in [('source_sha256', PAPER / 'article.tex'),
                      ('bibliography_sha256', PAPER / 'references.bib')]:
        if sha256(path) != verification[key]:
            failures.append(f'verification no longer describes {path.name}')
    a, b = PAPER / 'article.pdf', DELIVERY / 'article.pdf'
    if a.exists() != b.exists():
        failures.append('only one of the two local PDF copies exists')
    elif a.exists():
        if sha256(a) != verification['pdf_sha256'] or sha256(b) != verification['pdf_sha256']:
            failures.append('local PDF copies differ from the verified PDF')
    if failures:
        raise SystemExit('Artifact verification failed:\n- ' + '\n- '.join(failures))
    print(f"r53 archive verified: {len(frozen['sha256'])} files")
    print(f'Current delivery verified: {len(entries)} checksums, {len(COPIES)} canonical source copies')
    print('Verified PDF copies match' if a.exists() else 'Local PDFs absent; source checks passed')


if __name__ == '__main__':
    main()

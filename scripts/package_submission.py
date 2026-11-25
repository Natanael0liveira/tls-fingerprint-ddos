#!/usr/bin/env python3
"""Synchronize the delivery from the manuscript after its verification is recorded.

This copies build inputs and the verified PDF; it does not run new experiments
or carry an old verification report forward to a different source or PDF.
"""
import difflib
import json
import shutil

from check_release import BASELINE, COPIES, DELIVERY, PAPER, sha256


def main():
    report = json.loads((DELIVERY / 'verification.json').read_text())
    for path, key in [(PAPER / 'article.tex', 'source_sha256'),
                      (PAPER / 'references.bib', 'bibliography_sha256'),
                      (PAPER / 'article.pdf', 'pdf_sha256')]:
        if not path.is_file() or sha256(path) != report[key]:
            raise SystemExit(f'{path.name} is missing or differs from verification.json; verify the new manuscript first')
    # Validate every input before touching the delivery.
    for source in COPIES.values():
        if not (PAPER / source).is_file():
            raise SystemExit(f'Missing manuscript dependency: {source}')
    baseline = (BASELINE / 'article.tex').read_text().splitlines(keepends=True)
    current = (PAPER / 'article.tex').read_text().splitlines(keepends=True)
    for copy, source in COPIES.items():
        destination = DELIVERY / copy
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(PAPER / source, destination)
    shutil.copy2(PAPER / 'article.pdf', DELIVERY / 'article.pdf')
    (DELIVERY / 'changes-from-r53.diff').write_text(''.join(difflib.unified_diff(
        baseline, current, fromfile='r53/article.tex', tofile='submission/article.tex')))
    names = sorted([*COPIES, 'article.pdf', 'README.md', 'verification.json', 'changes-from-r53.diff'])
    (DELIVERY / 'SHA256SUMS').write_text(''.join(f'{sha256(DELIVERY / name)}  {name}\n' for name in names))
    print(f'Submission synchronized: {len(names)} files in {DELIVERY.relative_to(PAPER.parents[1])}')


if __name__ == '__main__':
    main()

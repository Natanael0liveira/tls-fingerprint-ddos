#!/usr/bin/env python3
"""Check/export the public table snapshot, optionally comparing a private frozen TeX.

The public snapshot is a transcription, not experimental reproduction. Its rows
are independently checked against reductions by audit_paper.py.
"""
import argparse
import csv
import hashlib
import io
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'experiments/sprint-6-noms/results/manuscript'
REPORT = ROOT / 'submissions/noms2027/verification.json'
LABELS = ['related', 'configs', 'floor', 'real', 'block', 'symbolic', 'triggers']
HEADERS = [
    ['work', 'selection', 'question'],
    ['configuration', 'trigger', 'scope', 'fleets'],
    ['endpoint', 'median_origins', 'lambda_binomial', 'lambda_beta', 'primary_new_in_sample/cross_fitted', 'primary_shared_in_sample/cross_fitted', 'beta_new_in_sample/cross_fitted', 'beta_shared_in_sample/cross_fitted'],
    ['filter', 'attack1_requests_pct', 'attack1_attackers_pct', 'attack1_legitimate_pct', 'attack1_alternative_legitimate_pct', 'attack2_requests_pct', 'attack2_attackers_pct', 'attack2_legitimate_pct', 'attack2_alternative_legitimate_pct', 'clean_FA_pct'],
    ['configuration', 'FA_all_pct', 'FA_E1_pct', 'FA_max_E2_E4_pct', 'median_collateral_per_FA_pct', 'crowds_pct', 'E1_0.1x_new_pct', 'E1_0.1x_shared_pct', 'pooled_100_new_pct', 'pooled_100_shared_pct'],
    ['scenario', 'binomial_recall_pct', 'binomial_collateral_pct', 'binomial_F1', 'modal_recall_pct', 'zscore_recall_pct', 'novelty_recall_pct'],
    ['trigger', 'scope', 'E1_FA_dev_pct', 'E1_FA_held_pct', 'max_E2_E4_FA_dev_pct', 'max_E2_E4_FA_held_pct', 'E1_new_dev_pct', 'E1_new_held_pct', 'E1_shared_dev_pct', 'crowds_dev_pct', 'median_collateral_per_FA_dev_pct'],
]
SPECS = dict(zip(LABELS, HEADERS))
SPECS['overview'] = ['policy', 'E1_0.1x_bots_pct', 'clean_action_windows_pct',
                     'median_legitimate_exposure_per_action_pct', 'fallback_origin_windows_pct']


def plain(s):
    s = re.sub(r'\$?\^\{[^}]*\}\$?', '', s) if not s.strip().startswith('$10^') else s
    s = re.sub(r'\\(?:textbf|textit|emph)\{([^{}]*)\}', r'\1', s)
    s = s.replace(r'\%', '%').replace(r'\,', '').replace(r'\ ', ' ')
    s = s.replace(r'\cup', 'union').replace(r'\Omega', 'Omega')
    return s.replace('$', '').replace('{=}', '=').strip()


def extract(source_path=None):
    expected = json.loads(REPORT.read_text())['source_sha256']
    if source_path is None:
        data = json.loads((DEST / 'tables.json').read_text())
        if data['source_sha256'] != expected:
            raise ValueError('Table snapshot identifies a different submitted manuscript')
        tables = data['tables']
        if len(tables) != len(SPECS) or {t['label'] for t in tables} != {'tab:' + s for s in SPECS}:
            raise ValueError('Table snapshot has missing or duplicate labels')
        for number, table in enumerate(tables, 1):
            if table['number'] != number or any(len(row) != len(table['columns']) for row in table['rows']):
                raise ValueError(f'Malformed table snapshot: {table["label"]}')
        return data
    source_path = Path(source_path)
    if hashlib.sha256(source_path.read_bytes()).hexdigest() != expected:
        raise ValueError('Private TeX does not match the frozen submitted-source hash')
    source = source_path.read_text()
    source = re.sub(r'(?<!\\)%[^\n]*', '', source)
    blocks = re.findall(r'\\begin\{table\*?\}.*?\\end\{table\*?\}', source, re.S)
    tables = []
    seen = set()
    for table_number, block in enumerate(blocks, 1):
        match = re.search(r'\\label\{tab:([^}]+)\}', block)
        if not match or match.group(1) not in SPECS:
            raise ValueError(f'Table {table_number}: unknown or missing table label')
        label = match.group(1)
        if label in seen:
            raise ValueError(f'Duplicate table label: {label}')
        seen.add(label)
        headers = SPECS[label]
        if label == 'related' and r'\textbf{Evaluated on}' in block:
            headers = ['work', 'selection', 'evaluated_on', 'question']
        data = block.split(r'\midrule', 1)[1].split(r'\bottomrule', 1)[0]
        rows, groups = [], []
        group = ''
        trigger = ''
        for line in data.splitlines():
            if r'\multicolumn' in line:
                group = line.strip()
                continue
            if '&' not in line or not line.strip().endswith('\\\\'):
                continue
            cells = [plain(x) for x in line.strip()[:-2].split('&')]
            if len(cells) != len(headers):
                raise ValueError(f'Table {table_number}: expected {len(headers)} cells, got {cells}')
            if label == 'triggers':
                trigger = cells[0] or trigger
                cells[0] = trigger
            rows.append(cells)
            groups.append(group)
        note = re.search(r'\\footnotesize (.*?)\\end\{minipage\}', block, re.S)
        tables.append({'number': table_number, 'label': 'tab:' + label,
                       'caption': re.search(r'\\caption\{([^}]*)\}', block).group(1),
                       'columns': headers, 'rows': rows, 'row_groups_tex': groups,
                       'note_tex': note.group(1).strip() if note else '',
                       'source_tex': block})
    if seen != set(SPECS):
        raise ValueError(f'Missing tables: {sorted(set(SPECS) - seen)}')
    return {'revision': 'noms2027-submission', 'kind': 'manuscript_transcription',
            'source': 'papers/http-session-noms/article.tex',
            'source_sha256': expected, 'tables': tables}


def outputs(source_path=None):
    data = extract(source_path)
    out = {'tables.json': json.dumps(data, indent=2, ensure_ascii=False) + '\n'}
    for table in data['tables']:
        buf = io.StringIO(newline='')
        writer = csv.writer(buf)
        writer.writerow(table['columns'])
        writer.writerows(table['rows'])
        out[f"table-{table['number']}.csv"] = buf.getvalue()
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--source', type=Path,
                        help='Compare with this private frozen TeX; it must match the recorded hash')
    args = parser.parse_args()
    if not args.check:
        DEST.mkdir(parents=True, exist_ok=True)
    bad = []
    for name, content in outputs(args.source).items():
        path = DEST / name
        if args.check:
            if not path.exists() or path.read_bytes() != content.encode():
                bad.append(name)
        else:
            path.write_bytes(content.encode())
    if bad:
        raise SystemExit('Stale table exports: ' + ', '.join(bad))
    basis = 'private frozen TeX' if args.source else 'committed table snapshot (full TeX withheld)'
    print('Eight tables: ' + ('exports match ' if args.check else 'exported from ') + basis)


if __name__ == '__main__':
    main()

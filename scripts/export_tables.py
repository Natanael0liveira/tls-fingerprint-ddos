#!/usr/bin/env python3
"""Export r53 tables faithfully; transcription is not experimental reproduction."""
import argparse
import csv
import hashlib
import io
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'papers/http-session-noms/article.tex'
DEST = ROOT / 'experiments/sprint-6-noms/results/r53'
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


def plain(s):
    s = re.sub(r'\$?\^\{[^}]*\}\$?', '', s) if not s.strip().startswith('$10^') else s
    s = re.sub(r'\\(?:textbf|textit|emph)\{([^{}]*)\}', r'\1', s)
    s = s.replace(r'\%', '%').replace(r'\,', '').replace(r'\ ', ' ')
    s = s.replace(r'\cup', 'union').replace(r'\Omega', 'Omega')
    return s.replace('$', '').replace('{=}', '=').strip()


def extract():
    source = SOURCE.read_text()
    source = re.sub(r'(?<!\\)%[^\n]*', '', source)
    blocks = re.findall(r'\\begin\{table\*?\}.*?\\end\{table\*?\}', source, re.S)
    tables = []
    for index, (label, headers) in enumerate(zip(LABELS, HEADERS), 1):
        block = next(b for b in blocks if '\\label{tab:' + label + '}' in b)
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
                raise ValueError(f'Table {index}: expected {len(headers)} cells, got {cells}')
            if label == 'triggers':
                trigger = cells[0] or trigger
                cells[0] = trigger
            rows.append(cells)
            groups.append(group)
        note = re.search(r'\\footnotesize (.*?)\\end\{minipage\}', block, re.S)
        tables.append({'number': index, 'label': 'tab:' + label,
                       'caption': re.search(r'\\caption\{([^}]*)\}', block).group(1),
                       'columns': headers, 'rows': rows, 'row_groups_tex': groups,
                       'note_tex': note.group(1).strip() if note else '',
                       'source_tex': block})
    return {'revision': 'r53', 'kind': 'manuscript_transcription',
            'source': str(SOURCE.relative_to(ROOT)),
            'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(), 'tables': tables}


def outputs():
    data = extract()
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
    args = parser.parse_args()
    DEST.mkdir(parents=True, exist_ok=True)
    bad = []
    for name, content in outputs().items():
        path = DEST / name
        if args.check:
            if not path.exists() or path.read_bytes() != content.encode():
                bad.append(name)
        else:
            path.write_bytes(content.encode())
    if bad:
        raise SystemExit('Stale table exports: ' + ', '.join(bad))
    print('Seven r53 tables: ' + ('exports match frozen TeX' if args.check else 'exported with notes and provenance'))


if __name__ == '__main__':
    main()

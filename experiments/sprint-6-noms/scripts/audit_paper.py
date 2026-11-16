#!/usr/bin/env python3
"""Check r53 numerical table cells against committed reductions, without raw data.

Checks Tables III, IV (primary timing rows), V (six registered configurations),
VI and VII. Additional post hoc aggregates come from the handoff.
This replaces the audit tied to the superseded manuscript; Git preserves it.
"""
import argparse
import csv
import json
import math
import statistics as st
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
R = ROOT / 'experiments/sprint-6-noms/results'
sys.path.insert(0, str(ROOT / 'scripts'))
from export_tables import extract


def audit():
    tables = {t['label']: t['rows'] for t in extract()['tables']}
    p = json.loads((R / 'production_tables.json').read_text())
    b = json.loads((R / 'production_tables_block.json').read_text())
    fb = json.loads((R / 'floor_bands.json').read_text())
    td, fd, bd = p['test_days'], p['fresh_day'], b['test_days']
    checks, failures = [], []

    def check(label, actual, expected):
        good = str(actual).replace('%', '') == str(expected)
        checks.append({'cell': label, 'printed': actual, 'computed': expected, 'ok': good})
        if not good:
            failures.append(checks[-1])

    def cells(table, i, offset, values):
        for j, val in enumerate(values, offset):
            check(f'{table} row {i+1} column {j+1}', tables[table][i][j], val)

    def pct(value, digits=1):
        return 'n/a' if value is None else f'{value*100:.{digits}f}'

    # III: median per-day floors; beta shared floors use exact beta-binomial tails.
    folds = sorted(next(iter(p['floor']['base'].values())))
    folds = [day for day in folds if day not in p['folds'].get('fresh', [])] if isinstance(p['folds'], dict) else folds
    # The held-out day is the last of the initial six evaluation folds.
    folds = folds[:5]
    def floor(run, endpoint, kind):
        return st.median(p['floor_deployed'][run][endpoint][d]['25'][kind]['min_attackers'] for d in folds)
    def exact(run, endpoint):
        return st.median(fb['per_endpoint'][endpoint][d][run]['bands']['ranks_11_plus']['beta_binomial'] for d in folds)
    for i, e in enumerate(['E1', 'E2', 'E3', 'E4']):
        n = st.median(p['floor']['base'][e][d]['median_origins'] for d in folds)
        levels = [round(math.log10(st.median(p['floor'][r][e][d]['level'] for d in folds))) for r in ['fleets', 'od']]
        values = [f'{n:,.0f}', *(f'10^{{{v}}}' for v in levels)]
        values += [f'{floor("fleets",e,k):.0f}/{floor("xfit_fleets",e,k):.0f}' for k in ['new', 'shared']]
        values += [f'{floor("od",e,"new"):.0f}/{floor("xfit_od",e,"new"):.0f}', f'{exact("od",e):.0f}/{exact("xfit_od",e):.0f}']
        cells('tab:floor', i, 1, values)

    # IV: three timing rows, two attacks, four metrics, independently recorded.
    timing = json.loads((R/'posthoc/e5_delay_modes.json').read_text())
    for i, mode in enumerate(['same', 'next', 'kept_next']):
        values = []
        for attack in ['attack 1', 'attack 2']:
            row = timing[attack][mode]
            values += [pct(row['requests']), pct(row['pairs']), pct(row['legit'],2), pct(row['edge_label_legit'],2)]
        cells('tab:real', i, 1, values)

    # V: E1-only arm has explicitly uncomputed pooled cells in the manuscript.
    configs = [('fleets','union|origins'), ('base','zcal|origins'), ('base','enrichment|omega'),
               ('fleets','unseen|none'), ('xfit_od','union|seasonal'), ('fleets','union|none')]
    for i, (run, key) in enumerate(configs):
        all_ = bd[run]['all'][key]
        e1 = bd[run]['per_endpoint']['E1'][key]
        maximum = max(bd[run]['per_endpoint'][e][key]['clean_rate'] for e in ['E2','E3','E4'])
        values = [pct(all_['clean_rate'],2), pct(e1['clean_rate'],2), pct(maximum,2),
                  pct(all_['clean_collateral_median']), pct(all_['flash1000']),
                  pct(e1['new:x0.1']['blocked']), pct(e1['shared:x0.1']['blocked']),
                  pct(all_['new:A100']['blocked']), pct(all_['shared:A100']['blocked'])]
        if i == 5:
            for col in [2,6,7]:
                check(f'tab:block row 6 column {col+1}',tables['tab:block'][i][col],values[col-1])
        else:
            cells('tab:block', i, 1, values)

    # VI: generated scopes, all six scenarios and all six metrics.
    with (R/'unseen_synth_summary.csv').open() as f:
        u = list(csv.DictReader(f))
    def value(mode, stacks, adv, method, metric):
        rows = [r for r in u if r['mode']==mode and float(r['alpha'])==1.5 and int(r['stacks'])==stacks and int(r['adv'])==adv and r['method']==method]
        if len(rows)!=1:
            raise ValueError((mode, stacks, adv, method, len(rows)))
        return float(rows[0][metric])
    for i, (mode,m,adv) in enumerate([('original',1,0),('original',5,0),('original',25,0),('original',100,0),('shared_profile_tail',25,0),('original',25,1)]):
        values=[pct(value(mode,m,adv,'enrichment','recall')),pct(value(mode,m,adv,'enrichment','fpr'),2),f"{value(mode,m,adv,'enrichment','f1'):.3f}"]
        values += [pct(value(mode,m,adv,method,'recall')) for method in ['modal','zscore','unseen']]
        cells('tab:symbolic',i,1,values)

    # VII: populations and periods follow the table note, including novelty unions.
    for i, (gate,run,scope) in enumerate((g,r,s) for g in ['origins','seasonal','none'] for r,s in [('fleets','union'),('xfit_od','union'),('fleets','unseen')]):
        key=f'{scope}|{gate}'
        t1=td[run]['per_endpoint']['E1'][key]; f1=fd[run]['per_endpoint']['E1'][key]
        rates=[t1['clean_rate'],f1['clean_rate']]+[max(period[run]['per_endpoint'][e][key]['clean_rate'] for e in ['E2','E3','E4']) for period in [td,fd]]
        values=[pct(v,2) for v in rates]+[pct(t1['new:x0.1']['blocked']),pct(f1['new:x0.1']['blocked']),pct(t1['shared:x0.1']['blocked']),pct(td[run]['all'][key]['flash1000']),pct(td[run]['all'][key]['clean_collateral_median'])]
        cells('tab:triggers',i,2,values)

    return {'revision':'r53','checked_cells':len(checks),'mismatches':failures,
            'coverage':['Table III: all numerical cells','Table IV: 24 primary timing cells from handoff aggregates','Table V: numeric cells of the six pre-registered rows','Table VI: all numerical cells','Table VII: all numerical cells'],
            'gaps':['Table IV: alternative configuration rows and clean-day FA not independently audited here','Table V: two-path row and E1-only footnote not independently audited here','Prose and descriptive Tables I/II are not experimental numeric checks; additional post hoc aggregates are available separately'],
            'checks':checks}


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--out',type=Path);args=ap.parse_args()
    result=audit()
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(json.dumps(result,indent=2)+'\n')
    print(f"r53: {result['checked_cells']} numerical cells checked; {len(result['mismatches'])} mismatches")
    for failure in result['mismatches']: print(failure)
    for gap in result['gaps']: print('Not audited:',gap)
    raise SystemExit(bool(result['mismatches']))

if __name__=='__main__': main()

# Tables and source map (r53)

The [machine-readable export](../experiments/sprint-6-noms/results/r53/tables.json)
contains all seven tables, original LaTeX, notes, row groups and the source hash.
Individual CSVs have explicit column names. Blank, `--` and `n/a` retain their
distinct meanings. Exporting TeX is transcription; the separate audit compares
numerical cells against recorded experimental reductions.

| Table | Content | Numerical source / provenance |
|---|---|---|
| [I](../experiments/sprint-6-noms/results/r53/table-1.csv) | Related approaches | Manuscript and bibliography |
| [II](../experiments/sprint-6-noms/results/r53/table-2.csv) | Configurations and chronology | Manuscript; frozen protocols in `results/` |
| [III](../experiments/sprint-6-noms/results/r53/table-3.csv) | Floors, in sample / cross-fitted | `production_tables.json`, `floor_bands.json` |
| [IV](../experiments/sprint-6-noms/results/r53/table-4.csv) | E5 timing and configurations | `posthoc/e5_delay_modes.json` supports the 24 primary timing cells; remaining rows retained from TeX |
| [V](../experiments/sprint-6-noms/results/r53/table-5.csv) | Prospective results | `production_tables_block.json`; two-path computation in `scripts/posthoc/regra_uniao.py` |
| [VI](../experiments/sprint-6-noms/results/r53/table-6.csv) | Generated scopes | `unseen_synth_summary.csv`, `symbolic_detector.json` |
| [VII](../experiments/sprint-6-noms/results/r53/table-7.csv) | Scopes by trigger | `production_tables.json`, separate `test_days` and `fresh_day` sections |

Result paths above are relative to `experiments/sprint-6-noms/results/`.
The [audit report](../experiments/sprint-6-noms/results/r53/audit.json) lists every
checked cell and its coverage limits. See [metrics](metrics.md) for denominators.

The two figures are frozen in `papers/http-session-noms/figures/`. Fig. 1 is the
pipeline diagram; Fig. 2 uses `production_tables.json` to compare coverage with
and without the trigger. Historical filename `fig6_stops.png` now represents Fig. 2.

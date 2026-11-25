# NOMS 2027 evaluation

This directory contains the evaluation code and saved reductions supporting the
[submitted manuscript](../../papers/http-session-noms/article.tex), recorded by
tag `noms2027-submitted`. The paper has two figures, eight tables and one appendix.
Its [table guide](../../docs/tables.md) defines each population and denominator.

## Start here

From the repository root:

```sh
make check
```

This checks the submission package, eight current table exports and 217 numerical
cells against saved reductions. It needs Python 3.9+ and Make, without private
traffic or the experimental Python environment. To refresh the current table
transcriptions and audit record, use `make tables`.

The [experimental environment](../README.md#python-environment) is needed for
analyses using NumPy, SciPy and pandas. With that environment, run the synthetic
sustained-botnet regression checks from the root with `make test`.

## Submitted results and their inputs

Paths in this table are relative to this directory. The manuscript exports are
transcriptions; the audit independently checks the supported numerical cells.

| Paper element | Saved input or record |
|---|---|
| Tables I–II: related work and configurations | Manuscript, bibliography and original protocol records |
| Table III: prospective overview | `results/production_tables_block.json`, fallback aggregates and exploratory cap results |
| Table IV: calibration floors | `results/production_tables.json`, `results/floor_bands.json` |
| Table V: prospective configurations | `results/production_tables_block.json`; two-path analysis in `scripts/posthoc/regra_uniao.py` |
| Table VI: real attacks | `results/posthoc/e5_delay_modes.json` supports 24 primary timing cells; other rows remain transcriptions |
| Table VII: generated scopes | `results/symbolic_detector.json`, `results/unseen_synth_summary.csv` |
| Table VIII: scope and trigger variants | `results/production_tables.json`, development and held-out sections |
| Figure 1: filtering pipeline | Manuscript figure source; see the [figure guide](../../docs/figures.md) |
| Figure 2: coverage and the trigger | `results/production_tables.json`; see the [figure guide](../../docs/figures.md) |
| Persistent filters, fallback and joint failures | `results/posthoc/`; scripts and provenance described in the [post hoc guide](scripts/posthoc/README.md) |
| Current table exports and audit | [results/manuscript/](results/manuscript/README.md) |

The audit does not independently verify every E5 alternative row, the two-path
row, all overview cells or all prose statistics. Its [record](results/manuscript/audit.json)
and the [submission verification](../../submissions/noms2027/verification.json)
state the checked cells and remaining gaps.

## Reproduction paths

The [reproduction guide](../../docs/reproduction.md) separates these operations:

| Operation | Inputs required | Entry point |
|---|---|---|
| Integrity, table transcription and supported numerical checks | Committed files | `make check` from the root |
| Prospective report from reductions | Committed reductions and experimental Python environment | `scripts/block_report.py`; exact command in the reproduction guide |
| Generated-scope experiments | Scenario caches and generator distributions | `symbolic`, `unseen-synth` targets |
| Operator-endpoint evaluation and reductions | Restricted exports and endpoint mapping | `rule-production*`, `production-tables*` targets |
| E5 and other exploratory replays | Restricted per-window inputs; saved aggregate outputs are public | [scripts/posthoc/](scripts/posthoc/README.md) |

From this directory, `make help` lists the historical execution targets. Its
`PY` variable defaults to `../.venv/bin/python`. The [methodology guide](../METHODOLOGY.md)
explains `DATA`, `REALWORK`, `RULEWORK`, `PRODDATA` and `BLOCKDATA`.
The `clean` target deletes saved result JSONs and CSVs; it is not part of the
reproduction instructions above.

## Protocols and implementation history

The original `results/fresh_day*.md` and `results/heldout_block*.md` records retain
the published protocol, amendments and chronology. They should be read alongside
the [evaluation design](../../docs/evaluation.md).

Earlier graph, STIX, classifier and latency experiments remain available as
supporting implementation history. Their old appendix and figure numbers do not
identify elements of the submitted manuscript. The
[archived notebook](../../archive/development/noms-evaluation-notebook.md)
records those experiments and draft review rounds.

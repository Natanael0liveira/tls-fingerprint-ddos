# Reproduction and data availability

## Available without operator data

- Frozen r53 TeX, bibliography, figures and PDF, with checksums.
- All seven tables and their notes exported from TeX under `experiments/sprint-6-noms/results/r53/`. These are manuscript transcriptions.
- Generated-campaign summaries and operator endpoint aggregate reductions: `symbolic_detector.json`, `unseen_synth_summary.csv`, `production_tables.json`, `production_tables_block.json`, and related original files.
- The audit independently compares supported table cells with those reductions; see its output for checked cells and omissions.
- Figure regeneration from the committed reduction, with pinned NumPy/Matplotlib versions.

```sh
python3 scripts/check_release.py
python3 scripts/export_tables.py --check
python3 experiments/sprint-6-noms/scripts/audit_paper.py
```

## Recompute the prospective report

Using the experimental environment with SciPy installed:

```sh
cd experiments/sprint-6-noms
../../experiments/.venv/bin/python scripts/block_report.py --tables results/production_tables_block.json --churn results/ja4_churn_block.json --out /tmp/noms-block-report.json
```

The tracked `block_report.json` was regenerated from the prospective inputs and matches the existing file exactly. Its `test_days` section denotes the 14 test days in `production_tables_block.json`; it does not denote the earlier development period.

## Restricted inputs and audit limits

Raw production exports, addresses and customer identifiers are not distributed. Original Makefile targets require the operator data drive (`PRODDATA`/`BLOCKDATA`) or generated scenario caches. Full dependencies are in `experiments/requirements.txt`; Python 3.11 was used by the existing environment.

The handoff supplied E5 timing aggregates, persistent-filter replay results, per-endpoint fallback results, history-baseline comparisons and stratified independence outputs. They are published under `experiments/sprint-6-noms/results/posthoc/`, with provenance hashes. Corresponding analysis scripts are in `scripts/posthoc/` within that experiment directory. Absolute workstation paths were replaced by environment variables; E5 input dates and selected fingerprint identifiers were excluded from the public outputs.

The audit checks 217 numeric cells, including 24 E5 primary timing cells. It does not independently check every E5 alternative-configuration/FA cell, the two-path row, the E1-only footnote or every prose statistic. Recomputing these analyses from per-window records still requires restricted inputs. The E5 replay accepts a private manifest rather than publishing dates or identifiers. See the [post hoc guide](../experiments/sprint-6-noms/scripts/posthoc/README.md).

For the ordinary checks no third-party Python packages are required. Figure regeneration was byte-identical to the supplied PNGs. A local LaTeX build produced 11 pages without warnings; extracted text differed only in two summation-symbol Unicode mappings between PDF engines. The committed reference PDF remains the supplied r53.

No new experiments were run during the repository update. Source checks, reduction checks, figure regeneration and compilation are distinct from rerunning the evaluation.

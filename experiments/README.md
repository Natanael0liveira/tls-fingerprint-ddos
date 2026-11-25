# Experiments for the submitted manuscript

The evaluation is in [sprint-6-noms/](sprint-6-noms/README.md). Its two figures and
eight table snapshots remain public; [the table guide](../docs/tables.md) maps
each table to its saved results. The complete manuscript is kept in a separate
local freeze identified by the [artifact record](../submissions/noms2027/verification.json).

- [Findings](FINDINGS.md): coverage, false alarms, collateral and limitations.
- [Methodology](METHODOLOGY.md): evaluation periods, generated campaigns and inputs.
- [Reproduction and availability](../docs/reproduction.md): which checks need restricted data.
- [Implementation map](../docs/runtime.md): scripts and their roles.

## Checks without operator data

Run from the repository root:

```sh
make check
```

This needs Python 3.9+ and Make. It checks public artifact hashes, eight table
snapshots and 217 numerical cells against committed reductions.
The audit reports its coverage gaps. It does not rerun the production evaluation.

`make tables` regenerates CSVs and the audit record from the public table snapshot
under `sprint-6-noms/results/manuscript/`. [Metrics](../docs/metrics.md) explains their
denominators and the distinction between blocked and challenged origins.

## Python environment

The experimental scripts use Python 3.11 and the dependencies in
[requirements.txt](requirements.txt). From the repository root:

```sh
python3.11 -m venv experiments/.venv
experiments/.venv/bin/python -m pip install -r experiments/requirements.txt
```

The synthetic sustained-botnet regression checks then run with:

```sh
make test
```

Figure regeneration has its own [requirements file](requirements-figures.txt):

```sh
experiments/.venv/bin/python -m pip install -r experiments/requirements-figures.txt
experiments/.venv/bin/python scripts/regenerate_figures.py --out build/figures
```

See the [figure guide](../docs/figures.md) for the two diagrams. Earlier laboratory
experiments additionally use tools such as tshark, Docker and Java; these are not
required for the submitted manuscript's checks above.

## Code and data layout

| Directory | Role |
|---|---|
| [sprint-6-noms/](sprint-6-noms/README.md) | Generated-scope and production evaluation, prospective report, post hoc checks and saved reductions |
| [sprint-2/](sprint-2/README.md) | Generator and committed client distributions reused by the evaluation |
| [pillar4-evidence-mitigation/](pillar4-evidence-mitigation/README.md) | Scope and calibration implementation imported by the evaluation |
| `common/`, `../ontology/` | Shared implementation and reference-rule vocabulary |
| `sprint-1/` through `sprint-5/`, `pillar2-symbolic-reasoning/` | Earlier laboratory experiments and supporting modules; their READMEs describe those earlier stages |
| [sprint-6-noms/results/manuscript/](sprint-6-noms/results/manuscript/README.md) | Current eight-table transcription and source-bound numerical audit |
| `sprint-6-noms/results/posthoc/` | Anonymized post hoc aggregates and provenance |

Raw production exports, customer identifiers and large scenario caches are not
distributed. See [.env.example](.env.example) for data-drive configuration and
[methodology](METHODOLOGY.md#scenario-caches) for cache paths. Existing module
paths are retained because scripts import across experiment directories.

The [development archive](../archive/development/README.md) preserves the earlier
infrastructure guide and lab notebook. It is not the guide to the submitted paper.

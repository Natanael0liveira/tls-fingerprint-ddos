# NOMS 2027 manuscript

**An Empirical Evaluation of TLS Fingerprint-Based Filtering for Application-Layer DDoS**

This directory contains the canonical [article.tex](article.tex), [references.bib](references.bib) and two figures. The [submission package](../../submissions/noms2027/README.md) contains the synchronized delivery; its [verification record](../../submissions/noms2027/verification.json) identifies the exact source and PDF.

Tag `noms2027-submitted` records the submitted source, identified on 24 November 2026. Its synchronized copy is byte-identical. The local PDF was rebuilt from this source; it has not been compared with the PDF uploaded to the submission system.

The verified PDF has 11 pages. Main text, conclusion, acknowledgment, AI disclosure and reproducibility end on page 8; references begin on page 8 and the appendix ends on page 11. Results open with a three-policy overview of the prospective period, followed by selection mechanisms, trigger effects, variants and exploratory checks, and the real-attack replay.

## Build

```sh
pdflatex -interaction=nonstopmode -halt-on-error article
bibtex article
pdflatex -interaction=nonstopmode -halt-on-error article
pdflatex -interaction=nonstopmode -halt-on-error article
```

Run from this directory. PDF hashes can vary with build metadata. A newly built PDF must be checked before its verification record is updated.

## Checks and delivery

From the repository root:

```sh
make check
make tables
make submission
```

`make check` verifies the delivery and archive, the current table exports and 217 numerical cells against saved results. `make tables` refreshes transcriptions and the audit record. `make submission` copies this verified source, bibliography, dependencies and PDF into the delivery and regenerates its diff and checksums. It rejects inputs that differ from the recorded verification; it does not certify a new manuscript automatically.

For Overleaf, upload the complete `submissions/noms2027/latex/` directory, including its bibliography and figures.

## Figures and experimental limits

The [figure guide](../../docs/figures.md) explains both diagrams; the [table guide](../../docs/tables.md) covers all eight current tables and their populations. To regenerate figures without changing the manuscript inputs:

```sh
python3 scripts/regenerate_figures.py --out build/figures
```

Run that command from the repository root after installing `experiments/requirements-figures.txt`. The scripts retain their historical filenames; only the two current figures are generated.

Sustained-botnet results describe the original per-window fingerprint resampling, not a validated fixed-assignment rerun. The corrected replay defaults to fixed per-bot fingerprints and requires private exports for a production rerun. Its synthetic regression tests do not establish new production numbers. See the [post hoc guide](../../experiments/sprint-6-noms/scripts/posthoc/README.md).

Earlier snapshots and development notes are indexed in the [historical archive](../../archive/README.md). E5 remains anonymized in public artifacts.

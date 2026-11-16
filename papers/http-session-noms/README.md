# Frozen NOMS 2027 manuscript: r53

**An Empirical Evaluation of TLS Fingerprint-Based Filtering for Application-Layer DDoS**

The source, bibliography, two PNGs and figure scripts were copied byte for byte from `entrega-NOMS2027-r53`. [freeze.json](freeze.json) records their SHA-256 hashes. The reference [PDF](NOMS2027-r53.pdf) has SHA-256 `77c2029a9d4b9b3ee8c0599d7804cea81412cb94cf54b0ede6564e8ec1efb534`.

## Build

```sh
pdflatex -interaction=nonstopmode -halt-on-error article
bibtex article
pdflatex -interaction=nonstopmode -halt-on-error article
pdflatex -interaction=nonstopmode -halt-on-error article
```

Expected: 11 pages; main text, acknowledgment and reproducibility through page 8; references start on page 9. PDF hashes vary with build metadata; compare extracted text with the reference PDF. The repository URL inside the frozen source intentionally retains its original spelling.

## Regenerate figures

From the repository root, install `experiments/requirements-figures.txt`, then:

```sh
python3 scripts/regenerate_figures.py --out build/figures
```

Fig. 1 comes from `figures/fig1_r48.py`; Fig. 2 from `fig_stops` in `figures/make_figures_en.r13.py`, reading `experiments/sprint-6-noms/results/production_tables.json`. The original figure script contains older unused functions; the wrapper runs only the two figures used by r53.

Run `python3 scripts/check_release.py` from the root to verify the freeze. Table exports preserve all seven tables and their notes. Public artifacts identify the customer only as E5.

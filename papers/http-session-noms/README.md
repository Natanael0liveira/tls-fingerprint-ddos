# NOMS 2027 supporting material

**An Empirical Evaluation of TLS Fingerprint-Based Filtering for Application-Layer DDoS**

This directory distributes the [bibliography](references.bib) and
[two figures](figures/README.md) supporting the submitted study. The complete
manuscript source, PDF and LaTeX build dependencies have been moved to an ignored
local freeze. The [artifact metadata](../../submissions/noms2027/verification.json)
records the submitted-source and locally rebuilt PDF hashes.

## Figures

The [figure guide](../../docs/figures.md) explains both diagrams; the
[table guide](../../docs/tables.md) covers all eight table snapshots.
To regenerate figures in a separate directory, install
`experiments/requirements-figures.txt` and run from the repository root:

```sh
python3 scripts/regenerate_figures.py --out build/figures
```

The original PNGs remain available for comparison. Historical generator filenames
are retained; only the two submitted figures are generated.

## Frozen manuscript

The separate local snapshot is under
`archive/local/submitted/noms2027-2026-11-24/`. It includes `paper/`, `submission/`,
the earlier complete snapshot, checksum manifests and a self-contained Git bundle.
It is ignored by Git and is not part of a public checkout. Its README describes
verification and restoration; changes should start from a separate working copy.

Run `make check` for public artifact checks. Full manuscript verification requires
the local freeze; see the [reproduction guide](../../docs/reproduction.md).
The PDF in that freeze was rebuilt locally and was not compared with the uploaded
submission binary. E5 outputs remain anonymized.

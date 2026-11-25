# NOMS 2027 artifact and submission record

**An Empirical Evaluation of TLS Fingerprint-Based Filtering for Application-Layer DDoS**

This directory publishes [submission hashes and verification scope](verification.json),
not the complete manuscript or upload project. The authors have chosen to keep
those files in a separate local freeze. The public artifact retains code, figures,
bibliography, table transcriptions and anonymized reductions.

The submitted-source SHA-256 is:

```text
faea129198a1a0cd1907536a8e13ac6548305837c89a166d8073755ecd16dbdc
```

The local rebuilt PDF hash is also recorded. That binary was not compared with
the PDF uploaded to the submission system.

## Public checks

Run from the repository root:

```sh
make check
```

This checks public artifact hashes, eight table snapshots and 217 numerical cells
against saved reductions. Public checks do not require the full TeX or PDF and
do not rerun restricted operator data. The [table guide](../../docs/tables.md)
and [reproduction guide](../../docs/reproduction.md) describe the coverage gaps.
The cap figures and every prose statistic are not independently audited by those
217 checks. Table transcriptions retain their table-specific LaTeX blocks;
they do not contain the full manuscript.

`make artifact` refreshes [SHA256SUMS](SHA256SUMS) for the public files without
copying a manuscript. The historical `make submission` target is an alias for
this public-artifact operation. To check those hashes directly, run from the root:

```sh
shasum -a 256 -c submissions/noms2027/SHA256SUMS
```

## Private frozen copy

The local snapshot lives at `archive/local/submitted/noms2027-2026-11-24/` and is
ignored by Git. It includes the exact submitted TeX, figures, bibliography,
build dependencies, a locally rebuilt PDF, the original verification report and
`noms2027-submitted.bundle`. Its own checksum manifests cover all frozen files.
No frozen source text was edited during removal from the current tree.

Full-source checks, when that snapshot is available:

```sh
python3 scripts/check_release.py --private archive/local/submitted/noms2027-2026-11-24
python3 scripts/export_tables.py --check --source archive/local/submitted/noms2027-2026-11-24/paper/article.tex
```

The historical tag `noms2027-submitted` and earlier commits still contain the
manuscript. Removing current files does not remove that history or copies already
published. This change does not make those earlier versions private.

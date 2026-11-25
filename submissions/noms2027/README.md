# NOMS 2027 submitted source package

**An Empirical Evaluation of TLS Fingerprint-Based Filtering for Application-Layer DDoS**

Tag `noms2027-submitted` records the submitted source. `latex/article.tex` is
byte-identical to the canonical source in `papers/http-session-noms/`.
The local PDF was rebuilt from that source and verified on 24 November 2026;
it has not been compared with the PDF uploaded to the submission system.
Current PDFs are local build products and may be absent in a public checkout.

## Package contents

| Path | Contents |
|---|---|
| `article.pdf` | Locally rebuilt PDF, when present |
| [latex/article.tex](latex/article.tex) | Complete manuscript source |
| [latex/references.bib](latex/references.bib) | Bibliography used by the submitted source |
| `latex/IEEEtran.cls`, `IEEEtran.bst`, `stfloats.sty` | Local build dependencies |
| `latex/figures/` | The two figures used by the paper |
| `figure-sources/` | Figure-generation scripts |
| [verification.json](verification.json) | Source/PDF hashes, checks performed and their limits |
| [SHA256SUMS](SHA256SUMS) | Package checksum manifest |

## Build

Upload the complete `latex/` directory to Overleaf, with `article.tex` as the main
document. To build locally, run from this package directory:

```sh
cd latex
pdflatex -interaction=nonstopmode -halt-on-error article
bibtex article
pdflatex -interaction=nonstopmode -halt-on-error article
pdflatex -interaction=nonstopmode -halt-on-error article
```

The verified local build has 11 pages. Main text, conclusion, acknowledgment,
AI disclosure and reproducibility end on page 8; references begin there and the
appendix ends on page 11. It has no overfull boxes or undefined references or
citations. PDF hashes can change with build metadata.

## Checks and interpretation

Run `make check` from the repository root to verify source/package integrity,
eight table transcriptions and 217 numerical cells against saved reductions.
The audit reports its gaps. Six overview values were checked separately; cap
figures and every prose statistic are not independently audited by those checks.
No check reruns restricted operator data.

The [table guide](../../docs/tables.md), [figure guide](../../docs/figures.md) and
[evaluation design](../../docs/evaluation.md) explain the reported populations
and separate pre-registered comparisons from exploratory analyses.
The [reproduction guide](../../docs/reproduction.md) describes available inputs.
The sustained-botnet estimates use the original per-window fingerprint resampling;
there is no validated fixed-assignment production rerun here.

## Maintaining the package

Canonical inputs live in `papers/http-session-noms/`. After a changed manuscript
has been rebuilt and its own verification recorded, `make submission` synchronizes
this package and regenerates its checksums. It refuses inputs that differ from
the recorded source, bibliography or PDF. Preserve `noms2027-submitted` as the
record of the submitted version.

The optional [historical source diff](changes-from-r53.diff) compares this source
with an earlier internal draft. Earlier snapshots and their identifiers are
explained in the [archive index](../../archive/README.md); they are not the
submitted version. Public E5 outputs remain anonymized.

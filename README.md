# TLS Fingerprint DDoS Filtering

Research artifact for **An Empirical Evaluation of TLS Fingerprint-Based Filtering for Application-Layer DDoS**, submitted to IEEE/IFIP NOMS 2027. The author identified the current canonical TeX as the final submitted version on **24 November 2026**. A local rebuild was verified on that date: 11 pages, with the main text through page 8.

- [Current manuscript and build instructions](papers/http-session-noms/README.md)
- [Submission package](submissions/noms2027/README.md), [LaTeX](submissions/noms2027/latex/article.tex), [verification record](submissions/noms2027/verification.json)
- [Glossary and configurations](docs/concepts.md), [metrics](docs/metrics.md), [study design](docs/evaluation.md)
- [Figures explained](docs/figures.md), [tables and provenance](docs/tables.md)
- [Reproduction and data availability](docs/reproduction.md)
- [Frozen r53 baseline](archive/noms2027/r53/README.md)

## What was evaluated

Per endpoint and five-minute window, a volume trigger decides whether to act. The scope selects TLS fingerprints over-represented relative to that endpoint's profile or absent from it. The primary configuration combines the binomial test and novelty rule, with known fleets exempted. If the trigger fires without selecting a fingerprint, a fallback challenges or rate-limits every client.

The data span 23 days at four operator endpoints: 3 initial calibration days, 5 development days, 1 held-out day and 14 prospective evaluation days. Botnets are injected into the 20 evaluation days. Two real attacks at a customer's site (E5) are examined separately, post hoc.

## Main findings

- Over the 14 prospective days, the primary configuration raises 31 false alarms in 16,103 clean windows (0.19%). Its median collateral per false alarm is 39.0%. Low alarm frequency does not establish low damage in affected windows.
- On the busiest endpoint, coverage of about 300 bots on new fingerprints is 2.9% with the trigger and 89.6% without it. Legitimate fleets and common fingerprints also limit selectivity.
- The fallback challenges or rate-limits 0.6% of clean origin-windows prospectively, compared with 0.016% blocked by the filters. Blocking and challenging are distinct actions.
- In exploratory replays at E5, filters applied one window late remove about 36% of each attack's requests, with at most 1.6% legitimate-origin collateral under two attacker labelings. The CDN had already rate-limited the attacks; service protection was not measured.
- Ungated novelty exceeds the false-alarm budget at E5 (8.94%). The results support validation at each endpoint rather than a default deployment policy.

## Repository layout

| Path | Purpose |
|---|---|
| `papers/http-session-noms/` | Canonical manuscript, bibliography and figures; edit here |
| `submissions/noms2027/` | Self-contained delivery, verified PDF, checksums and source comparison |
| `archive/noms2027/r53/` | Frozen r53 snapshot and its original checksums |
| `archive/local/` | Ignored local history, reviews and original handoffs |
| `docs/` | Current definitions, figure/table guides and reproduction instructions |
| `experiments/sprint-6-noms/` | Evaluation code and saved aggregate results |
| `experiments/sprint-6-noms/results/manuscript/` | Exports and numerical audit of the current manuscript |
| `experiments/sprint-6-noms/results/r53/` | Historical r53 exports, retained unchanged |
| `experiments/sprint-1/` through `sprint-5/`, `common/`, `pillar*/` | Experiment infrastructure and dependencies still imported by the evaluation |
| `ontology/` | Vocabulary read by the reference implementation |

Current PDFs and upload bundles are local build products. Source files, verification records and checksums are versioned. Historical experiment paths remain stable so imports and reproduction commands continue to work.

## Quick checks

```sh
make check
```

This verifies the frozen r53 archive, delivery/source synchronization, eight table exports and 217 independently checked numerical cells. See the audit output for its coverage and gaps. These checks need only Python 3.9+ and Make; CI uses Python 3.11.

To regenerate current table transcriptions and their audit record, run `make tables`. To refresh the delivery from the already verified source and PDF, run `make submission`. Packaging refuses to reuse a verification record for a different source, bibliography or PDF.

The sustained-botnet regression checks require the experimental environment:

```sh
make test
```

The manuscript's persistence estimates use the original model, which redraws bot fingerprints every window from a fixed daily pool. The corrected script defaults to fixed assignments, but no production rerun of that model was performed here. See the [post hoc guide](experiments/sprint-6-noms/scripts/posthoc/README.md).

For figure regeneration install `experiments/requirements-figures.txt`; full experimental dependencies are in `experiments/requirements.txt`. Raw operator data are restricted. Transcribing a manuscript value or checking a saved reduction does not rerun the underlying experiment.

MIT licensed, subject to [NOTICE](NOTICE).

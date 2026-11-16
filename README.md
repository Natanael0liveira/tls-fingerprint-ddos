# TLS Fingerprint DDoS Filtering

Research artifact for **An Empirical Evaluation of TLS Fingerprint-Based Filtering for Application-Layer DDoS**, prepared for IEEE/IFIP NOMS 2027. The manuscript is frozen at **r53, 16 November 2026**, with 11 pages (8 pages of main text).

- [Frozen paper](papers/http-session-noms/NOMS2027-r53.pdf), [LaTeX](papers/http-session-noms/article.tex), [checksums](papers/http-session-noms/freeze.json)
- [Glossary and configurations](docs/concepts.md)
- [Figures explained](docs/figures.md), [tables explained and provenance](docs/tables.md)
- [Metrics](docs/metrics.md), [study design](docs/evaluation.md)
- [Findings and limitations](experiments/FINDINGS.md)
- [Reproduction and availability](docs/reproduction.md)

## What was evaluated

Per endpoint and five-minute window, a volume trigger decides whether to act. The scope selects TLS fingerprints over-represented relative to that endpoint's profile or absent from it. The primary configuration combines the binomial test and novelty rule, with known fleets exempted. A separate, exploratory two-path rule also applies novelty filtering without the volume trigger.

The data span 23 days at four operator endpoints: 3 initial calibration days, 5 development days, 1 held-out day and 14 prospective evaluation days. Botnets are injected into the 20 evaluation days. Two real attacks at a customer's site (E5) are examined separately, post hoc.

## Main findings

- On generated botnets using 5–25 new TLS stacks, profile-based selection covers about 90% of attackers. At 100 stacks, the binomial test covers 38.6%; adversarial fingerprints reduce coverage to 30.4% with 3.78% collateral.
- Over the 14 prospective days, the primary configuration raises 31 false alarms in 16,103 clean windows (0.19%). Its median collateral per false alarm is 39.0%. Remaining within the 1% budget does not establish a stable false-alarm rate.
- On the busiest endpoint, coverage of about 300 bots on new fingerprints is 2.9% with the trigger and 89.6% without it. Common fingerprints and legitimate fleets limit selectivity.
- In counterfactual replays at E5, filters applied one window late remove about 36% of each attack's requests. Collateral is below 0.1% under the main attacker labels and up to 1.6% under alternative labels. The CDN had already rate-limited these attacks; this is not a comparison of WAF effectiveness.
- The ungated novelty rule exceeds the budget at E5 (8.94%). The two-path rule requires prospective validation across sites.

## Repository layout

| Path | Purpose |
|---|---|
| `papers/http-session-noms/` | Frozen r53 source, PDF and two figures |
| `docs/` | Current definitions, metrics, figure and table reading guides, and reproduction guide |
| `experiments/sprint-6-noms/` | Evaluation scripts and committed aggregate results |
| `experiments/sprint-1/` through `sprint-5/`, `common/`, `pillar*/` | Earlier experiment infrastructure, including dependencies still imported by the evaluation |
| `ontology/` | Vocabulary read by the reference implementation |

Earlier manuscripts, the outdated translation and unused manuscript figures have been removed from the current tree; Git history preserves them. Earlier experiment directories remain because deleting them would break imports and reproduction. Their historical reports do not override r53.

## Quick checks

```sh
python3 scripts/check_release.py
python3 scripts/export_tables.py --check
python3 experiments/sprint-6-noms/scripts/audit_paper.py
```

The audit compares the current tables with the committed aggregate results and reports its coverage and gaps. Transcribing a value from the manuscript is not an independent experimental reproduction. Post hoc scripts and anonymized results recovered from the handoff are also included. Raw operator data are not public; see [availability](docs/reproduction.md).

For figure regeneration install `experiments/requirements-figures.txt`. Full experimental dependencies remain in `experiments/requirements.txt`. Build instructions are in the [paper README](papers/http-session-noms/README.md).

MIT licensed, subject to [NOTICE](NOTICE). The frozen paper cites the original repository name `knowledge-graph-ddos-article`; its source is preserved byte for byte.

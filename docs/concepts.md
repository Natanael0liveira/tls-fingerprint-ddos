# Glossary and configuration map

| Term | Meaning in the paper |
|---|---|
| Endpoint | One service/target whose normal traffic profile is learned separately |
| Origin | An address–TLS-fingerprint pair, not a device and not a CDN origin server |
| Origin-window | One occurrence of an origin in one five-minute window |
| TLS fingerprint / JA4 | A client TLS signature that multiple legitimate clients and bots may share |
| Stack | A TLS implementation/library represented by a shared fingerprint in the generated campaign |
| Profile | Fingerprint frequencies in preceding traffic used for calibration |
| Trigger | Decision whether the window should activate mitigation |
| Scope | Procedure selecting which fingerprints a filter matches |
| Novelty rule | Selects fingerprints absent from the endpoint profile once at least five origins present them |
| New / shared | Attack fingerprints absent from / present in the endpoint's profile |
| Known fleets | Recurring legitimate concentrations exempted in the primary configuration |
| Calibration level λe | Endpoint-specific test-score cutoff; extremely small binomial tails are scores, not reliable literal probabilities |
| Floor | Botnet size needed for the scope alone to select a typical stack; not a hard threshold or full-botnet guarantee |
| In sample / cross-fitted | Calibration against the pooled history / profiles formed without the calibration day being scored |
| Fallback | Challenge or rate limit every client when the trigger fires but no fingerprint is selected |
| Ω | Earlier volume-dominated trigger retained for the base rule |

## Table II configurations

| Configuration | Trigger | Scope | Fleets |
|---|---|---|---|
| Primary | Origin count | Binomial union novelty | Exempt |
| z-score | Origin count | Calibrated z-score | No exemption |
| Base rule | Ω | Binomial | No exemption |
| Novelty rule | None | Novelty | No exemption |
| Beta-binomial arm | Seasonal | Cross-fitted beta-binomial union novelty | No exemption |
| No-trigger arm | None, E1 only | Binomial union novelty | Exempt |
| Two-path rule | None for novelty; origin count for binomial | Novelty plus gated binomial | As specified in Table II |

The first six configurations were fixed for the prospective evaluation. The two-path rule was derived post hoc and fixed before E5 was examined. The held-out-day protocol fixed only the primary and base rule. Table VIII's binomial and beta-binomial scopes include novelty; Table VII evaluates scopes alone on generated traffic.

Code identifiers predate the final terminology: `unseen` means novelty, `union` means test union novelty, `fleets` is the run with fleet exemption, and `xfit_od` is the cross-fitted beta-binomial run. `fresh_day` denotes the held-out day. These identifiers are retained to preserve existing results.

The per-fingerprint origin cap in Table III is a separate exploratory comparison. It challenges origins above each fingerprint’s calibration maximum (at least four), rather than blocking all clients on selected fingerprints.

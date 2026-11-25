# Findings of the submitted evaluation

The [submitted manuscript](../papers/http-session-noms/article.tex) is the
reference for these claims. The [table guide](../docs/tables.md) supplies
populations, denominators and machine-readable results.

| Evidence | Result | Cost or limit |
|---|---|---|
| Prospective primary pipeline, E1–E4 | 31 false alarms in 16,103 clean windows (0.19%) | Median collateral per false alarm: 39.0% of that window's legitimate origins |
| About 300 bots on new fingerprints at E1 | 89.6% coverage without the trigger | 2.9% behind the primary trigger |
| Prospective fallback | Challenges or rate-limits 0.6% of clean origin-windows | Filters block 0.016%; blocking and challenging are distinct actions |
| Prospective novelty, E1–E4 | No observed false alarm; 89.6% new-stack coverage at E1 | Cannot select shared fingerprints; zero observed alarms is not a zero-risk guarantee |
| Prospective beta-binomial arm | Preferred by the registered coverage decision rule | Median false-alarm collateral 65.7%; the preference does not establish a default deployment policy |
| Generated scopes, 5–25 new stacks | About 90% coverage from profile-relative scopes | Scope-only result; one-off fingerprints impose an approximate ceiling |
| Generated scopes, 100 new stacks | Novelty retains 88.1% coverage | Binomial coverage falls to 38.6% |
| E5, one-window-late replay | Removes 36.5% / 35.7% of the two attacks' requests | Collateral 0.02% / 0.05%, or 1.61% / 0.07% under alternative labels; attacks were already rate-limited |
| E5, ungated novelty and two-path rule | Selects fingerprints new at that site | Clean-window false-alarm rate 8.94%, exceeding the budget |
| Exploratory per-fingerprint origin cap | Challenges 57% of E1's 0.1× botnet on new fingerprints | Acts in 1.5% of clean windows, with median legitimate exposure 0.7%; cap figures were not independently recomputed here |

The results support three endpoint-specific measurements: coverage behind the
trigger, damage per false alarm and fallback exposure. No configuration dominated.
The study measures offline filtering outcomes, not live service availability.

Post hoc, the primary's 31 joint false alarms exceed independence expectations
under each stratification examined. The sustained-botnet estimates use per-window
fingerprint resampling; they do not establish fixed per-bot coverage. See the
[evaluation design](../docs/evaluation.md) and [post hoc guide](sprint-6-noms/scripts/posthoc/README.md).

Future work is prospective validation across sites of policies that weigh an
attack's service degradation against mitigation collateral. The current data
provide decision criteria rather than a validated operational policy.

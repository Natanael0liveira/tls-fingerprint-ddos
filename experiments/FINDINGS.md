# Findings frozen with r53

The [manuscript](../papers/http-session-noms/NOMS2027-r53.pdf) is the authoritative statement. See the [table map](../docs/tables.md) for denominators and machine-readable values.

| Setting | Positive result | Limitation/cost |
|---|---|---|
| Generated, 5–25 new stacks | About 90% coverage from profile-based scopes | This is scope-only; individual fingerprints impose an approximate ceiling |
| Generated, 100 stacks | Novelty retains 88.1% coverage | Binomial falls to 38.6% |
| Generated, shared/adversarial | Binomial selects 85.4% / 30.4% | Collateral 2.23% / 3.78%; novelty selects none |
| Prospective primary | FA 0.19%, below 1% | 31 alarms; median collateral 39.0%; rate stability not established |
| Prospective novelty | No observed false alarms | Cannot select shared fingerprints; transfers poorly to E5 |
| Prospective beta-binomial | Preferred by the coverage decision rule | Median FA collateral 65.7%; E1 new coverage 11.8% versus novelty 89.6% |
| E1, about 300 bots on new stacks | Ungated novelty coverage 89.6% | Primary coverage 2.9% because of the trigger |
| E5, one-window-late replay | Requests removed: 36.5% / 35.7% | Main-label collateral 0.02% / 0.05%, alternative 1.61% / 0.07%; attacks already rate-limited |
| E5, ungated novelty/two-path | Detects fingerprints new at the site | FA 8.94%, exceeding budget |

Post hoc, the primary's 31 joint false alarms exceed independence expectations of 2.87, 5.8 or 11.0 under different stratifications. This supports evaluating trigger and scope together, without identifying a shared causal mechanism.

Future work: prospective evaluation of the two-path rule across sites, and testing whether combined endpoint profiles reduce false alarms from legitimate updates without losing attack coverage.

The committed reductions support independent checks of several tables. E5 timing, persistence and stratification aggregates recovered from the handoff are in `sprint-6-noms/results/posthoc/`; [availability](../docs/reproduction.md) distinguishes aggregate checks from restricted-data reproduction.

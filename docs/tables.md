# Reading the current tables and their sources

This guide follows the eight tables in the [current manuscript](../papers/http-session-noms/article.tex). [Figures 1–2 have an illustrated guide](figures.md). The [r53 archive](../archive/noms2027/r53/README.md) has its own historical numbering.

## How to read the numbers

An origin is an address–fingerprint pair, not a unique person or machine. Production windows last five minutes. FA measures how often a filter is selected in clean windows; FA coll. measures the median damage **among those false alarms**. Coverage includes attack windows in which the trigger never fires. These quantities have different denominators; see [metrics](metrics.md).

Observed zero, a blank/dash and `n/a` are distinct: zero is a measured result, a blank/dash generally means not computed, and `n/a` denotes a conditional median with no false alarms. The overview uses its dash specifically for no fallback. Bold marks FA rates above the 1% budget. For configuration components and terminology, see the [glossary](concepts.md).

## Table I — Related approaches

**Question:** What does each approach select, and which operational question does it address?

Read each row across: prior work, selection criterion, evaluation setting, then its main question. Anomaly extraction identifies explanatory feature values; PacketScore scores packets against a nominal profile; the JA3 report discusses HTTPS mitigation; this work evaluates the coverage and collateral of endpoint-relative JA4 filtering.

“New” means absent from the particular endpoint's profile, not a globally new TLS implementation. The table positions the research question. It supplies no common benchmark or evidence of superiority over the listed approaches.

## Table II — Configurations and chronology

**Question:** Which trigger, scope and fleet policy make up each configuration, and when was it fixed?

Follow the three component columns together. The primary configuration uses the origin trigger, binomial **union novelty** selection and known-fleet exemptions. The beta-binomial arm changes both the trigger and statistical model, uses cross-fitting, and has no fleet exemption. The E1-only no-trigger arm retains the primary scope and exemption while removing its trigger.

The separators record chronology. The first six rows were fixed for the prospective evaluation, but the held-out-day protocol fixed only the primary and base rule. The novelty rule and two arms were pre-registered after that day, before the prospective data were examined; 11 of the 14 prospective days had not yet begun when the protocol was published. The two-path rule is post hoc, though fixed before E5 was examined.

In the last row, the slashes pair two paths: novelty without the trigger, and binomial selection with the origin trigger. These are components of one rule. The table defines configurations, not their measured effectiveness; use Table V for that comparison.

## Table III — Prospective coverage and exposure

**Question:** What does each policy deliver, and which legitimate clients does its action expose?

The three rows compare the primary pipeline, novelty without the trigger and an exploratory per-fingerprint origin cap over the 14-day prospective period. The primary pipeline blocks 2.9% of E1's approximately 300 bots on new fingerprints, compared with 89.6% for ungated novelty. The cap challenges 57%; challenging and blocking are distinct actions.

`Clean` is the share of E1–E4 clean windows with an action. `Legit.` is the median legitimate-origin share affected in those action windows. `Fallback` counts challenged or rate-limited clean origin-windows. The primary row therefore combines 0.19% clean-window activity, 39.0% median collateral per false alarm and 0.6% fallback exposure; those percentages have different denominators.

For ungated novelty, `n/a` means no E1–E4 false alarm, not an unmeasured median. In this overview, `--` means no fallback. E5 is separate: novelty raises false alarms in 8.9% of its clean windows with median collateral of 0.24%. The cap is post hoc; its numerical cells have not been independently recomputed here.

## Table IV — Calibration floors

**Question:** How large must a 25-stack botnet be for the scope alone to select a typical stack?

`n0` is the median legitimate origin count per window. The two `λe` columns are calibrated score cutoffs. Each floor cell gives **in sample / cross-fitted**, using development-day medians; the slash is not division. New fingerprints are absent from the profile, whereas shared ones are already present.

For example, E1's primary shared floor `254/286` means 254 or 286 attackers per window, depending on the calibration procedure. It is the size of the whole injected botnet needed to select a typical stack, not a number of blocked attackers or a guarantee of selecting all stacks. Random variation allows selection below the floor, and a separate trigger can still prevent action above it.

**Finding:** Legitimate fleets and shared fingerprints can make the floor large relative to normal traffic. E2's primary shared floor is `1090/1041` against `n0 = 62`. This is meaningful because attacks are added to the legitimate window. Extremely small `λe` values are calibrated scores, not reliable literal false-alarm probabilities. Table V uses the primary in sample and the beta-binomial arm cross-fitted.

## Table V — The 14-day prospective evaluation

**Question:** Which configurations trade coverage for false alarms and collateral over the prospective period?

Read the column groups separately:

- FA `all` pools 16,103 clean windows; `E1` is the busiest endpoint; `E2–E4` is the **highest** rate among those endpoints.
- `FA coll.` is the pooled median collateral per false alarm. `Crowds` is the pooled filter-firing rate under 1,000-client crowds.
- `E1, 0.1×` is about 300 attackers at E1. `100 attackers` pools a different injection size across endpoints. New and Shared describe fingerprint overlap with the profile.
- The no-trigger arm is E1-only; its additional values are in the note and cannot be read as pooled results across E1–E4.

**Example:** The primary row's FA of 0.19% and FA coll. of 39.0% mean infrequent false alarms with substantial damage in affected windows. They do not mean 39% of all legitimate traffic was blocked. Multiplying the FA rate by this median does not yield expected collateral, which requires the conditional mean.

The novelty rule has no observed prospective false alarms and 89.6% new-stack coverage at E1, but zero shared-stack coverage. The beta-binomial arm reaches 39.7% on the pooled 100-attacker shared scenario, with median FA collateral of 65.7%. The E1-only no-trigger arm exceeds budget at 1.56% FA. The two-path row combines novelty and primary results post hoc; it was not a seventh pre-registered configuration. Zero observed novelty alarms here does not contradict its failures at E5 in Table VI.

## Table VI — Two real attacks at E5

**Question:** What would the filters have removed, with what collateral, and how does delayed application change that result?

The first block holds the primary configuration fixed and changes timing: selection-window application, one-window delay, then delayed filters retained to the attack's end. The other configurations are compared in their selecting windows.

For each attack, `Req.` is the fraction of requests on selected fingerprints; `Att.` and `Leg.` are blocked fractions of attacker and legitimate origins respectively. Counts are summed over that attack's windows before taking the fractions. `Leg.e` repeats collateral under the alternative labels that count only edge-blocked addresses as attackers. `FA` instead uses E5's 1,152 clean windows across four days.

**Example:** One window late, the primary filters remove 36.5% and 35.7% of the attacks' requests, with 0.02% and 0.05% legitimate-origin collateral. Under the alternative labels that collateral is 1.61% and 0.07%. The novelty and two-path rules each have 8.94% clean-window FA, above budget.

These are post hoc counterfactual replays of attacks already rate-limited by the CDN. Request removal is neither the fraction of distinct machines completely blocked nor a measured improvement over the WAF. Fingerprint rotation also helped the origin trigger fire. Preserve the alternative-label and clean-day results when interpreting the positive request-removal result.

## Table VII — Scopes alone on generated traffic

**Question:** How does fingerprint selection change as attackers spread across more stacks or share legitimate fingerprints?

`K = 1000` is the attacker count; `M` is the number of stacks, with results over 15 seeds. Rows labelled only by `M` use new stacks. The last two use shared and adversarial fingerprints. The binomial columns report recall, collateral in attack windows (`Att. coll.`), and F1. The other three scope columns are **recall only**; their collateral is supplied in the note.

**Finding:** At 25 new stacks the binomial test selects 90.3% of attackers with no observed collateral. At 100 stacks, too few attackers per stack reduce recall to 38.6%. Shared and adversarial cases have 85.4% and 30.4% recall, with 2.23% and 3.78% collateral. The modal rule blocks 39.0% of legitimate traffic from five stacks onward, while the z-score's collateral reaches 3.37% on shared and 11.3% on adversarial stacks.

The approximate 90% recall ceiling comes from the one-off fingerprints assigned to about one bot in ten. These are isolated scopes in the alarm cluster, without the production trigger. Their recall cannot be equated with end-to-end coverage in Tables V or VIII, and an absent collateral column does not imply zero damage.

## Table VIII — Scopes under different triggers

**Question:** What changes when a scope runs behind the origin trigger, a seasonal trigger, or no trigger?

Compare scopes within a trigger block, then compare the same scope across blocks. `binomial` and `beta-bin.` **include novelty** here. Origin/binomial is the primary configuration, Seasonal/beta-bin. is the beta-binomial arm, and None/novelty is the standalone novelty rule of Table II. The beta-binomial rows use cross-fitting.

FA and New have separate development (`dev.`) and held-out (`held`) columns. Shared, Crowds and FA coll. use **development days only**. Crowds and FA coll. pool the endpoints; New and Shared concern **E1's 0.1× botnet only**. E2–E4 FA is their highest endpoint rate, not their mean.

**Example:** On development days, removing the trigger from the binomial configuration raises E1 new-stack coverage from 11.8% to 89.6%, while the largest E2–E4 false-alarm rate rises from 0.28% to 4.38%. The seasonal binomial variant reaches 20.4% coverage but also exceeds budget at 2.64%. This shows why Fig. 2's coverage gain must be read alongside false-alarm costs.

Some variants were added after the held-out day, as marked in the table. A held-out column does not make every displayed variant a pre-specified held-out test. Table V supplies the later prospective comparison.

## Exports and provenance

The [current machine-readable export](../experiments/sprint-6-noms/results/manuscript/tables.json) contains all eight tables in source order, original LaTeX, notes, row groups and the source hash. CSVs have explicit column names. Exporting TeX is transcription; the separate audit compares supported numerical cells with saved experimental reductions.

| Table | Content | Numerical source / provenance |
|---|---|---|
| [I](../experiments/sprint-6-noms/results/manuscript/table-1.csv) | Related approaches | Manuscript and bibliography |
| [II](../experiments/sprint-6-noms/results/manuscript/table-2.csv) | Configurations and chronology | Manuscript and frozen protocols |
| [III](../experiments/sprint-6-noms/results/manuscript/table-3.csv) | Prospective overview | `production_tables_block.json`, fallback aggregate; cap is post hoc |
| [IV](../experiments/sprint-6-noms/results/manuscript/table-4.csv) | Calibration floors | `production_tables.json`, `floor_bands.json` |
| [V](../experiments/sprint-6-noms/results/manuscript/table-5.csv) | Prospective variants | `production_tables_block.json`; two-path code in `scripts/posthoc/regra_uniao.py` |
| [VI](../experiments/sprint-6-noms/results/manuscript/table-6.csv) | Two real attacks | `posthoc/e5_delay_modes.json` supports 24 primary timing cells; other rows remain manuscript transcriptions |
| [VII](../experiments/sprint-6-noms/results/manuscript/table-7.csv) | Generated scopes | `unseen_synth_summary.csv`, `symbolic_detector.json` |
| [VIII](../experiments/sprint-6-noms/results/manuscript/table-8.csv) | Scopes by trigger | `production_tables.json`, development and held-out sections |

Result paths above are relative to `experiments/sprint-6-noms/results/`. The [current audit](../experiments/sprint-6-noms/results/manuscript/audit.json) lists 217 checked cells and its coverage limits. The overview's six numerical cells for the primary and novelty rows were checked separately in the [submission verification](../submissions/noms2027/verification.json). Neither check reruns the restricted data.

Historical [r53 exports](../experiments/sprint-6-noms/results/r53/README.md) are retained unchanged. See [metrics](metrics.md) for denominators and [reproduction](reproduction.md) for data availability.

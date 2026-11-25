# Methodology of the submitted evaluation

The [artifact record](../submissions/noms2027/verification.json) identifies the
complete submitted manuscript, kept in a separate local freeze.
The [evaluation design](../docs/evaluation.md), [metrics](../docs/metrics.md) and
[table map](../docs/tables.md) explain the protocol, denominators and public
result files.

## Evaluation periods

The operator-endpoint data cover 23 days: three initial calibration days, five
development days, one held-out day and fourteen prospective days. Each evaluated
day uses preceding traffic for its endpoint profiles and calibration. The five
development-day design choices precede the held-out and prospective evaluations.
The prospective protocol fixed six configurations; its three comparisons and
addendum are described in the [evaluation design](../docs/evaluation.md).

A separate customer site, E5, supplies seven clean days and an attack day with two
previously mitigated attacks. Labels, the request-share metric and those replays
are exploratory. Clean-window false alarms there use the last four clean days.
Original protocol and addendum files in `sprint-6-noms/results/` retain their
published contents and dates.

## Generated campaigns and injected botnets

Generated campaigns isolate fingerprint selection while varying the number of
TLS stacks and their overlap with legitimate traffic. New fingerprints are absent
from the legitimate traffic; shared fingerprints also occur among clients.
Production experiments inject bot counts into recorded five-minute windows at
four endpoints. Coverage includes windows where the trigger does not fire.

Selection-window coverage and deployed-filter coverage are different quantities.
The E5 timing replay tests delayed application. The sustained-botnet replay is
also post hoc: the paper's estimates redraw bot fingerprints each window from a
fixed daily pool. The corrected script defaults to fixed per-bot assignments,
but no fixed-assignment production rerun was performed here. See the
[post hoc guide](sprint-6-noms/scripts/posthoc/README.md).

## Scenario caches

The historical Makefiles use `experiments/data` as a link to an external data
root. The cache and export paths below are relative to that root:

| Path | Purpose |
|---|---|
| `synth/sprint6_realistic` | Generated campaign cache used by the scope experiments (`REALWORK`) |
| `synth/sprint6_rule` | Attack-free generated runs used for reference profiles (`RULEWORK`) |
| `synth/sprint4_realistic_work` | Earlier campaign cache used by historical comparison targets (`WORK`) |
| `azion/` | Restricted operator exports (`PRODDATA`) |
| `azion/block2/` | Restricted prospective-period export tree (`BLOCKDATA`) |

The generator distributions in [sprint-2/distributions/](sprint-2/distributions/)
are committed. The captures, large caches and private endpoint map are not.
[Reproduction instructions](../docs/reproduction.md) distinguish checks on saved
reductions from commands that require these inputs.

## What the checks establish

`make tables` regenerates CSVs from the committed eight-table snapshot, retaining its submitted-source hash.
The independent numerical audit checks 217 cells against committed reductions
and reports omitted cells and prose statistics. Neither operation reproduces
restricted traffic or establishes live service protection. Original protocols,
result aggregates and the [historical archive](../archive/README.md) remain
separate from regenerated manuscript transcriptions.

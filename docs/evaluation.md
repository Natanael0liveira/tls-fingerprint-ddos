# Evaluation design (r53)

The manuscript is an offline evaluation. It does not establish live service protection or superiority over the CDN's WAF.

## Periods

1. Three initial calibration days.
2. Five development days, each using preceding history. Five design choices were made on these days.
3. One held-out day; only the primary and base rule were fixed by its protocol.
4. Fourteen prospective days. The protocol fixed six configurations before data export or analysis; 11 of the 14 days had not begun when it was published.
5. A separate customer site, E5: seven clean days and an attack day with two real attacks. Replay labels and the request-share metric were chosen post hoc. Clean-day FA uses the last four clean days, each calibrated on its predecessors.

23 days at E1–E4 include 20 days receiving injected attacks. The customer site is separate. E1 holds about 95% of the operator's origin-windows.

## Pre-registered tests

- Stability of the primary configuration's FA rate relative to development. The fixed-rate test rejects consistency; a later Fisher test accounting for uncertainty gives P=0.07, which does not establish stability.
- Whether novelty and two alternative arms stay within the 1% budget per endpoint. Novelty and beta-binomial meet the observed-rate budget; the no-trigger arm on E1 does not.
- Preference for an eligible arm that improves coverage over novelty by at least one percentage point on new **or** shared stacks. Beta-binomial is preferred under this rule; that does not mean universal superiority or lower collateral.

An addendum amended test 3 after export but before results were computed: the original relative size gave only 2–7 attackers at E2–E4 and at most 0.1% coverage on development data. Both versions prefer the same arm. Protocols and export-hash records remain immutable in `experiments/sprint-6-noms/results/heldout_block*.md` and `fresh_day*.md`.

The two-path rule, independence analyses, persistent-filter replay and history-baseline comparison are exploratory. New findings should retain this distinction.

# Metrics and populations

| Metric | Denominator and aggregation |
|---|---|
| False-alarm rate (FA) | Clean five-minute windows in which a configuration selects a filter / eligible clean windows |
| Coverage on production injections | Mean blocked fraction over all attack windows, including windows whose trigger does not fire |
| Collateral | Legitimate origins selected / legitimate origins in that window |
| FA coll. | Median collateral conditional on a false alarm; not damage across all clean windows |
| Expected collateral per clean window | FA rate multiplied by **mean**, not median, collateral per false alarm |
| Origin-window collateral | Blocked legitimate origin-windows / all legitimate origin-windows; dominated by large endpoints |
| Crowds | Filter-firing rate under 1,000-client crowds |
| Table V E2–E4 | Highest endpoint FA rate among E2, E3 and E4 |
| Table V E1, 0.1× | About 300 attackers on E1; separate from the pooled 100-attacker scenario |
| Table VI Req. | Requests on selected fingerprints / requests, summed over the respective attack's windows |
| Table VI Att., Leg. | Blocked attacker/legitimate origins divided by their respective populations over the attack windows |
| Table VI Leg.e | Collateral when only edge-blocked addresses count as attackers |
| Table VII recall | Scope selection in the alarm cluster; does not include the production trigger |

`n/a` means no false alarms and hence no conditional median. A dash or blank generally denotes a measurement not computed; in the Table III overview, the dash specifically means no fallback. Neither means observed zero collateral. Bold identifies FA rates exceeding 1%, not arbitrary percentages exceeding 1%.

Table VIII uses development days for Crowds, FA coll. and Shared. Its paired dev./held. columns distinguish development and held-out results. New/Shared refer to E1's 0.1× injection.

The post hoc independence expectations 2.87, 5.8 and 11.0 use different stratifications. Their range is not a confidence interval. Window-based intervals assume independence; endpoint-day resampling addresses a different level of dependence.

Table III distinguishes blocked origins from origins exposed to a challenge. Its Clean column counts windows with an action; its Legit. column is conditional on those windows. These are not interchangeable measures of harm.

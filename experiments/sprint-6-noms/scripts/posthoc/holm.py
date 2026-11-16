from scipy import stats
import numpy as np
p = {
 "dev bb joint (Poisson 22 vs 7.533)": stats.poisson.sf(21, 7.5330876795162505),
 "Fisher trigger 31/233 vs 5/168": stats.fisher_exact([[31,202],[5,163]], alternative='greater')[1],
 "weekday binom 30/31 p=10/14": stats.binomtest(30, 31, 10/14, alternative='greater').pvalue,
 "held-out Bin(3,5/168)>=2": stats.binom.sf(1, 3, 5/168),
 "dev z joint (Poisson 20 vs 11.93)": stats.poisson.sf(19, 11.929898904006048),
 "Fisher rate rise": stats.fisher_exact([[31,16103-31],[5,5643-5]], alternative='greater')[1],
 "dev binomial xfit joint (Poisson 6 vs 3.168)": stats.poisson.sf(5, 3.1676917989417985),
 "dev binomial joint (Poisson 5 vs 3.472)": stats.poisson.sf(4, 3.4720001889644747),
}
for k,v in p.items(): print(f"{k:50s} raw={v:.6g}")
items = sorted(p.items(), key=lambda kv: kv[1]); m=len(items); run=0
print()
for i,(k,v) in enumerate(items):
    run = max(run, min(1, (m-i)*v)); print(f"{k:50s} holm={run:.5g}")
print("weekday binom with window share 0.714339:", stats.binomtest(30, 31, 0.7143389430540893, alternative='greater').pvalue)
print("rule of three 3/56", 3/56, "exact one-sided", 1-0.05**(1/56))
print("Omega endpoint share", 1188627.0/1303422.8)
print("implied floor E2", 1-(1-0.09302325581395349)/3, "E3", 1-(1-0.631578947368421)/3, "E4", 1-(1-0.390625)/3)
print("E3 surge Poisson P(X>=2|0.35)", stats.poisson.sf(1, 0.35))

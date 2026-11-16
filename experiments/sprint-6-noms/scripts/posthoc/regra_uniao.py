"""Exact false alarms, collateral and coverage of the two-path rule on the paper's endpoints:
the count (unseen filter) without a trigger, OR the origin trigger AND the binomial
configuration (test U unseen, known fleets at 5%). Reads the same window CSVs as Tables IV-VI."""
import sys, json
from pathlib import Path
import os
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np, pandas as pd
from production_tables import load, clopper_pearson
ROLE = json.loads(Path(os.environ["ENDPOINT_MAP"]).read_text())
A = os.environ["PRODDATA"]
periods = {"dev": (f"{A}/results/rule_production_windows_rolling_origin_fleets0.05_v2.csv",
                   ["2026-09-20", "2026-09-21", "2026-09-22", "2026-09-23", "2026-09-24"]),
           "held": (f"{A}/results/rule_production_windows_rolling_origin_fleets0.05_v2.csv", ["2026-09-25"]),
           "block": (f"{A}/block2/results/rule_production_windows_rolling_origin_fleets0.05_v2.csv", None)}
out, cache = {}, {}
for per, (path, folds) in periods.items():
    W = cache.get(path) if path in cache else cache.setdefault(path, load(path))
    if folds is None:
        folds = sorted(set(W["fold"]) - {"2026-09-20", "2026-09-21", "2026-09-22", "2026-09-23", "2026-09-24", "2026-09-25"})
    W = W[W["fold"].isin(folds) & W["host"].isin(ROLE)]
    behind = W["gate_origins"] & W["union_named"]
    rule = W["unseen_named"] | behind
    coll = np.where(behind, W["union_collateral"], np.where(W["unseen_named"], W["unseen_collateral"], np.nan))
    rec = np.where(behind, W["union_recall"], np.where(W["unseen_named"], W["unseen_recall"], 0.0))
    W = W.assign(rule=rule, rule_coll=coll, rule_rec=rec, behind=behind)
    C = W[W["kind"] == "clean"]
    res = {"folds": folds}
    for name, g in [("all", C)] + [(ROLE[h], C[C["host"] == h]) for h in sorted(ROLE, key=ROLE.get)]:
        k, n = int(g["rule"].sum()), int(len(g))
        res[name] = {"windows": n, "rule_fires": k, "rate": k / n if n else None, "ci95": clopper_pearson(k, n),
                     "count_fires": int(g["unseen_named"].sum()), "binomial_behind_trigger": int(g["behind"].sum()),
                     "both_same_window": int((g["unseen_named"] & g["behind"]).sum()),
                     "coll_median": float(np.nanmedian(g.loc[g["rule"], "rule_coll"])) if k else None,
                     "by_day": {d: int(x) for d, x in g.groupby("fold")["rule"].sum().items()}}
    # coverage of the injected botnets (25 stacks): E1 at a tenth of its median window, and 100 attackers pooled
    cov = {}
    for kind, src, col, x, who in [("attack_rel", "fresh", "fraction", 0.1, "E1"), ("attack_rel", "tail", "fraction", 0.1, "E1"),
                                   ("attack", "fresh", "attackers", 100, "all"), ("attack", "tail", "attackers", 100, "all")]:
        d = W[(W["kind"] == kind) & (W["source"] == src) & (W["stacks"] == 25) & (W[col] == x)]
        if who == "E1":
            d = d[d["host"] == next(h for h, e in ROLE.items() if e == "E1")]
        cov[f"{who}:{src}:{x:g}"] = float(d["rule_rec"].mean()) if len(d) else None
    fl = W[(W["kind"] == "flash") & (W["flash"] == 1000)]
    res["coverage"] = cov
    res["flash1000_fires"] = float(fl["rule"].mean()) if len(fl) else None
    out[per] = res
    a = res["all"]
    print(f"{per}: rule {a['rule_fires']}/{a['windows']} = {100*a['rate']:.3f}% CI {[round(100*x,3) for x in a['ci95']]} "
          f"(count {a['count_fires']}, binomial behind trigger {a['binomial_behind_trigger']}, both {a['both_same_window']}), "
          f"coll median {a['coll_median']}; per endpoint " + ", ".join(f"{e} {res[e]['rule_fires']}/{res[e]['windows']} ({100*res[e]['rate']:.2f}%)" for e in ("E1","E2","E3","E4"))
          + f"; coverage {cov}; flash1000 {res['flash1000_fires']}")
Path(sys.argv[1]).write_text(json.dumps(out, indent=1))

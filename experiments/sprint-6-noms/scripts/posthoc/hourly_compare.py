"""Hourly profiles (--profile-by-hour 1) against the paper's binomial configuration (one profile per
endpoint), same days: false alarms behind the origin trigger, the count, joint excess against
stratified independence, weekday endpoint-days, flash crowds and coverage cells."""
import sys, json
from pathlib import Path
import os
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pandas as pd
from scipy.stats import poisson, fisher_exact
from production_tables import load, clopper_pearson
A = os.environ["PRODDATA"]
DEV = ["2026-09-20", "2026-09-21", "2026-09-22", "2026-09-23", "2026-09-24", "2026-09-25"]
ROLE = json.loads(Path(os.environ["ENDPOINT_MAP"]).read_text())
pairs = {"prospective": (f"{A}/block2/results/rule_production_windows_rolling_origin_fleets0.05_v2.csv",
                         f"{A}/block2/results_hour1/rule_production_windows_rolling_origin_fleets0.05_hour1.csv", None),
         "E5 clean days": (f"{A}/incidente-2026-11-10/results/rule_production_windows_rolling_origin_fleets0.05_v2.csv",
                           f"{A}/incidente-2026-11-10/results_hour1/rule_production_windows_rolling_origin_fleets0.05_hour1.csv",
                           ["2026-11-06", "2026-11-07", "2026-11-08", "2026-11-09"])}
out = {}
for per, (p_one, p_hour, folds) in pairs.items():
    for prof, path in (("one profile", p_one), ("hourly profiles", p_hour)):
        W = load(path); W = W[W["host"].isin(ROLE)]
        fo = folds or sorted(set(W["fold"]) - set(DEV) - {"2026-09-17", "2026-09-18", "2026-09-19"})
        W = W[W["fold"].isin(fo)]
        C = W[W["kind"] == "clean"].copy()
        C["hour"] = C["window"].astype(str).str.slice(11, 13)
        C["dec"] = C.groupby("host")["size"].transform(lambda s: pd.qcut(s.rank(method="first"), 10, labels=False))
        j = C["gate_origins"] & C["union_named"]
        r = {"windows": int(len(C)), "binomial_fa": int(j.sum()), "binomial_rate": float(j.mean()),
             "ci95": clopper_pearson(int(j.sum()), int(len(C))), "count_fa": int(C["unseen_named"].sum()),
             "scope_alone_rate": float(C["union_named"].mean()),
             "per_endpoint": {ROLE[h]: int((g["gate_origins"] & g["union_named"]).sum()) for h, g in C.groupby("host")},
             "coll_median": float(C.loc[j, "union_collateral"].median()) if j.any() else None}
        for name, keys in [("endpoint", ["host"]), ("endpoint_day_hour", ["host", "fold", "hour"]), ("endpoint_n_decile", ["host", "dec"])]:
            g = C.assign(g=C["gate_origins"], s=C["union_named"]).groupby(keys)
            e = float((g["g"].mean() * g["s"].mean() * g.size()).sum())
            r[f"expected_{name}"] = round(e, 2); r[f"P_{name}"] = float(poisson.sf(int(j.sum()) - 1, e)) if e > 0 else None
        ed = C.assign(j=j).groupby(["host", "fold"])["j"].sum().reset_index()
        ed["wd"] = pd.to_datetime(ed["fold"]).dt.weekday < 5
        t = pd.crosstab(ed["wd"], ed["j"] > 0).reindex(index=[True, False], columns=[True, False], fill_value=0)
        r["endpoint_days_weekday_with_fa"] = f"{int(t.loc[True, True])}/{int(t.loc[True].sum())}"
        r["endpoint_days_weekend_with_fa"] = f"{int(t.loc[False, True])}/{int(t.loc[False].sum())}"
        r["weekday_fisher_P"] = float(fisher_exact(t.to_numpy(), alternative="greater")[1]) if t.loc[False].sum() else None
        fl = W[(W["kind"] == "flash") & (W["flash"] == 1000)]
        r["flash1000"] = float((fl["gate_origins"] & fl["union_named"]).mean()) if len(fl) else None
        for cell, kind, src, col, x, host in [("E1 0.1x new", "attack_rel", "fresh", "fraction", 0.1, next(h for h, e in ROLE.items() if e == "E1")),
                                              ("E1 0.1x shared", "attack_rel", "tail", "fraction", 0.1, next(h for h, e in ROLE.items() if e == "E1")),
                                              ("100 new", "attack", "fresh", "attackers", 100, None), ("100 shared", "attack", "tail", "attackers", 100, None)]:
            d = W[(W["kind"] == kind) & (W["source"] == src) & (W["stacks"] == 25) & (W[col] == x)]
            if host: d = d[d["host"] == host]
            r[f"cov {cell}"] = round(float((d["union_recall"] * (d["gate_origins"] & d["union_named"])).mean()), 4) if len(d) else None
        out[f"{per} | {prof}"] = r
        print(per, "|", prof, json.dumps(r, default=str))
json.dump(out, open(sys.argv[1], "w"), indent=1, default=str)

"""Battery F4 (11 Nov 2026): the persistence replay of battery F per endpoint, prospective period and development days,
binomial configuration. Answers the expert r21: the pooled 0.012% is dominated by E1's client-windows, where no false alarm
fell. Same rebuild as bateria_f.py; each endpoint's share is over its own clean client-windows. Post hoc."""
import sys, json
from collections import defaultdict
from pathlib import Path
import pandas as pd
from pathlib import Path
import os
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rule_detection_production import load_day, build_windows
from production_tables import load
exec(open(Path(__file__).with_name("bateria_f.py")).read().split("out = {}")[0].split('"""', 2)[2])
out = {}
for period in ("dev", "prospective"):
    data_dir, csv = RUNS[period]
    R = records(data_dir); W = load(csv)
    names = pd.read_csv(csv, usecols=["kind", "fold", "host", "window", "named"], dtype={"fold": str, "named": str})
    W = W[W["kind"] == "clean"].merge(names[names["kind"] == "clean"], on=["kind", "fold", "host", "window"], how="left")
    folds = DEV if period == "dev" else sorted(set(W["fold"]) - set(DEV) - {"2026-09-25"})
    C = W[W["fold"].isin(folds) & W["host"].isin(ROLE)].copy(); C["ts"] = pd.to_datetime(C["window"], utc=True)
    eligible = set(zip(C["host"], C["ts"]))
    FA = C[C["gate_origins"] & C["union_named"]]
    cache = {}
    def pidx(h, d):
        if (h, d) not in cache:
            bg = [r["clean"] for (hh, w), r in R.items() if hh == h and w.date() < d]
            cache[(h, d)] = set(pd.concat(bg).groupby(level=0).sum().loc[lambda s: s > 0].index) if bg else set()
        return cache[(h, d)]
    filters = []
    for _, x in FA.iterrows():
        r = R[(x["host"], x["ts"])]; c0 = r["clean"][r["clean"] > 0]
        named = set(str(x["named"]).split(";")) if isinstance(x["named"], str) and x["named"] else set()
        filters.append((x["host"], x["ts"], named | {f for f, c in c0.items() if c >= K_MIN and f not in pidx(x["host"], x["ts"].date())}))
    active = defaultdict(set)
    for h, t, F in filters:
        for k in range(1, 13): active[(h, t + k * STEP)] |= F
    per = {}
    tot = C.groupby("host")["size"].sum().to_dict()
    for host, role in ROLE.items():
        same = sum(float(R[(h, t)]["clean"][R[(h, t)]["clean"].index.isin(F)].sum()) for h, t, F in filters if h == host)
        hold = sum(float(R[(h, w)]["clean"][R[(h, w)]["clean"].index.isin(F)].sum()) for (h, w), F in active.items() if h == host and (h, w) in eligible)
        n = float(tot.get(host, 0))
        per[role] = {"false_alarms": sum(1 for h, _, _ in filters if h == host), "clean_client_windows": n,
                     "share_of_all_client_windows": n / float(C["size"].sum()),
                     "same_window_share": same / n if n else None, "hold_12_share": hold / n if n else None}
    e24 = [r for r in ("E2", "E3", "E4")]
    n24 = sum(per[r]["clean_client_windows"] for r in e24)
    per["E2-E4 pooled"] = {"same_window_share": sum(per[r]["same_window_share"] * per[r]["clean_client_windows"] for r in e24) / n24,
                           "hold_12_share": sum(per[r]["hold_12_share"] * per[r]["clean_client_windows"] for r in e24) / n24}
    out[period] = per
    print(period, json.dumps({k: {m: (round(100 * v, 4) if isinstance(v, float) and m != "clean_client_windows" else v) for m, v in d.items()} for k, d in per.items()}))
json.dump(out, open(sys.argv[1], "w"), indent=1)

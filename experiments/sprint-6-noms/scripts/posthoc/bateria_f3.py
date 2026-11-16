"""Battery F3 (11 Nov 2026): for the prospective false alarms of the binomial configuration, the share of each later
window's clients on the false alarm's filter (mean over the next 12 windows), split by whether the fingerprints came back
within the hour, next to the share in the window that selected them. Same rebuild as bateria_f.py. Post hoc."""
import sys, json
from pathlib import Path
import numpy as np, pandas as pd
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
    sel, later_all, later_back = [], [], []
    for _, x in FA.iterrows():
        r = R[(x["host"], x["ts"])]; c0 = r["clean"][r["clean"] > 0]
        named = set(str(x["named"]).split(";")) if isinstance(x["named"], str) and x["named"] else set()
        F = named | {f for f, c in c0.items() if c >= K_MIN and f not in pidx(x["host"], x["ts"].date())}
        sel.append(float(c0[c0.index.isin(F)].sum() / r["n"]))
        shares = []
        for k in range(1, 13):
            key = (x["host"], x["ts"] + k * STEP)
            if key in eligible and R[key]["n"]:
                c = R[key]["clean"]; shares.append(float(c[c.index.isin(F)].sum() / R[key]["n"]))
        m = float(np.mean(shares)); later_all.append(m)
        if any(s > 0 for s in shares): later_back.append(m)
    out[period] = {"false_alarms": len(sel), "selecting_window_share_median": float(np.median(sel)),
                   "later_mean_share_median_all": float(np.median(later_all)),
                   "later_mean_share_median_returning": float(np.median(later_back)) if later_back else None,
                   "returning": len(later_back), "later_mean_share_max": float(np.max(later_all))}
    print(period, out[period])
json.dump(out, open(sys.argv[1], "w"), indent=1)

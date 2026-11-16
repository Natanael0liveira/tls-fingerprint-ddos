"""Battery F2 (11 Nov 2026): for the replay of battery F, how many false alarms' fingerprints come back within the next
hour, and how many false alarms have less than a full hour of eligible clean windows after them (the period ends, or
later windows hold fewer than k_min origins). Same rebuild of each filter as bateria_f.py. Post hoc."""
import sys, re, json
from pathlib import Path
import pandas as pd
from pathlib import Path
import os
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rule_detection_production import load_day, build_windows
from production_tables import load
exec(open(Path(__file__).with_name("bateria_f.py")).read().split("out = {}")[0].split('"""', 2)[2])
res = {}
for period, (data_dir, csv) in RUNS.items():
    R = records(data_dir); W = load(csv)
    names = pd.read_csv(csv, usecols=["kind", "fold", "host", "window", "named"], dtype={"fold": str, "named": str})
    W = W[W["kind"] == "clean"].merge(names[names["kind"] == "clean"], on=["kind", "fold", "host", "window"], how="left")
    folds = DEV if period == "dev" else sorted(set(W["fold"]) - set(DEV) - {"2026-09-25"})
    C = W[W["fold"].isin(folds) & W["host"].isin(ROLE)].copy(); C["ts"] = pd.to_datetime(C["window"], utc=True)
    eligible = set(zip(C["host"], C["ts"])); last = C["ts"].max()
    for cfg in ("binomial", "count"):
        FA = C[C["gate_origins"] & C["union_named"]] if cfg == "binomial" else C[C["unseen_named"]]
        cache = {}
        def pidx(h, d):
            if (h, d) not in cache:
                bg = [r["clean"] for (hh, w), r in R.items() if hh == h and w.date() < d]
                cache[(h, d)] = set(pd.concat(bg).groupby(level=0).sum().loc[lambda s: s > 0].index) if bg else set()
            return cache[(h, d)]
        n = back = short = past_end = 0; returned_windows = []
        for _, x in FA.iterrows():
            r = R[(x["host"], x["ts"])]; c0 = r["clean"][r["clean"] > 0]
            named = (set(str(x["named"]).split(";")) if isinstance(x["named"], str) and x["named"] else set()) if cfg == "binomial" else set()
            F = named | {f for f, c in c0.items() if c >= K_MIN and f not in pidx(x["host"], x["ts"].date())}
            n += 1; hits = 0; follow = 0
            for k in range(1, 13):
                key = (x["host"], x["ts"] + k * STEP)
                if key in eligible:
                    follow += 1
                    c = R[key]["clean"]
                    if c[c.index.isin(F)].sum() > 0: hits += 1
            if x["ts"] + 12 * STEP > last: past_end += 1
            if follow < 12: short += 1
            if hits: back += 1; returned_windows.append(hits)
        res[f"{period}:{cfg}"] = {"false_alarms": n, "fingerprints_back_within_hour": back, "never_back": n - back,
                                  "windows_with_return_median": (sorted(returned_windows)[len(returned_windows) // 2] if returned_windows else 0),
                                  "less_than_12_eligible_followup_windows": short, "hour_runs_past_period_end": past_end}
        print(period, cfg, res[f"{period}:{cfg}"])
json.dump(res, open(sys.argv[1], "w"), indent=1)

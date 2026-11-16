"""11 Nov 2026: the fallback's challenged share of clean client-windows per endpoint (expert r21, question 1).
Fallback = origin trigger fires and the binomial configuration selects nothing. Same windows as bateria_f.py."""
import sys, json
from pathlib import Path
import pandas as pd
from pathlib import Path
import os
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from production_tables import load
src = open(Path(__file__).with_name("bateria_f.py")).read()
exec(src.split("def records")[0].split('"""', 2)[2])
out = {}
for period, (data_dir, csv) in RUNS.items():
    W = load(csv); W = W[W["kind"] == "clean"]
    folds = DEV if period == "dev" else sorted(set(W["fold"]) - set(DEV) - {"2026-09-25"})
    C = W[W["fold"].isin(folds) & W["host"].isin(ROLE)]
    fb = C[C["gate_origins"] & ~C["union_named"]]; fa = C[C["gate_origins"] & C["union_named"]]
    N = float(C["size"].sum()); res = {"pooled": {"fallbacks": len(fb), "false_alarms": len(fa), "challenged_share": float(fb["size"].sum()) / N}}
    for h, r in ROLE.items():
        Ch = C[C["host"] == h]; n = float(Ch["size"].sum())
        res[r] = {"fallbacks": int((fb["host"] == h).sum()), "false_alarms": int((fa["host"] == h).sum()),
                  "windows": len(Ch), "challenged_share": float(fb[fb["host"] == h]["size"].sum()) / n}
    out[period] = res
    print(period, {k: (v["fallbacks"], v["false_alarms"], round(100 * v["challenged_share"], 3)) for k, v in res.items()})
json.dump(out, open(sys.argv[1], "w"), indent=1)

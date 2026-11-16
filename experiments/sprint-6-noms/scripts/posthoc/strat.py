import sys, json
from pathlib import Path
import os
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pandas as pd
from scipy.stats import poisson
from production_tables import load
A = os.environ["PRODDATA"]
ROLE = json.loads(Path(os.environ["ENDPOINT_MAP"]).read_text())
DEV = ["2026-09-20", "2026-09-21", "2026-09-22", "2026-09-23", "2026-09-24"]
res = {}
for tag, path, scope, gate in [("block binomial", f"{A}/block2/results/rule_production_windows_rolling_origin_fleets0.05_v2.csv", "union", "origins"),
                               ("block z-score", f"{A}/block2/results/rule_production_windows_rolling_origin_v2.csv", "zcal", "origins"),
                               ("block bb seasonal", f"{A}/block2/results/rule_production_windows_crossfit_origin_od_v2.csv", "union", "seasonal")]:
    W = load(path)
    fo = sorted(set(W["fold"]) - set(DEV) - {"2026-09-25"})
    C = W[(W["kind"] == "clean") & W["fold"].isin(fo) & W["host"].isin(ROLE)].copy()
    C["hour"] = C["window"].astype(str).str.slice(11, 13)
    C["dec"] = C.groupby("host")["size"].transform(lambda s: pd.qcut(s.rank(method="first"), 10, labels=False))
    g_, s_ = C[f"gate_{gate}"], C[f"{scope}_named"]
    obs = int((g_ & s_).sum()); r = {"observed": obs, "windows": int(len(C))}
    for name, keys in [("endpoint", ["host"]), ("endpoint_day", ["host", "fold"]), ("endpoint_day_hour", ["host", "fold", "hour"]), ("endpoint_n_decile", ["host", "dec"])]:
        gg = C.assign(g=g_, s=s_).groupby(keys)
        e = float((gg["g"].mean() * gg["s"].mean() * gg.size()).sum())
        r[name] = {"expected": e, "P": float(poisson.sf(obs - 1, e))}
    if tag == "block binomial":
        # weekday windows share, for the binomial weekday test with window weights
        C["wd"] = pd.to_datetime(C["fold"]).dt.weekday < 5
        r["weekday_window_share"] = float(C["wd"].mean())
        r["weekday_fa"] = int((g_ & s_ & C["wd"]).sum())
    res[tag] = r
    print(tag, json.dumps(r))
    del W
json.dump(res, open(sys.argv[1], "w"), indent=1)

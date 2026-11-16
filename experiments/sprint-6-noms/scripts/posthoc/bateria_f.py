"""Battery F (11 Nov 2026), item D of the external simulated review: what a false alarm costs when the filter persists.

For the binomial configuration (origin trigger, binomial test with the count, fleets 5%), every false alarm on the clean
windows of the development days and of the prospective period gets its filter rebuilt: the test's picks (column "named"
of the per-window CSV) and the count's picks (fingerprints with at least k_min origins absent from the profile, the sum
of every earlier day's clean windows, as in rule_detection_production.py). The rebuild is checked against the collateral
the pipeline stored. Then the filter acts from the next window and stays for 1, 6 or 12 windows (5 minutes to an hour);
overlapping filters on one endpoint are merged per window, so no client is counted twice. Output: the share of clean
client-windows blocked, next to the same-window share the paper reports (0.006% and 0.016%), and per false alarm the
share of each later window's clients the filter would block. The same for the count run without the trigger (the two-path
rule's other path), whose picks are rebuilt the same way. Post hoc."""
import sys, json, re
from collections import defaultdict
from pathlib import Path
import numpy as np, pandas as pd
from pathlib import Path
import os
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rule_detection_production import load_day, build_windows
from production_tables import load

A = Path(os.environ["PRODDATA"])
ROLE = json.loads(Path(os.environ["ENDPOINT_MAP"]).read_text())
DEV = ["2026-09-20", "2026-09-21", "2026-09-22", "2026-09-23", "2026-09-24"]
K_MIN, STEP = 5, pd.Timedelta(minutes=5)
RUNS = {"dev": (A, A / "results/rule_production_windows_rolling_origin_fleets0.05_v2.csv"),
        "prospective": (A / "block2", A / "block2/results/rule_production_windows_rolling_origin_fleets0.05_v2.csv")}
HOLD = [1, 6, 12]

def records(data_dir):
    days = sorted(p for p in data_dir.iterdir() if p.is_dir() and re.fullmatch(r"\d{4}-\d{2}-\d{2}(_\d{4}-\d{2}-\d{2})?", p.name))
    recs = []
    for d in days:
        recs += build_windows(*load_day(d, "origin"))
    return {(r["host"], r["window"]): r for r in recs if r["host"] in ROLE}

out = {}
for period, (data_dir, csv) in RUNS.items():
    R = records(data_dir)
    W = load(csv)
    names = pd.read_csv(csv, usecols=["kind", "fold", "host", "window", "named"], dtype={"fold": str, "named": str})
    names = names[names["kind"] == "clean"]
    W = W[W["kind"] == "clean"].merge(names, on=["kind", "fold", "host", "window"], how="left")
    folds = DEV if period == "dev" else sorted(set(W["fold"]) - set(DEV) - {"2026-09-25"})
    C = W[W["fold"].isin(folds) & W["host"].isin(ROLE)].copy()
    C["ts"] = pd.to_datetime(C["window"], utc=True)
    nsum = float(C["size"].sum())
    eligible = set(zip(C["host"], C["ts"]))
    for cfg in ("binomial", "count"):
      FA = C[C["gate_origins"] & C["union_named"]] if cfg == "binomial" else C[C["unseen_named"]]
      prof_cache = {}
      def profile_index(host, day):
          k = (host, day)
          if k not in prof_cache:
              bg = [r["clean"] for (h, w), r in R.items() if h == host and w.date() < day]
              prof_cache[k] = set(pd.concat(bg).groupby(level=0).sum().loc[lambda s: s > 0].index) if bg else set()
          return prof_cache[k]
      filters, max_err, same = [], 0.0, 0.0
      for _, x in FA.iterrows():
          r = R[(x["host"], x["ts"])]
          counts = r["clean"][r["clean"] > 0]
          named = (set(str(x["named"]).split(";")) if isinstance(x["named"], str) and x["named"] else set()) if cfg == "binomial" else set()
          unseen = {f for f, c in counts.items() if c >= K_MIN and f not in profile_index(x["host"], x["ts"].date())}
          F = named | unseen
          coll = float(counts[counts.index.isin(F)].sum() / r["n"]) if r["n"] else 0.0
          max_err = max(max_err, abs(coll - float(x["union_collateral" if cfg == "binomial" else "unseen_collateral"])))
          same += float(counts[counts.index.isin(F)].sum())
          filters.append((x["host"], x["ts"], F))
      res = {"clean_windows": int(len(C)), "clean_client_windows": nsum, "false_alarms": len(filters),
             "rebuild_max_abs_error_vs_stored_collateral": max_err,
             "same_window_share": same / nsum}
      for N in HOLD:
          active = defaultdict(set)
          for h, t, F in filters:
              for k in range(1, N + 1):
                  active[(h, t + k * STEP)] |= F
          blocked, per_fa = 0.0, []
          for (h, w), F in active.items():
              if (h, w) in eligible and (h, w) in R:
                  c = R[(h, w)]["clean"]
                  blocked += float(c[c.index.isin(F)].sum())
          for h, t, F in filters:
              shares = []
              for k in range(1, N + 1):
                  key = (h, t + k * STEP)
                  if key in eligible and key in R and R[key]["n"]:
                      c = R[key]["clean"]
                      shares.append(float(c[c.index.isin(F)].sum() / R[key]["n"]))
              if shares:
                  per_fa.append(float(np.mean(shares)))
          res[f"hold_{N}"] = {"share_of_clean_client_windows": blocked / nsum,
                              "ratio_to_same_window": (blocked / nsum) / (same / nsum) if same else None,
                              "per_false_alarm_mean_share_median": float(np.median(per_fa)) if per_fa else None,
                              "per_false_alarm_mean_share_p90": float(np.percentile(per_fa, 90)) if per_fa else None}
      out[f"{period}:{cfg}"] = res
      print(period, cfg, json.dumps(res, indent=1))
json.dump(out, open(sys.argv[1], "w"), indent=1)

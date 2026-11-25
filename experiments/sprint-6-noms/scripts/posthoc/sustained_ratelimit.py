"""Sustained botnets and a per-fingerprint rate limit (20 Nov 2026), after external reviews A (W2, W6, m2)
and B (W3) and the blind expert (F2). Post hoc.

Primary configuration, as in the frozen runs: rolling split, origin unit, k_min 5, trigger at the p99 of the
calibration windows' origins, binomial test at the calibrated level with 5% known fleets, union with the novelty
rule. Every clean window of the development days, the held-out day and the prospective period is rebuilt from the
exports and its decision checked against the stored per-window CSV (trigger, picks, collateral).

1. Sustained botnet, deployed filter. The same botnet joins every window of a test day: 25 stacks new to the
   endpoint ("fresh") or drawn once a day from its profile outside the ten commonest ("tail"), 90% of the
   attackers on the stacks, as in the frozen runs. Each attacker's fingerprint is drawn once and held all day.
   --assignment resampled reproduces the original replay, which kept the stack pool but redrew each
   attacker's fingerprint in every window. Its results must not be described as fixed assignments.
   A pick made in window t acts from t+1 for an hour (12 windows),
   as in the one-hour replay of the false alarms (bateria_f.py). Reported: coverage in the selecting window (the
   paper's convention), coverage of the deployed filter over a day-long attack, and over
   attacks of 30 minutes and one hour starting at every window of the day (for these, an hour's hold equals
   keeping the filter to the attack's end).
2. Per-fingerprint rate limit, a standing policy with no trigger: in each window a fingerprint may hold as many
   origins as its maximum over the calibration windows, never fewer than k_min - 1 (a fingerprint absent from the
   profile gets k_min - 1). The excess is challenged at random among the fingerprint's origins, so the bots and the
   legitimate clients of a fingerprint over its cap are hit in proportion. Reported on the clean windows and on the
   same attack windows.

Usage: PRODDATA=... ENDPOINT_MAP=... python sustained_ratelimit.py OUT.json [--workers 7] [--assignment fixed]
The output holds aggregates only: endpoints as E1-E4, no fingerprints, no timestamps.
"""
import argparse, hashlib, json, os, re, sys, time, zlib
import multiprocessing as mp
from collections import defaultdict
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rule_detection_production import load_day, build_windows, known_fleets, adjusted_p, scope, botnet, stacks_for  # noqa: E402
from production_tables import cluster_ci  # noqa: E402

ROLE = {}
PERIODS = {}
ASSIGNMENT = "fixed"
SEED = 20261121
DEV = {"2026-09-20", "2026-09-21", "2026-09-22", "2026-09-23", "2026-09-24"}
HELD = {"2026-09-25"}
ARGS = SimpleNamespace(k_min=5, rho=3.0, significance=0.01, fleets=0.05, percentiles=[99],
                       ja4_share=0.9, prefix_pool=2000, overdispersion=False)
STEP, HOLD = pd.Timedelta(minutes=5), 12
CONFIGS = [("fresh", "A", 100), ("fresh", "x", 0.1), ("fresh", "x", 0.5), ("fresh", "x", 1.0),
           ("tail", "A", 100), ("tail", "x", 0.1), ("tail", "x", 0.5), ("tail", "x", 1.0)]
DURATIONS = [6, 12]
G = {}          # filled before forking: G["recs"][host] = records sorted by window


def group(day):
    return "dev" if day in DEV else "held" if day in HELD else "prospective"


def load_period(data_dir):
    days = sorted(p for p in data_dir.iterdir()
                  if p.is_dir() and re.fullmatch(r"\d{4}-\d{2}-\d{2}(_\d{4}-\d{2}-\d{2})?", p.name))
    recs = []
    for d in days:
        recs += build_windows(*load_day(d, "origin"))
    if pd.Series([(r["host"], r["window"]) for r in recs]).duplicated().any():
        raise SystemExit(f"{data_dir}: duplicated host-windows")
    dates = sorted({r["window"].date() for r in recs})
    by = defaultdict(list)
    for r in recs:
        if r["host"] in ROLE:
            by[r["host"]].append(r)
    for h in by:
        by[h].sort(key=lambda r: r["window"])
    return dict(by), dates


def prepare(cal):
    """Profile, known fleets, calibrated level, trigger threshold and rate-limit caps of one endpoint and fold."""
    bg = pd.concat([r["clean"] for r in cal]).groupby(level=0).sum()
    P = (bg / bg.sum()).sort_values(ascending=False)
    P.attrs["n"] = int(bg.sum())
    fl = known_fleets(cal, lambda r: P, ARGS)
    t = [min(adjusted_p(r["clean"], P, ARGS.rho, fl)[1], default=np.inf) for r in cal if r["n"] >= ARGS.k_min]
    la = min(np.log(ARGS.significance), float(np.percentile(t, 100 - ARGS.percentiles[0], method="lower")))
    thr = float(pd.Series([r["n"] for r in cal if r["n"] >= ARGS.k_min], dtype=float).quantile(0.99))
    caps = pd.concat([r["clean"] for r in cal]).groupby(level=0).max()
    return P, fl, la, thr, caps, float(np.median([r["n"] for r in cal]))


def picks(total, n, P, fl, la):
    """(binomial picks, novelty picks) of a window, as judge() makes them."""
    if n < ARGS.k_min:
        return frozenset(), frozenset()
    tot = total[total > 0].sort_values(ascending=False)
    named = scope(tot, P, ARGS.rho, la, exclude=fl)
    unseen = set(tot.index[~tot.index.isin(P.index) & (tot.to_numpy() >= ARGS.k_min)])
    return frozenset(named), frozenset(unseen)


def rate_limit(legit, bot, caps):
    """Origins the per-fingerprint cap challenges: (legitimate, attackers, acted)."""
    total = legit if bot is None else legit.add(bot, fill_value=0)
    cap = caps.reindex(total.index).fillna(0.0).clip(lower=ARGS.k_min - 1)
    excess = (total - cap).clip(lower=0.0)
    share = (excess / total).fillna(0.0)
    lc = float((legit * share.reindex(legit.index)).sum())
    bc = float((bot * share.reindex(bot.index)).sum()) if bot is not None else 0.0
    return lc, bc, bool(excess.sum() > 0)


def on(series, F):
    return float(series[series.index.isin(F)].sum()) if F else 0.0


def task(job):
    period, d, host = job
    recs = G["recs"][host]
    cal = [r for r in recs if r["window"].date() < d]
    test = [r for r in recs if r["window"].date() == d and r["n"] > 0]
    if sum(r["n"] >= ARGS.k_min for r in cal) < 50 or np.median([r["n"] for r in cal]) < ARGS.k_min or not test:
        return None
    P, fl, la, thr, caps, med = prepare(cal)
    out = {"period": period, "day": d.isoformat(), "host": host, "threshold": thr, "clean": [], "attack": {}}
    for r in test:
        if r["n"] < ARGS.k_min:
            continue
        named, unseen = picks(r["clean"], r["n"], P, fl, la)
        union = named | unseen
        lc, _, acted = rate_limit(r["clean"], None, caps)
        out["clean"].append({"window": r["window"].isoformat(), "n": r["n"], "gate": bool(r["n"] >= thr),
                             "union": bool(union), "binom": bool(named), "unseen": bool(unseen),
                             "union_coll": on(r["clean"], union) / r["n"], "rl_cut": lc, "rl_acted": acted})
    for ci, (source, kind, size) in enumerate(CONFIGS):
        rng = np.random.default_rng([SEED, d.toordinal(), zlib.crc32(host.encode()), ci])
        A_ = int(size) if kind == "A" else max(1, int(round(size * med)))
        stacks = stacks_for(source, 25, P, rng)          # the stack pool is fixed in both models
        if stacks is None:
            continue
        fixed_bot = botnet(A_, stacks, ARGS, rng)[0] if ASSIGNMENT == "fixed" else None
        T, S, U, rows = [], [], [], []
        for r in test:
            bot = fixed_bot if fixed_bot is not None else botnet(A_, stacks, ARGS, rng)[0]
            named, unseen = picks(r["clean"].add(bot, fill_value=0), r["n"] + A_, P, fl, la)
            union = named | unseen
            gate = r["n"] + A_ >= thr
            T.append(r["window"]); U.append(union); S.append(union if gate else frozenset())
            rows.append((r, bot, gate, *rate_limit(r["clean"], bot, caps)[:2]))
        acc = defaultdict(float)
        windows = []
        for i, (r, bot, gate, lc, bc) in enumerate(rows):
            F, Fu = set(), set()
            j = i - 1
            while j >= 0 and T[i] - T[j] <= HOLD * STEP:
                F |= S[j]; Fu |= U[j]; j -= 1
            w = {"gate": gate, "same_primary": on(bot, S[i]) / A_, "same_scope_alone": on(bot, U[i]) / A_,
                 "deployed_primary": on(bot, F) / A_, "deployed_scope_alone": on(bot, Fu) / A_,
                 "rate_limit": bc / A_, "rate_limit_gated": bc / A_ if gate else 0.0,
                 "coll_same_primary": on(r["clean"], S[i]), "coll_deployed_primary": on(r["clean"], F),
                 "coll_rate_limit": lc, "n": r["n"]}
            windows.append(w)
        res = {"A": A_, "windows": windows}
        for D in DURATIONS:
            covs = []
            for s0 in range(len(T)):
                end = T[s0] + (D - 1) * STEP
                if end > T[-1]:
                    break
                got = tot = 0.0
                for i in range(s0, len(T)):
                    if T[i] > end:
                        break
                    F = set()
                    for j in range(s0, i):
                        if T[i] - T[j] <= HOLD * STEP:
                            F |= S[j]
                    got += on(rows[i][1], F); tot += A_
                covs.append(got / tot)
            res[f"D{D}"] = covs
        out["attack"][f"{source}:{kind}{size:g}"] = res
    return out


def validate(results, period, csv):
    """Rebuilt clean decisions against the stored per-window CSV of the frozen run."""
    days = {r["day"] for r in results if r["period"] == period}
    W = pd.read_csv(csv, usecols=["kind", "fold", "host", "window", "size", "union_named", "union_collateral"],
                    dtype={"fold": str})
    cal = W[(W["kind"] == "calib") & (W["size"] >= ARGS.k_min)].groupby(["fold", "host"])["size"].quantile(0.99)
    W = W[(W["kind"] == "clean") & (W["size"] >= ARGS.k_min) & W["fold"].isin(days) & W["host"].isin(ROLE)]
    W = W.assign(ts=pd.to_datetime(W["window"], utc=True))
    bad = {"windows": 0, "trigger": 0, "picks": 0}
    err, fa_mine, fa_stored = 0.0, 0, 0
    for r in results:
        if r["period"] != period:
            continue
        mine = pd.DataFrame(r["clean"]).assign(ts=lambda x: pd.to_datetime(x["window"], utc=True))
        ref = W[(W["fold"] == r["day"]) & (W["host"] == r["host"])]
        m = mine.merge(ref, on="ts", how="outer", indicator=True)
        bad["windows"] += int((m["_merge"] != "both").sum())
        m = m[m["_merge"] == "both"]
        gate_ref = m["size"] >= cal[(r["day"], r["host"])]
        bad["trigger"] += int((gate_ref != m["gate"]).sum())
        bad["picks"] += int((m["union"] != m["union_named"].astype(bool)).sum())
        err = max(err, float((m["union_coll"] - m["union_collateral"]).abs().max()))
        fa_mine += int((m["gate"] & m["union"]).sum())
        fa_stored += int((gate_ref & m["union_named"].astype(bool)).sum())
    return {"mismatched": bad, "max_abs_collateral_difference": err,
            "false_alarms_rebuilt": fa_mine, "false_alarms_stored": fa_stored}


def summarize(results):
    out = {"clean": {}, "attack": {}}
    for g in ("dev", "held", "prospective"):
        for E in ("E1", "E2", "E3", "E4", "all"):
            ws = [w for r in results if group(r["day"]) == g and (E == "all" or ROLE[r["host"]] == E) for w in r["clean"]]
            if not ws:
                continue
            n = sum(w["n"] for w in ws)
            fa = [w for w in ws if w["gate"] and w["union"]]
            alone = [w for w in ws if w["union"]]
            acted = [w["rl_cut"] / w["n"] for w in ws if w["rl_acted"]]
            out["clean"][f"{g}|{E}"] = {
                "windows": len(ws), "false_alarm_rate": len(fa) / len(ws),
                "false_alarm_collateral_median": float(np.median([w["union_coll"] for w in fa])) if fa else None,
                "filters_share_of_origin_windows": sum(w["union_coll"] * w["n"] for w in fa) / n,
                "scope_alone_rate": len(alone) / len(ws),
                "scope_alone_share_of_origin_windows": sum(w["union_coll"] * w["n"] for w in alone) / n,
                "rate_limit_acting_rate": len(acted) / len(ws),
                "rate_limit_share_of_origin_windows": sum(w["rl_cut"] for w in ws) / n,
                "rate_limit_median_share_when_acting": float(np.median(acted)) if acted else None,
                "rate_limit_in_false_alarm_windows_zero": sum(w["rl_cut"] == 0 for w in fa)}
            for cfg in sorted({c for r in results for c in r["attack"]}):
                rs = [r for r in results if group(r["day"]) == g and (E == "all" or ROLE[r["host"]] == E) and cfg in r["attack"]]
                W = [w for r in rs for w in r["attack"][cfg]["windows"]]
                if not W:
                    continue
                nsum = sum(w["n"] for w in W)
                m = {k: float(np.mean([w[k] for w in W])) for k in ("gate", "same_primary", "same_scope_alone",
                     "deployed_primary", "deployed_scope_alone", "rate_limit", "rate_limit_gated")}
                for k in ("coll_same_primary", "coll_deployed_primary", "coll_rate_limit"):
                    m[k] = sum(w[k] for w in W) / nsum
                for D in DURATIONS:
                    c = [x for r in rs for x in r["attack"][cfg][f"D{D}"]]
                    m[f"attacks_{D}_windows_mean"] = float(np.mean(c))
                    m[f"attacks_{D}_windows_never_filtered"] = float(np.mean(np.array(c) == 0))
                # the paper's interval: endpoints fixed, days resampled (production_tables.cluster_ci)
                frame = pd.DataFrame({"host": [r["host"] for r in rs for _ in r["attack"][cfg]["windows"]],
                                      "fold": [r["day"] for r in rs for _ in r["attack"][cfg]["windows"]]})
                m["deployed_primary_ci95"] = cluster_ci(frame, [w["deployed_primary"] for w in W])
                m["same_primary_ci95"] = cluster_ci(frame, [w["same_primary"] for w in W])
                m["attackers"] = sorted({r["attack"][cfg]["A"] for r in rs})
                out["attack"][f"{g}|{E}|{cfg}"] = m
    return out


def require_validated(checks):
    """Do not publish attack aggregates if the frozen clean decisions differ."""
    for period, check in checks.items():
        if (any(check["mismatched"].values())
                or not np.isfinite(check["max_abs_collateral_difference"])
                or check["max_abs_collateral_difference"] > 1e-12
                or check["false_alarms_rebuilt"] != check["false_alarms_stored"]):
            raise ValueError(f"{period}: clean-window reconstruction failed: {check}")


def main():
    global ROLE, PERIODS, ASSIGNMENT, SEED
    ap = argparse.ArgumentParser()
    ap.add_argument("out", type=Path)
    ap.add_argument("--workers", type=int, default=7)
    ap.add_argument("--assignment", choices=("fixed", "resampled"), default="fixed",
                    help="fixed: one fingerprint per bot all day; resampled: reproduce the original replay")
    ap.add_argument("--seed", type=int, default=SEED)
    a = ap.parse_args()
    if a.workers < 1 or a.seed < 0:
        ap.error("--workers must be positive and --seed must be nonnegative")
    if not os.environ.get("PRODDATA") or not os.environ.get("ENDPOINT_MAP"):
        ap.error("set PRODDATA and ENDPOINT_MAP to the private export directory and endpoint mapping")
    data_root = Path(os.environ["PRODDATA"])
    ROLE = json.loads(Path(os.environ["ENDPOINT_MAP"]).read_text())
    PERIODS = {"dev": (data_root, 3, data_root / "results/rule_production_windows_rolling_origin_fleets0.05_v2.csv"),
               "prospective": (data_root / "block2", 9,
                               data_root / "block2/results/rule_production_windows_rolling_origin_fleets0.05_v2.csv")}
    ASSIGNMENT, SEED = a.assignment, a.seed
    results, checks = [], {}
    for period, (data_dir, min_days, csv) in PERIODS.items():
        t0 = time.time()
        G["recs"], dates = load_period(data_dir)
        jobs = sorted(((period, d, h) for d in dates[min_days:] for h in G["recs"]), key=lambda j: ROLE[j[2]] != "E1")
        with mp.get_context("fork").Pool(a.workers) as pool:
            part = [r for r in pool.imap_unordered(task, jobs) if r is not None]
        if not part:
            raise ValueError(f"{period}: no eligible endpoint-days")
        part.sort(key=lambda r: (r["day"], r["host"]))
        checks[period] = validate(part, period, csv)
        require_validated(checks)
        results += part
        print(period, f"{time.time() - t0:.0f}s", json.dumps(checks[period]), flush=True)
    out = {"design": __doc__.split("Usage:")[0].strip(),
           "assignment": ASSIGNMENT, "seed": SEED,
           "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
           "parameters": {**vars(ARGS), "hold_windows": HOLD, "step_minutes": 5},
           "reference_csv_sha256": {p: hashlib.sha256(csv.read_bytes()).hexdigest()
                                     for p, (_, _, csv) in PERIODS.items()},
           "validation": checks, **summarize(results)}
    a.out.write_text(json.dumps(out, indent=1, allow_nan=False) + "\n")
    print("wrote", a.out)


if __name__ == "__main__":
    main()

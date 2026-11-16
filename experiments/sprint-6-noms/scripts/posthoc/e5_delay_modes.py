"""E5 timing replay, ported from the handoff without customer identifiers.

Supply a PRIVATE JSON manifest with labels_json, requests_json, windows_csv,
attack_fingerprints_json, profile_fingerprints_json (list), attack_day, and
attacks (map of anonymous attack labels to ordered HH:MM windows).
Only aggregate metrics are exported. Input dates, paths and fingerprint IDs
stay outside this repository. Selection and timing arithmetic follow the
handoff script; raw-data execution requires the restricted exports.
"""
import sys, json, argparse
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pandas as pd
from production_tables import load
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--manifest", type=Path, required=True)
parser.add_argument("--out", type=Path, required=True)
args = parser.parse_args()
config = json.loads(args.manifest.read_text())
q = pd.DataFrame(json.load(open(config["labels_json"])))
q["att"] = q["ips_blocked"] + q["ips_unblocked_root_only"]; q["leg"] = q["ips_unblocked_other_uris"]; q["t"] = q["w"].str.slice(11, 16)
q["att2"] = q["ips_blocked"]; q["leg2"] = q["ips_unblocked_root_only"] + q["ips_unblocked_other_uris"]
r9 = pd.DataFrame(json.load(open(config["requests_json"])))
r9 = r9[r9["w"].str.startswith(config["attack_day"])].copy(); r9["t"] = r9["w"].str.slice(11, 16)
csv = config["windows_csv"]
W = load(csv); W = W[(W["kind"] == "waf") & (W["fold"] == config["attack_day"])]
nm = pd.read_csv(csv, usecols=["kind", "fold", "window", "named"], dtype={"fold": str, "named": str})
nm = nm[(nm["kind"] == "waf") & (nm["fold"] == config["attack_day"])]
W = W.merge(nm, on=["kind", "fold", "window"]); W["t"] = W["window"].astype(str).str.slice(11, 16)
e3 = pd.DataFrame(json.load(open(config["attack_fingerprints_json"])))
prof = set(pd.concat([pd.DataFrame(json.load(open(path))) for path in config["profile_fingerprints_json"]])
           .query("clientes - clientes_bloqueados_waf > 0")["ja4"])
e3["t"] = e3["janela"].str.slice(11, 16)
def selected(t):
    r = W[W["t"] == t]
    if r.empty: return set()
    r = r.iloc[0]; win = e3[e3["t"] == t]
    unseen = set(win[(~win["ja4"].isin(prof)) & (win["clientes"] >= 5) & (win["ja4"] != "-")]["ja4"])
    test = set(str(r["named"]).split(";")) - {"", "nan"}
    return unseen | (test if r["gate_origins"] else set())
out = {}
for name, wins in config["attacks"].items():
    sel = {t: selected(t) for t in wins}
    res = {}
    for mode in ("same", "next", "kept_sel", "kept_next"):
        att = leg = req = att_tot = leg_tot = req_tot = 0; a2 = a2t = l2 = l2t = 0; acc = set(); legs = []
        for i, t in enumerate(wins):
            prev = set(acc)                       # everything chosen before t
            if mode == "same": S = sel[t]
            elif mode == "next": S = sel[wins[i - 1]] if i else set()
            elif mode == "kept_sel": S = prev | sel[t]
            else: S = prev
            acc |= sel[t]
            lab = q[q["t"] == t]; rr = r9[r9["t"] == t]
            a = lab.loc[lab["fp"].isin(S), "att"].sum(); l = lab.loc[lab["fp"].isin(S), "leg"].sum()
            att += a; leg += l; att_tot += lab["att"].sum(); leg_tot += lab["leg"].sum()
            req += rr.loc[rr["fp"].isin(S), "requests"].sum(); req_tot += rr["requests"].sum()
            legs.append(round(l / max(lab["leg"].sum(), 1), 5))
            m = lab["fp"].isin(S); a2 += lab.loc[m, "att2"].sum(); a2t += lab["att2"].sum(); l2 += lab.loc[m, "leg2"].sum(); l2t += lab["leg2"].sum()
        res[mode] = {"pairs": round(att / att_tot, 4), "legit": round(leg / leg_tot, 5), "requests": round(req / req_tot, 4),
                     "legit_max_window": max(legs), "edge_label_pairs": round(a2 / a2t, 4), "edge_label_legit": round(l2 / l2t, 5)}
    out[name] = res
    print(name); [print(" ", m, res[m]) for m in ("same", "next", "kept_sel", "kept_next")]
json.dump(out, open(args.out, "w"), indent=1)

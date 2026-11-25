#!/usr/bin/env python3
"""English figures for the NOMS submission (papers/http-session-noms).

Generates the DATA figures. Fig. 1 (fig1_scoping) is a draw.io schematic and is NOT
produced here -- see figures/README.md and figures/src-drawio/.
  fig6_stops.png      -- Fig. 2 (Section V-C), one column at print size: what the binomial
                         configuration stops per endpoint, by botnet size, against what the
                         scope alone would block, with the gap the trigger lets through shaded.
  fig4_operating.png  -- Fig. 3 (Section V-D), one column at print size: operating points
                         on production traffic, false alarms against blocked share (test
                         days and the cross-fitted calibration), with the 1% budget.
  fig5_latency.png    -- Fig. 4 (Appendix D), single column: the cost of both layers.

Run from the repository root:
    experiments/.venv/bin/python papers/http-session-noms/figures/make_figures_en.py
"""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Monochrome palette, matched to Fig. 1 (the draw.io schematic):
#   INK   -- the main series                 (the schematic's black)
#   MUTED -- comparison series
#   NOTE  -- annotations and reference lines (the gray of Fig. 1's notes)
# No hue: contrast comes from tone and marker, so the figures survive grayscale
# printing and color-blind readers. NAVY2, GRAY, GRAYB and TXT are unused.
NAVY = "#1a1a1a"      # INK   (historical name, kept so the function bodies need not change)
NAVY2 = "#4d4d4d"
GRAY = "#ececec"
GRAYB = "#9a9a9a"
BAR_GRAY = "#bdbdbd"  # MUTED
CHANCE = "#595959"    # NOTE
TXT = "#222222"

OUT = os.path.dirname(os.path.abspath(__file__))
SHOW_XFIT = False   # round 6: Fig. 3 shows the in-sample operating points only


def fig_operating(root):
    """False alarms against blocked share on production traffic, 100 attackers.

    Drawn at print size (one column, 3.45 in), with one rule per visual attribute so that
    the legend is read once: the shape is the scope, a black marker sits behind a trigger
    (the origin trigger, or the Omega trigger for the base rule), a white one is the scope alone
    as its own trigger, and a gray one is the cross-fitted calibration, joined by an arrow
    to its in-sample point. The dashed line is the 1% false-alarm budget. The held-out day
    is left to Tables IV and VI: its trigger barely fired, so its zero rates would sit in the
    best corner of the plot.
    """
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch
    T = json.load(open(os.path.join(root, "experiments/sprint-6-noms/results/production_tables.json")))
    shape = {"base": ("o", 16), "binomial": ("D", 13), "beta": ("s", 14), "z": ("^", 18), "unseen": ("v", 18)}
    points = [  # (scope, behind a gate?, run, key, cross-fitted run or None)
        ("base", True, "base", "enrichment|omega", "xfit"),
        ("binomial", True, "fleets", "union|origins", "xfit_fleets"),
        ("beta", True, "od", "union|origins", "xfit_od"),
        ("z", True, "base", "zcal|origins", "xfit"),
        ("unseen", True, "base", "unseen|origins", None),
        ("binomial", False, "fleets", "union|none", "xfit_fleets"),
        ("beta", False, "od", "union|none", "xfit_od"),
        ("unseen", False, "fleets", "unseen|none", None),
    ]

    def style(gated, xfit):
        # black: behind a trigger; white: the scope alone; gray: cross-fitted, whichever the trigger
        if xfit:
            return dict(facecolors=BAR_GRAY, edgecolors=NAVY, linewidths=0.6)
        return dict(facecolors=NAVY if gated else "white", edgecolors=NAVY, linewidths=0.6 if gated else 0.8)

    fig, axes = plt.subplots(1, 2, figsize=(3.45, 2.5), sharey=True)
    for ax, cell, title in ((axes[0], "new:A100", "new stacks"), (axes[1], "shared:A100", "shared stacks")):
        ax.axvline(1, color=CHANCE, lw=0.7, ls=(0, (3, 2)), zorder=1)
        for scope, gated, run, key, xrun in points:
            mk, s = shape[scope]
            r = T["test_days"][run]["all"][key]
            p0 = (max(r["clean_rate"] * 100, 0.01), r[cell]["blocked"] * 100)
            ax.scatter(*p0, marker=mk, s=s, zorder=3, **style(gated, False))
            if scope == "z" and gated:
                off, ha, va = ((-4.5, -0.5), "right", "center") if cell.startswith("new") else ((0, 4.5), "center", "bottom")
                ax.annotate("$z$-score", xy=p0, xytext=off, textcoords="offset points",
                            fontsize=6.2, ha=ha, va=va, color=NAVY)
            if xrun and SHOW_XFIT:
                r1 = T["test_days"][xrun]["all"][key]
                p1 = (max(r1["clean_rate"] * 100, 0.01), r1[cell]["blocked"] * 100)
                ax.annotate("", xy=p1, xytext=p0, zorder=2,
                            arrowprops=dict(arrowstyle="-|>", color=CHANCE, lw=0.5, mutation_scale=5,
                                            shrinkA=2.5, shrinkB=2.5))
                ax.scatter(*p1, marker=mk, s=s, zorder=3, **style(gated, True))
        ax.set_xscale("log")
        ax.set_xlim(0.007, 15)
        ax.set_xticks([0.01, 0.1, 1, 10])
        ax.set_xticklabels(["0.01", "0.1", "1", "10"])
        ax.set_ylim(-4, 100)
        ax.set_title(title, fontsize=7, pad=2)
        ax.tick_params(labelsize=6.5, length=2, pad=1.5)
        ax.grid(alpha=.25, lw=0.5, zorder=0)
        ax.spines[["top", "right"]].set_visible(False)
    axes[0].set_ylabel("% of 100 attackers blocked", fontsize=7, labelpad=1)
    axes[0].text(0.8, 99, "1% budget", fontsize=6.5, ha="right", va="top", color=CHANCE)

    def handle(mk, s, **kw):
        return Line2D([], [], ls="", marker=mk, markersize=(s ** 0.5) * 0.95, **kw)
    # left column: one shape per scope; right column: the three fills, as swatches no point uses
    h = [handle(*shape[k], mfc=NAVY, mec=NAVY) for k in ("base", "binomial", "beta", "z", "unseen")]
    h += [Patch(facecolor=NAVY, edgecolor=NAVY, lw=0.6), Patch(facecolor="white", edgecolor=NAVY, lw=0.8)]
    l = ["base rule ($\\Omega$ trigger)", "binomial", "beta-binomial$^{*}$", "$z$-score, calibrated", "unseen filter",
         "black: behind a trigger", "white: the scope alone$^{*}$"]
    # one x label for both panels, just under the tick labels, then a clear gap before the legend
    fig.tight_layout(pad=0.2, w_pad=0.5, rect=(0, 0.29, 1, 1))
    y0 = axes[0].get_position().y0
    fig.text(0.5, y0 - 0.105, "false alarms (% of clean windows)", ha="center", va="center", fontsize=6.8)
    fig.legend(h, l, loc="upper center", bbox_to_anchor=(0.5, y0 - 0.125), ncol=2, fontsize=6.3, borderpad=0.2,
               frameon=False, handletextpad=0.3, columnspacing=0.8, labelspacing=0.3)
    out = os.path.join(OUT, "fig4_operating.png")
    fig.savefig(out, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"OK: {out}")


def fig_stops(root):
    """What the binomial configuration stops per endpoint, by botnet size (test days).

    Drawn at print size (one column, 3.45 in) from the `sweep` block of
    production_tables.json: run `fleets`, scope union, origin trigger, 25 new stacks.
    Two lines per endpoint, what the scope alone would block in every window and what the
    configuration stops, and the shaded gap between them, what the trigger lets through.
    The trigger's own rate and the shared stacks are left to the text and Table V, so that
    every line is a share of the botnet. The absolute sizes (25-1,000) and the relative ones
    (a tenth, half and the whole median window) share the x axis in attackers per window.
    """
    T = json.load(open(os.path.join(root, "experiments/sprint-6-noms/results/production_tables.json")))
    S = T["sweep"]["fleets"]
    n0 = {"E1": 2983, "E2": 62, "E3": 41, "E4": 20}          # Table V, median origins per window
    names = {"E1": "E1, beacons (busiest)", "E2": "E2, web console", "E3": "E3, API", "E4": "E4, sign-on"}
    fig, axes = plt.subplots(2, 2, figsize=(3.45, 2.6), sharex=True, sharey=True)
    for ax, e in zip(axes.flat, ("E1", "E2", "E3", "E4")):
        pts = [(A, f"M25:A{A}") for A in (25, 50, 100, 250, 1000)]
        pts += [(x * n0[e], f"M25:x{x:g}") for x in (0.1, 0.5, 1)]
        pts.sort()
        xs = [p[0] for p in pts]
        alone = [S[e][f"new:{k}"]["blocked_alone"] * 100 for _, k in pts]
        conf = [S[e][f"new:{k}"]["blocked"] * 100 for _, k in pts]
        # what the scope names but the trigger lets through: the paper's point on the busiest endpoint
        ax.fill_between(xs, conf, alone, where=[a > c for a, c in zip(alone, conf)], interpolate=True,
                        color="#d6d6d6", lw=0, zorder=1)
        ax.plot(xs, alone, "--", color=CHANCE, lw=1.2, label="the scope without the trigger")
        ax.plot(xs, conf, "o-", color=NAVY, lw=1.2, ms=2.6, label="with the trigger")
        ax.plot([0.1 * n0[e]], [-6], marker="^", color=NAVY, mfc="white", mew=0.8, ms=5.5, clip_on=False, zorder=4)
        ax.set_xscale("log")
        ax.set_xlim(1.5, 4000)
        ax.set_ylim(-6, 100)
        ax.set_title(names[e], fontsize=7, pad=2)
        ax.grid(alpha=.25, lw=0.5, zorder=0)
        ax.tick_params(labelsize=6.5, length=2, pad=1.5)
        ax.spines[["top", "right"]].set_visible(False)
    axes[0, 0].text(520, 62, "lost\nto the\ntrigger", fontsize=6, ha="center", va="center", color=NAVY, zorder=5)
    for ax in axes[1]:
        ax.set_xlabel("attackers per window", fontsize=7, labelpad=1)
    for ax in axes[:, 0]:
        ax.set_ylabel("% of the botnet", fontsize=7, labelpad=1)
    h, l = axes[0, 0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", bbox_to_anchor=(0.5, -0.005), ncol=2, fontsize=6.5,
               frameon=False, handlelength=2.2, columnspacing=1.2)
    fig.tight_layout(pad=0.2, h_pad=0.5, w_pad=0.4, rect=(0, 0.07, 1, 1))
    out = os.path.join(OUT, "fig6_stops.png")
    fig.savefig(out, dpi=300, bbox_inches="tight")
    plt.close(fig)
    e1 = S["E1"]
    print(f"OK: {out} | E1 new A100 alone {e1['new:M25:A100']['blocked_alone']:.3f} conf {e1['new:M25:A100']['blocked']:.3f}"
          f" | x0.1 alone {e1['new:M25:x0.1']['blocked_alone']:.3f} conf {e1['new:M25:x0.1']['blocked']:.3f}")


def fig_latency(root):
    import json
    d = json.load(open(os.path.join(
        root, "experiments/sprint-6-noms/results/latency_summary.json")))["by_window_size"]
    sizes = sorted((int(k) for k in d), key=int)
    adm = [d[str(n)]["admission_p50_us"] / 1e6 for n in sizes]
    adm_c = [d[str(n)]["admission_class_p50_us"] / 1e6 for n in sizes]
    sym_c = [d[str(n)]["class_total_s"] for n in sizes]
    sym_n = [n for n in sizes if "symbolic_total_s" in d[str(n)]]
    sym = [d[str(n)]["symbolic_total_s"] for n in sym_n]

    # drawn at the width it prints (one column), with fonts of about 7 pt
    fig, ax = plt.subplots(figsize=(3.45, 1.9))
    # comparison series (grey): pair edges enumerated or materialized
    ax.loglog(sym_n, sym, "s-", color=BAR_GRAY, lw=1.2, ms=3.6, markeredgecolor="#777",
              label="aggregation, pair edges")
    ax.loglog(sizes, adm, "o-", color=BAR_GRAY, lw=1.2, ms=3.6, markeredgecolor="#777",
              label="admission, pair edges")
    # proposed series (ink): equality-based sub-relations kept as classes
    ax.loglog(sizes, sym_c, "s-", color=NAVY, lw=1.2, ms=3.6,
              label="aggregation, class counts")
    ax.loglog(sizes, adm_c, "o-", color=NAVY, lw=1.2, ms=3.6,
              label="admission, class counts")

    # reference slopes anchored on the first point of each series
    def ref(xs, y0, k, color, label, dy):
        x = [xs[0], xs[-1]]
        y = [y0, y0 * (x[1] / x[0]) ** k]
        ax.loglog(x, y, ":", color=color, lw=0.8, alpha=.7)
        ax.text(x[1], y[1] * dy, label, color=color, fontsize=6.3, ha="right",
                style="italic")
    ref(sym_n, sym[0], 2, "#777", "slope 2", 2.2)
    ref(sizes, sym_c[0], 1, NAVY, "slope 1", 2.2)
    ref(sizes, adm[0], 1, "#777", "slope 1", 2.2)
    ax.text(sizes[-1], adm_c[-1] * 3.0, "constant", color=NAVY, fontsize=6.3,
            ha="right", style="italic")
    ax.set_ylim(bottom=min(adm_c) / 4)     # room under the flat series
    ax.set_yticks([1e-6, 1e-4, 1e-2, 1, 100])   # one label every two decades

    ax.set_xlabel("active sessions in the window, $|S_W|$", fontsize=7, labelpad=1)
    ax.set_ylabel("latency (s)", fontsize=7, labelpad=1)
    ax.tick_params(labelsize=6.5, length=2, pad=1.5)
    ax.grid(True, which="both", alpha=.25, lw=0.5)
    ax.spines[["top", "right"]].set_visible(False)
    # legend below the axes, with a clear gap after the x label
    h, l = ax.get_legend_handles_labels()
    fig.tight_layout(pad=0.2, rect=(0, 0.2, 1, 1))
    y0 = ax.get_position().y0
    fig.legend(h, l, loc="upper center", bbox_to_anchor=(0.5, y0 - 0.15), ncol=2, fontsize=6.3,
               frameon=False, handletextpad=0.3, columnspacing=1.0, labelspacing=0.3, borderpad=0.2)
    out = os.path.join(OUT, "fig5_latency.png")
    fig.savefig(out, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"OK: {out}")


if __name__ == "__main__":
    root = os.path.abspath(os.path.join(OUT, "..", "..", ".."))
    # Fig. 1 (fig1_scoping) is a draw.io schematic, not generated here.
    # Sources live in src-drawio/; see README.md for the export procedure.
    fig_stops(root)
    fig_operating(root)
    fig_latency(root)


def fig_scoping(root=None):
    """Fig. 1: the pipeline per endpoint and five-minute window, drawn in code.

    Replaces the earlier schematic (round 6, 9 Nov 2026): same flow and the same aspect
    ratio (two columns, 7.17 x 1.84 in), without the session-ontology box and the STIX
    label, and with the count query and the class sizes merged into one "counts" box.
    """
    from matplotlib.patches import Rectangle, Ellipse
    W, H = 7.17, 7.17 / 3.62
    fig = plt.figure(figsize=(W, H))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100 * H / W)
    ax.axis("off")
    fs, tfs = 6.2, 6.7

    def box(x0, y0, x1, y1, title, body, title_style="bold", body_italic_last=False, title_inline=None):
        ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fill=False, ec=NAVY, lw=1.0, zorder=2))
        cx = (x0 + x1) / 2
        lines = body.split("\n") if body else []
        n = len(lines) + (1 if title else 0)
        lh = 2.1
        ytop = (y0 + y1) / 2 + (n - 1) * lh / 2
        y = ytop
        if title:
            ax.text(cx, y, title, ha="center", va="center", fontsize=tfs, fontweight="bold", color=NAVY)
            y -= lh
        for i, l in enumerate(lines):
            st = "italic" if (body_italic_last and i == len(lines) - 1) else "normal"
            ax.text(cx, y, l, ha="center", va="center", fontsize=fs, color=NAVY, style=st)
            y -= lh

    def arrow(x0, y0, x1, y1, dashed=False):
        ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                    arrowprops=dict(arrowstyle="-|>", color=CHANCE if dashed else NAVY, lw=0.9,
                                    ls=(0, (3, 2)) if dashed else "-", mutation_scale=7,
                                    shrinkA=0, shrinkB=0), zorder=3)

    yb0, yb1 = 10.2, 21.9          # main row
    ym = (yb0 + yb1) / 2
    # round 10: the title moved to the caption; the top band holds the rule's branch, a fingerprint
    # absent from the profile blocked without the trigger (dashed), which the binomial configuration
    # runs behind the trigger instead
    yt = 24.0
    ax.plot([23.4, 23.4], [yb1, yt], color=NAVY, lw=0.9, ls=(0, (3, 2)), zorder=3)
    ax.plot([23.4, 89.9], [yt, yt], color=NAVY, lw=0.9, ls=(0, (3, 2)), zorder=3)
    ax.annotate("", xy=(89.9, yb1), xytext=(89.9, yt),
                arrowprops=dict(arrowstyle="-|>", color=NAVY, lw=0.9, ls=(0, (3, 2)), mutation_scale=7,
                                shrinkA=0, shrinkB=0), zorder=3)
    ax.text(56.6, yt + 1.35, "two-path rule: a fingerprint absent from the profile at $\\geq k_{\\min}$ origins is blocked without the trigger",
            ha="center", va="center", fontsize=fs, color=NAVY, style="italic")
    # access log as a cylinder
    cx0, cx1, er = 0.5, 12.8, 1.2
    ax.add_patch(Rectangle((cx0, yb0 + er), cx1 - cx0, yb1 - yb0 - 2 * er, fc="white", ec="none", zorder=1))
    ax.plot([cx0, cx0], [yb0 + er, yb1 - er], color=NAVY, lw=1.0, zorder=2)
    ax.plot([cx1, cx1], [yb0 + er, yb1 - er], color=NAVY, lw=1.0, zorder=2)
    ax.add_patch(Ellipse(((cx0 + cx1) / 2, yb1 - er), cx1 - cx0, 2 * er, fill=False, ec=NAVY, lw=1.0, zorder=2))
    from matplotlib.patches import Arc
    ax.add_patch(Arc(((cx0 + cx1) / 2, yb0 + er), cx1 - cx0, 2 * er, theta1=180, theta2=360, ec=NAVY, lw=1.0, zorder=2))
    for i, l in enumerate(["access log", "per request: JA4,", "source, endpoint"]):
        ax.text((cx0 + cx1) / 2, ym + 1.4 - i * 2.1, l, ha="center", va="center", fontsize=fs, color=NAVY)
    # counts, trigger, scope
    box(15.6, yb0, 31.2, yb1, "counts", "origins per JA4 $c(f)$\nand origins $n$")
    box(34.0, yb0, 52.6, yb1, "trigger", "distinct origins $\\geq$ p99\nand $\\geq k_{\\min}$\notherwise: no action",
        body_italic_last=True)
    box(55.4, yb0, 75.2, yb1, "scope", "every $f$ with\n$c(f)/n \\geq \\rho\\, b(f)$ and\n$\\Pr[X\\geq c(f)] < \\lambda_e/|F|$,\n$\\cup$ unseen, $-$ known fleets")
    # outcomes
    box(80.4, 13.4, 99.4, yb1, "block", "only the clients\non $f$ at $e$")
    box(80.4, 0.6, 99.4, 9.0, None, "nothing selected:\nrate-limit or challenge\nevery client")
    # calibration
    box(15.6, 0.6, 75.2, 7.6, "calibration on attack-free days, no labels",
        "the profile $b(f)$, the p99 thresholds,\nthe largest $\\lambda_e\\leq 0.01$ at which at most 1% of windows get a filter, and the known fleets")
    # arrows of the main flow
    arrow(cx1, ym, 15.6, ym)
    arrow(31.2, ym, 34.0, ym)
    arrow(52.6, ym, 55.4, ym)
    ax.plot([75.2, 77.8], [ym, ym], color=NAVY, lw=0.9, zorder=3)
    arrow(77.8, ym, 80.4, ym)
    ax.plot([77.8, 77.8], [ym, 4.8], color=NAVY, lw=0.9, zorder=3)
    arrow(77.8, 4.8, 80.4, 4.8)
    # calibration feeds the trigger and the scope
    arrow(43.3, 7.6, 43.3, yb0, dashed=True)
    arrow(65.3, 7.6, 65.3, yb0, dashed=True)
    out = os.path.join(OUT, "fig1_scoping.png")
    fig.savefig(out, dpi=300)
    plt.close(fig)
    print(f"OK: {out}")

"""fig1_r48.py: Fig. 1 with the boxes in words (round 48, 16 Nov 2026). Same frame, palette and size as
make_figures_en.r13.py's fig_scoping; the formulas stay in Section III-C."""
import importlib.util, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("mf", os.path.join(HERE, "make_figures_en.r13.py"))
mf = importlib.util.module_from_spec(spec); spec.loader.exec_module(mf)
plt, NAVY, CHANCE = mf.plt, mf.NAVY, mf.CHANCE
from matplotlib.patches import Rectangle, Ellipse, Arc

def fig_scoping_words(out_dir):
    W, H = 7.17, 7.17 / 3.62
    fig = plt.figure(figsize=(W, H)); ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 100); ax.set_ylim(0, 100 * H / W); ax.axis("off")
    fs, tfs = 6.2, 6.7
    def box(x0, y0, x1, y1, title, body, body_italic_last=False):
        ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fill=False, ec=NAVY, lw=1.0, zorder=2))
        cx = (x0 + x1) / 2; lines = body.split("\n") if body else []; n = len(lines) + (1 if title else 0)
        lh = 2.1; y = (y0 + y1) / 2 + (n - 1) * lh / 2
        if title:
            ax.text(cx, y, title, ha="center", va="center", fontsize=tfs, fontweight="bold", color=NAVY); y -= lh
        for i, l in enumerate(lines):
            st = "italic" if (body_italic_last and i == len(lines) - 1) else "normal"
            ax.text(cx, y, l, ha="center", va="center", fontsize=fs, color=NAVY, style=st); y -= lh
    def arrow(x0, y0, x1, y1, dashed=False):
        ax.annotate("", xy=(x1, y1), xytext=(x0, y0), arrowprops=dict(arrowstyle="-|>", color=CHANCE if dashed else NAVY, lw=0.9,
                    ls=(0, (3, 2)) if dashed else "-", mutation_scale=7, shrinkA=0, shrinkB=0), zorder=3)
    yb0, yb1 = 10.2, 21.9; ym = (yb0 + yb1) / 2
    xc0, xc1 = 15.6, 26.8     # counts
    xt0, xt1 = 29.6, 49.6     # trigger
    xs0, xs1 = 52.4, 76.0     # scope
    # the two-path rule's first path (post hoc): from the counts to the block, without the trigger
    yt = 24.0; xcc = (xc0 + xc1) / 2
    ax.plot([xcc, xcc], [yb1, yt], color=NAVY, lw=0.9, ls=(0, (3, 2)), zorder=3)
    ax.plot([xcc, 89.9], [yt, yt], color=NAVY, lw=0.9, ls=(0, (3, 2)), zorder=3)
    ax.annotate("", xy=(89.9, yb1), xytext=(89.9, yt), arrowprops=dict(arrowstyle="-|>", color=NAVY, lw=0.9, ls=(0, (3, 2)),
                mutation_scale=7, shrinkA=0, shrinkB=0), zorder=3)
    ax.text((xcc + 89.9) / 2, yt + 1.35, "two-path rule: a fingerprint absent from the profile is blocked once 5 origins present it, without the trigger",
            ha="center", va="center", fontsize=fs, color=NAVY, style="italic")
    # access log
    cx0, cx1, er = 0.5, 12.8, 1.2
    ax.add_patch(Rectangle((cx0, yb0 + er), cx1 - cx0, yb1 - yb0 - 2 * er, fc="white", ec="none", zorder=1))
    ax.plot([cx0, cx0], [yb0 + er, yb1 - er], color=NAVY, lw=1.0, zorder=2); ax.plot([cx1, cx1], [yb0 + er, yb1 - er], color=NAVY, lw=1.0, zorder=2)
    ax.add_patch(Ellipse(((cx0 + cx1) / 2, yb1 - er), cx1 - cx0, 2 * er, fill=False, ec=NAVY, lw=1.0, zorder=2))
    ax.add_patch(Arc(((cx0 + cx1) / 2, yb0 + er), cx1 - cx0, 2 * er, theta1=180, theta2=360, ec=NAVY, lw=1.0, zorder=2))
    for i, l in enumerate(["access log", "per request: JA4,", "source, endpoint"]):
        ax.text((cx0 + cx1) / 2, ym + 1.4 - i * 2.1, l, ha="center", va="center", fontsize=fs, color=NAVY)
    box(xc0, yb0, xc1, yb1, "counts", "origins per\nfingerprint in\nthe window")
    box(xt0, yb0, xt1, yb1, "trigger", "the window's origins\nreach 5 and their\nattack-free 99th percentile\notherwise: no action", body_italic_last=True)
    box(xs0, yb0, xs1, yb1, "scope", "fingerprints over-represented\nvs. the profile (binomial test)\nor absent from it,\nminus known fleets")
    box(80.4, 13.4, 99.4, yb1, "block", "only the clients on\nthe selected fingerprints")
    box(80.4, 0.6, 99.4, 9.0, None, "nothing selected:\nrate-limit or challenge\nevery client")
    box(xc0, 0.6, xs1, 7.6, "calibration on attack-free days, no labels",
        "the endpoint's fingerprint profile, the trigger's 99th percentile, the binomial test's level\n(at most 1% of windows get a filter) and the known fleets")
    arrow(cx1, ym, xc0, ym); arrow(xc1, ym, xt0, ym); arrow(xt1, ym, xs0, ym)
    ax.plot([xs1, 77.8], [ym, ym], color=NAVY, lw=0.9, zorder=3); arrow(77.8, ym, 80.4, ym)
    ax.plot([77.8, 77.8], [ym, 4.8], color=NAVY, lw=0.9, zorder=3); arrow(77.8, 4.8, 80.4, 4.8)
    arrow((xt0 + xt1) / 2, 7.6, (xt0 + xt1) / 2, yb0, dashed=True); arrow((xs0 + xs1) / 2, 7.6, (xs0 + xs1) / 2, yb0, dashed=True)
    out = os.path.join(out_dir, "fig1_scoping.png"); fig.savefig(out, dpi=300); plt.close(fig); print("OK:", out)

if __name__ == "__main__":
    fig_scoping_words(sys.argv[1] if len(sys.argv) > 1 else HERE)

# Current manuscript figures

See the [illustrated reading guide](../../../docs/figures.md) for the meaning of each figure and the [table guide](../../../docs/tables.md) for Tables I–VIII.

| Printed number | Image | Generator |
|---|---|---|
| Fig. 1: filtering pipeline | [fig1_scoping.png](fig1_scoping.png) | [fig1_r48.py](fig1_r48.py) |
| Fig. 2: coverage lost to the trigger | [fig6_stops.png](fig6_stops.png) | `fig_stops` in [make_figures_en.r13.py](make_figures_en.r13.py) |

The historical filename `fig6_stops.png` represents **Fig. 2**. Both current figures are generated with Matplotlib; the previous draw.io instructions and four-figure numbering describe an earlier manuscript.

From the repository root:

```sh
python3 scripts/regenerate_figures.py --out build/figures
```

Dependencies are pinned in [requirements-figures.txt](../../../experiments/requirements-figures.txt). Fig. 2 reads `sweep.fleets` in [production_tables.json](../../../experiments/sprint-6-noms/results/production_tables.json). Regeneration writes to a separate directory so the manuscript inputs remain available for comparison.

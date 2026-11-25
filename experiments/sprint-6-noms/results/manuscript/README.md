# Submitted table snapshots

`tables.json` and `table-1.csv` through `table-8.csv` transcribe all eight tables,
with notes, labels and the submitted-source hash. The overview is Table III;
prospective variants are Table V and real attacks are Table VI. Table-specific
LaTeX blocks are retained; the full manuscript is omitted from this checkout.

`audit.json` records 217 numerical comparisons with saved reductions and their
coverage gaps. These comparisons are distinct from transcription and from
reexecuting restricted production traffic.

`make tables` regenerates CSVs and the audit record from the public snapshot.
`make check` verifies their consistency and compares supported cells with saved
reductions. Comparing against the frozen TeX is a separate optional local check;
see the [reproduction guide](../../../../docs/reproduction.md).

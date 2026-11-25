# Current manuscript exports

`tables.json` and `table-1.csv` through `table-8.csv` transcribe all current tables
in source order, with notes, labels and the manuscript hash. The overview is
Table III; prospective variants are Table V and real attacks are Table VI.

`audit.json` checks 217 numerical cells against saved experimental reductions
and records the current source hash, checked cells and coverage gaps. The table
exports themselves are transcriptions, not independent experimental reproduction.

Regenerate with `make tables` and verify with `make check`, from the repository
root. Historical r53 exports remain unchanged in `../r53/`.

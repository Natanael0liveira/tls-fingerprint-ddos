# Implementation map

| Function | Source |
|---|---|
| Load aggregate operator exports; construct windows; inject botnets; evaluate scopes/triggers | `experiments/sprint-6-noms/scripts/rule_detection_production.py` |
| Reduce per-window runs into anonymized tables | `experiments/sprint-6-noms/scripts/production_tables.py` |
| Evaluate generated scopes | `symbolic_detector.py`, `unseen_synth.py` in the same directory |
| Profile calibration | `level_calibration.py`, `floor_bands.py` |
| Pre-registered report | `block_report.py` |
| Current table checks | `audit_paper.py` |
| Sustained bots and per-fingerprint cap | `scripts/posthoc/sustained_ratelimit.py` in Sprint 6; fixed assignments by default, historical resampling via a flag |
| Submission and archive integrity | `scripts/check_release.py`, `scripts/package_submission.py` at the repository root |
| Historical count-query compilation | `compile_counts.py`, `experiments/common/kg_ontology.py`, `ontology/` |

The evaluation imports modules in earlier sprint and pillar directories. Their paths remain stable to preserve reproduction. Compilation/ontology and STIX checks are implementation diagnostics, separate from the manuscript’s empirical results.

The algorithm is assessed offline. E5 compares selection-window, one-window-late, and persistent-to-end application. The study does not measure production deployment latency or service availability. Old latency reports should not be treated as deployment evidence.

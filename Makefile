PYTHON ?= python3
EXPERIMENT_PYTHON ?= experiments/.venv/bin/python

.PHONY: check tables artifact submission test

check:
	$(PYTHON) scripts/check_release.py
	$(PYTHON) scripts/export_tables.py --check
	$(PYTHON) experiments/sprint-6-noms/scripts/audit_paper.py

tables:
	$(PYTHON) scripts/export_tables.py
	$(PYTHON) experiments/sprint-6-noms/scripts/audit_paper.py --out experiments/sprint-6-noms/results/manuscript/audit.json

artifact:
	$(PYTHON) scripts/package_submission.py
	$(PYTHON) scripts/check_release.py

submission: artifact

test:
	$(EXPERIMENT_PYTHON) -m unittest discover -s experiments/sprint-6-noms/scripts/posthoc -p test_sustained_ratelimit.py -v

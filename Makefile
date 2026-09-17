.PHONY: test validate summarize external-check all

test:
	python -m unittest discover -s tests -v

validate:
	python scripts/validate_results.py

summarize:
	python scripts/summarize_live_runs.py

external-check:
	python scripts/verify_external_artifacts.py

all: test validate summarize external-check

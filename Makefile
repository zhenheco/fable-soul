.PHONY: check test validate

check: validate test

validate:
	python3 scripts/validate_skill.py

test:
	python3 -m unittest discover -s tests -v

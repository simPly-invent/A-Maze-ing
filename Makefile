VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
COMP := $(PYTHON) a_maze_ing.py
INSTALL := python3 -m venv .venv && $(PIP) install -r requirements.txt
PATH_PY_CACHE := maze/__pycache__ .venv


install :
	$(INSTALL)

run:
	$(COMP)

clean:
	rm -rf $(PATH_PY_CACHE)

lint:
	flake8 . && mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	flake8 . && mypy . --strict
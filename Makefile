VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
COMP := $(PYTHON) a_maze_ing.py
INSTALL := python3 -m venv .venv && $(PIP) install -r requirements.txt
PATH_PY_CACHE := maze/__pycache__


install :
	$(INSTALL)

run:
	$(COMP)

clean:
	rm -r $(PATH_PY_CACHE)
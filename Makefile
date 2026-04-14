VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
COMP := $(PYTHON) a_maze_ing.py
INSTALL := python3 -m venv .venv && $(PIP) install -r requirements.txt
BUILD := poetry build 
PATH_PY_CACHE := maze/__pycache__ .venv
PATH_PY_DIST := mazegen/dist

all:
	make install && make run

install :
	$(INSTALL)

run:
	$(COMP)

build:
	$(BUILD)
	mv dist mazegen
	

clean:
	rm -rf $(PATH_PY_CACHE) $(PATH_PY_DIST)

lint:
	flake8 . 
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	flake8 .
	mypy . --strict

debug:
	python3 -m pdb a_maze_ing.py

.PHONY: install run debug build clean lint lint-strict
VENV := .venv
PYTHON := $(VENV)/bin/python
COMP := python3 a_maze_ing.py
ENV := .venv/bin/activate
CREATE_VENV := python3 -m venv .venv 
SHELL := /bin/bash


install :
	$(CREATE_VENV)
	source $(ENV)
	pip install -r requirements.txt

run:
	$(COMP)

test : install
	$(PYTHON) -m pytest ./tests/   
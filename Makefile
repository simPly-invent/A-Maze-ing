VENV := .venv
PYTHON := $(VENV)/bin/python

$(PYTHON) : python3 -m venv $(VENV)

install : $(PYTHON)
	$(PYTHON) -m pip install -r requirements.txt

run: 

test : install
	$(PYTHON) -m pytest ./tests/   
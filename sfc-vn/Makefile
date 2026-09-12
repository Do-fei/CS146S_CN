PYTHON ?= python3
DIST := dist/city11.sfc

.PHONY: all rom web test clean

all: rom web

rom:
	$(PYTHON) tools/build_rom.py -o $(DIST)

web:
	$(PYTHON) tools/export_web.py

test:
	$(PYTHON) -m pytest -q

clean:
	rm -rf dist __pycache__ game/__pycache__ tools/__pycache__ tests/__pycache__ .pytest_cache

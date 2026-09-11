PYTHON ?= python3
DIST := dist/yuejianqiao.sfc

.PHONY: all rom preview test clean

all: rom

rom:
	$(PYTHON) tools/build_rom.py -o $(DIST)

preview:
	$(PYTHON) tools/preview.py

test:
	$(PYTHON) -m pytest -q

clean:
	rm -rf dist __pycache__ game/__pycache__ tools/__pycache__ tests/__pycache__ .pytest_cache

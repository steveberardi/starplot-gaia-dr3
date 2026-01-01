PYTHONPATH=./src/
PYTHON=./venv/bin/python

REPO_NAME=starplot-gaia-edr3

VERSION=$(shell ./venv/bin/python -c 'from build import __version__; print(__version__)')
VERSION_CHECK=$(shell gh release list \
		-R steveberardi/$(REPO_NAME) \
		--limit 1000 \
		--json tagName \
		--jq '.[] | select(.tagName == "v$(VERSION)")' | wc -c)

GAIA_SOURCE_PATH=/Volumes/Blue2TB/gaia/gdr3/gaia_source/


export STARPLOT_DATA_PATH=./data/

# Development ------------------------------------------
install: venv/bin/activate

format: venv/bin/activate
	@$(PYTHON) -m ruff format src/*.py $(ARGS)
	@$(PYTHON) -m ruff check src/*.py --fix $(ARGS)

venv/bin/activate: requirements.txt
	python -m venv venv
	./venv/bin/pip install -r requirements.txt

shell: venv/bin/activate
	$(PYTHON)

clean:
	rm -rf __pycache__
	rm -rf venv
	rm -rf build

build: venv/bin/activate
	rm -rf build
	rm -f build.log
	@mkdir -p build
	$(PYTHON) build.py

# Create catalog of mag 6 to 18 and 25% sampling rate
build-18: venv/bin/activate
	rm -rf /Volumes/starship500/build/gaia-18
	rm -f build.log
	mkdir -p /Volumes/starship500/build/gaia-18
	$(PYTHON) src/build.py \
		--source $(GAIA_SOURCE_PATH) \
		--destination /Volumes/starship500/build/gaia-18/ \
		--num_workers 10 \
		--nside 2 \
		--mag_min 6 \
		--mag_max 18 \
		--sample_rate 0.25

squash-18: venv/bin/activate
	$(PYTHON) src/squash.py \
		--source /Volumes/starship500/build/gaia-18/ \
		--destination /Volumes/starship500/build/gaia-18-squashed/ \
		--num_workers 10

stats: venv/bin/activate
	$(PYTHON) src/stats.py

m13: venv/bin/activate
	$(PYTHON) src/m13.py

profile:
# 	$(PYTHON) -m cProfile -o results.prof m13.py
	$(PYTHON) -m snakeviz -s -p 8080 -H 0.0.0.0 results.prof

# Releases ------------------------------------------
release-check:
	@CHECK="$(VERSION_CHECK)";  \
	if [ $$CHECK -eq 0 ] ; then \
		echo "version check passed!"; \
	else \
		echo "version tag already exists"; \
		false; \
	fi

release: release-check
	gh release create \
		v$(VERSION) \
		build/constellations.$(VERSION).parquet \
		--title "v$(VERSION)" \
		-R steveberardi/$(REPO_NAME)

version: venv/bin/activate
	@echo $(VERSION)


.PHONY: clean test release release-check build

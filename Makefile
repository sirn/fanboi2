BUILDDIR ?= build

PYTHON ?= python
_PYTHON != $(basename $(PYTHON))

VENVDIR ?= venv
VENVCMD ?= $(PYTHON) -m venv
VENV_ALEMBIC ?= $(VENVDIR)/bin/alembic
VENV_NOSE2 ?= $(VENVDIR)/bin/nose2
VENV_PIP ?= $(VENVDIR)/bin/pip
VENV_PIPCOMPILE ?= $(VENVDIR)/bin/pip-compile
VENV_PYTHON ?= $(VENVDIR)/bin/$(_PYTHON)

BUILDENV ?= env LDFLAGS="$(LDFLAGS)" CFLAGS="$(CFLAGS)"


## ----------------------------------------------------------------------------
## Meta targets
##

.PHONY: all
all: prod


## ----------------------------------------------------------------------------
## Build targets
##

$(VENVDIR):
	$(VENVCMD) "$(VENVDIR)"
	$(VENV_PIP) install --upgrade pip
	$(VENV_PIP) install --upgrade pip-tools

requirements.txt: pyproject.toml requirements.in
	$(VENVDIR)/bin/pip-compile --allow-unsafe requirements.in

dev-requirements.txt: requirements.txt dev-requirements.in
	$(VENVDIR)/bin/pip-compile --allow-unsafe dev-requirements.in

test-requirements.txt: requirements.txt test-requirements.in
	$(VENVDIR)/bin/pip-compile --allow-unsafe test-requirements.in

$(BUILDDIR):
	mkdir -p "$(BUILDDIR)"

$(BUILDDIR)/.build: $(VENVDIR) $(BUILDDIR) requirements.txt
	$(BUILDENV) $(VENV_PIP) install -r requirements.txt -e .
	touch "$(BUILDDIR)/.build" \

$(BUILDDIR)/.build-test: $(VENVDIR) $(BUILDDIR) requirements.txt test-requirements.txt
	$(BUILDENV) $(VENV_PIP) install \
		-r requirements.txt \
		-r test-requirements.txt \
		-e .[test]
	touch \
		"$(BUILDDIR)/.build" \
		"$(BUILDDIR)/.build-test"

$(BUILDDIR)/.build-dev: $(VENVDIR) $(BUILDDIR) requirements.txt test-requirements.txt dev-requirements.txt
	$(BUILDENV) $(VENV_PIP) install \
		-r requirements.txt \
		-r test-requirements.txt \
		-r dev-requirements.txt \
		-e .[test,dev]
	touch \
		"$(BUILDDIR)/.build" \
		"$(BUILDDIR)/.build-test" \
		"$(BUILDDIR)/.build-dev"


## ----------------------------------------------------------------------------
## Prod targets
##

.PHONY: prod
prod: $(BUILDDIR)/.build

.PHONY: dist
dist: $(VENVDIR)
	$(VENV_PIP) install --upgrade build
	$(VENV_PYTHON) -m build --sdist


## ----------------------------------------------------------------------------
## Dev targets
##

.PHONY: dev
dev: $(BUILDDIR)/.build-dev


## ----------------------------------------------------------------------------
## Test targets
##

.PHONY: test
test: $(BUILDDIR)/.build-test
	$(VENV_NOSE2) --verbose --with-coverage


## ----------------------------------------------------------------------------
## Maintenance
##

.PHONY: migrate
migrate: $(BUILDDIR)/.build
	$(VENV_ALEMBIC) upgrade head $(ARGS)

.PHONY: clean
clean:
	rm -rf \
		$(BUILDDIR) \
		fanboi2.egginfo \
		fanboi2/__pycache__ \
		fanboi2/static \
		node_modules \
		$(VENVDIR)

$(VERBOSE).SILENT:

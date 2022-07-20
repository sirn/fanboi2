BUILDDIR ?= build

PYTHON ?= python
_PYTHON != basename $(PYTHON)

VENVDIR ?= venv
VENVCMD ?= $(PYTHON) -m venv
VENV_ALEMBIC ?= $(VENVDIR)/bin/alembic
VENV_NOSE2 ?= $(VENVDIR)/bin/nose2
VENV_PIP ?= $(VENVDIR)/bin/pip
VENV_PIPCOMPILE ?= $(VENVDIR)/bin/pip-compile
VENV_PYTHON ?= $(VENVDIR)/bin/$(_PYTHON)
VENV_HONCHO ?= $(VENVDIR)/bin/honcho

PNPM ?= pnpm
GULP ?= $(PNPM) run gulp
_ASSETS != test -d assets && find assets/ -type f

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
	$(VENV_PIP) install --upgrade honcho

requirements.txt: pyproject.toml requirements.in
	$(VENV_PIPCOMPILE) --allow-unsafe requirements.in

dev-requirements.txt: requirements.txt dev-requirements.in
	$(VENV_PIPCOMPILE) --allow-unsafe dev-requirements.in

test-requirements.txt: requirements.txt test-requirements.in
	$(VENV_PIPCOMPILE) --allow-unsafe test-requirements.in

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

node_modules: package.json pnpm-lock.yaml
	$(PNPM) install

$(BUILDDIR)/.build-assets: $(BUILDDIR) node_modules $(_ASSETS)
	$(GULP)
	touch "$(BUILDDIR)/.build-assets"


## ----------------------------------------------------------------------------
## Assets targets
##

.PHONY: assets
assets: $(BUILDDIR)/.build-assets


## ----------------------------------------------------------------------------
## Prod targets
##

.PHONY: prod
prod: $(BUILDDIR)/.build $(BUILDDIR)/.build-assets

.PHONY: prod-run
prod-run: $(BUILDDIR)/.build $(BUILDDIR)/.build-assets
	$(VENV_HONCHO) start -f Procfile

.PHONY: dist
dist: $(VENVDIR) $(BUILDDIR)/.build-assets
	$(VENV_PIP) install --upgrade build
	$(VENV_PYTHON) -m build --sdist


## ----------------------------------------------------------------------------
## Database targets
##

.PHONY: db-migrate
db-migrate: $(BUILDDIR)/.build
	$(VENV_ALEMBIC) upgrade head


## ----------------------------------------------------------------------------
## Dev targets
##

.PHONY: dev
dev: $(BUILDDIR)/.build-dev

.PHONY: dev-run
dev-run: $(BUILDDIR)/.build-dev $(BUILDDIR)/.build-assets
	$(VENV_HONCHO) start -f Procfile.dev


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

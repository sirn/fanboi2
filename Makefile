LDFLAGS     += -L/usr/local/lib
CFLAGS      += -I/usr/local/include

BUILDDIR    ?= .build
VENVDIR     ?= .venv
ENVFILE     ?= .env
YARN        ?= yarn

VIRTUALENV  ?= virtualenv
ALEMBIC      = $(VENVDIR)/bin/alembic
FBCTL        = $(VENVDIR)/bin/fbctl
FBCELERY     = $(VENVDIR)/bin/fbcelery
HONCHO       = $(VENVDIR)/bin/honcho
PIP          = $(VENVDIR)/bin/pip3
PRECOMMIT    = $(VENVDIR)/bin/pre-commit
PYTHON       = $(VENVDIR)/bin/python3

BUILDENV     = env LDFLAGS="$(LDFLAGS)" CFLAGS="$(CFLAGS)"
RUNENV       = env $$(test -f $(ENVFILE) && cat $(ENVFILE))

ASSETS_SRCS != find assets/ -type f


all: assets prod


## Build target
##


$(VENVDIR):
	$(VIRTUALENV) -p python3.6 $(VENVDIR)


$(BUILDDIR):
	mkdir -p $@


$(BUILDDIR)/.build: $(VENVDIR) $(BUILDDIR) setup.py
	$(BUILDENV) $(PIP) install -e .
	touch $(BUILDDIR)/.build


$(BUILDDIR)/.build-test: $(VENVDIR) $(BUILDDIR) setup.py
	$(BUILDENV) $(PIP) install -e .[test]
	touch \
		$(BUILDDIR)/.build \
		$(BUILDDIR)/.build-test


$(BUILDDIR)/.build-dev: $(VENVDIR) $(BUILDDIR) setup.py
	$(BUILDENV) $(PIP) install -e .[test,dev]
	touch \
		$(BUILDDIR)/.build \
		$(BUILDDIR)/.build-test \
		$(BUILDDIR)/.build-dev


node_modules: package.json yarn.lock
	$(YARN) install


$(BUILDDIR)/.build-assets: $(ASSETS_SRCS) $(BUILDDIR) node_modules
	$(YARN) run gulp
	touch $(BUILDDIR)/.build-assets


## Production target
##


prod: $(BUILDDIR)/.build


serve: prod
	$(RUNENV) $(FBCTL) serve


worker: prod
	$(RUNENV) $(FBCELERY) worker


assets: $(BUILDDIR)/.build-assets


## Development target
##


dev: $(BUILDDIR)/.build-dev


devrun: dev $(BUILDDIR)/.build-assets
	$(HONCHO) start \
		-e $(ENVFILE) \
		-f vendor/honcho/Procfile.dev


devhook: dev
	$(PRECOMMIT) install $(ARGS)


devserve: dev
	$(RUNENV) $(FBCTL) serve --reload


devassets: $(BUILDDIR)/.build-assets
	$(YARN) run gulp watch


test: $(BUILDDIR)/.build-test
	$(PYTHON) setup.py nosetests


## Maintenance target
##


migrate: $(BUILDDIR)/.build
	$(RUNENV) $(ALEMBIC) upgrade head $(ARGS)


clean:
	rm -rf \
		$(BUILDDIR) \
		fanboi2.egg-info \
		fanboi2/__pycache__ \
		fanboi2/static \
		node_modules \
		$(VENVDIR)


$(VERBOSE).SILENT:


.PHONY: all prod serve worker assets dev devrun devserver devassets test migrate clean

LDFLAGS     += -L/usr/local/lib
CFLAGS      += -I/usr/local/include

CURDIR      != pwd

BUILDDIR    ?= $(CURDIR)/.build
VENVDIR     ?= $(CURDIR)/.venv
ENVFILE     ?= $(CURDIR)/.env
YARN        ?= yarn

VIRTUALENV  ?= virtualenv
ALEMBIC      = $(VENVDIR)/bin/alembic
FBCTL        = $(VENVDIR)/bin/fbctl
HONCHO       = $(VENVDIR)/bin/honcho
PIP          = $(VENVDIR)/bin/pip3
PRECOMMIT    = $(VENVDIR)/bin/pre-commit
PYTHON       = $(VENVDIR)/bin/python3

BUILDENV     = env LDFLAGS="$(LDFLAGS)" CFLAGS="$(CFLAGS)"
RUNENV       = env $$(test -f $(ENVFILE) && cat $(ENVFILE))

ASSETS_SRCS != find assets/ -type f


all: prod


$(VENVDIR):
	$(VIRTUALENV) -p python3.6 $(VENVDIR)


$(BUILDDIR):
	mkdir -p $@


$(BUILDDIR)/.build: $(VENVDIR) $(BUILDDIR) setup.py
	$(BUILDENV) $(PIP) install -e $(CURDIR)
	touch $(BUILDDIR)/.build


$(BUILDDIR)/.build-test: $(VENVDIR) $(BUILDDIR) setup.py
	$(BUILDENV) $(PIP) install -e $(CURDIR)[test]
	touch \
		$(BUILDDIR)/.build \
		$(BUILDDIR)/.build-test


$(BUILDDIR)/.build-dev: $(VENVDIR) $(BUILDDIR) setup.py
	$(BUILDENV) $(PIP) install -e $(CURDIR)[dev]
	touch \
		$(BUILDDIR)/.build \
		$(BUILDDIR)/.build-test \
		$(BUILDDIR)/.build-dev


node_modules: package.json yarn.lock
	$(YARN) install


$(BUILDDIR)/.build-assets: $(ASSETS_SRCS) $(BUILDDIR) node_modules
	$(YARN) run gulp
	touch $(BUILDDIR)/.build-assets


prod: build assets


serve: prod
	$(RUNENV) $(FBCTL) serve


build: $(BUILDDIR)/.build


assets: $(BUILDDIR)/.build-assets


dev: devbuild assets


devhook: dev
	$(PRECOMMIT) install $(ARGS)


devserve: dev
	$(HONCHO) start \
		-e $(ENVFILE) \
		-f $(CURDIR)/vendor/honcho/Procfile.dev


devbuild: $(BUILDDIR)/.build-dev


test: $(BUILDDIR)/.build-test
	$(PYTHON) $(CURDIR)/setup.py nosetests


migrate: $(BUILDDIR)/.build
	$(RUNENV) $(ALEMBIC) upgrade head $(ARGS)


clean:
	rm -rf \
		$(BUILDDIR) \
		$(CURDIR)/fanboi2.egg-info \
		$(CURDIR)/fanboi2/__pycache__ \
		$(CURDIR)/fanboi2/static \
		$(CURDIR)/node_modules \
		$(VENVDIR)


$(VERBOSE).SILENT:


.PHONY: all prod serve build assets dev devserver devbuild test migrate clean

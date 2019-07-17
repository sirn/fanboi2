LDFLAGS     += -L/usr/local/lib
CFLAGS      += -I/usr/local/include
HOSTNAME    != hostname -s

BUILDDIR    ?= builds/$(HOSTNAME)
VENVDIR     ?= $(BUILDDIR)/venv
YARN        ?= yarn

VIRTUALENV  ?= virtualenv
ALEMBIC      = $(VENVDIR)/bin/alembic
FBCTL        = $(VENVDIR)/bin/fbctl
FBCELERY     = $(VENVDIR)/bin/fbcelery
PIP          = $(VENVDIR)/bin/pip3
PYTHON       = $(VENVDIR)/bin/python3

BUILDENV     = env LANG=en_US.UTF-8 LDFLAGS="$(LDFLAGS)" CFLAGS="$(CFLAGS)"

ASSETS_SRCS != [ -d assets ] && find assets/ -type f


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

$(BUILDDIR)/.build-deploy: $(VENVDIR) $(BUILDDIR) setup.py
	$(BUILDENV) $(PIP) install -e .[deploy]
	touch $(BUILDDIR)/.build-deploy


node_modules: package.json yarn.lock
	$(YARN) install


$(BUILDDIR)/.build-assets: $(ASSETS_SRCS) $(BUILDDIR) node_modules
	$(YARN) run gulp
	touch $(BUILDDIR)/.build-assets


## Production target
##


prod: $(BUILDDIR)/.build


serve: prod
	$(FBCTL) serve


worker: prod
	$(FBCELERY) worker


shell: prod
	$(FBCTL) shell


beat: prod
	$(FBCELERY) beat


assets: $(BUILDDIR)/.build-assets


## Development target
##


dev: $(BUILDDIR)/.build-dev


devserve: dev
	$(FBCTL) serve --reload --workers=1 --threads=4


devassets: assets
	$(YARN) run gulp watch


test: $(BUILDDIR)/.build-test
	$(PYTHON) setup.py nosetests $(ARGS)


## Deploy target
##


deploy: $(BUILDDIR)/.build-deploy


dist: distclean assets distpack


distclean:
	$(PYTHON) setup.py clean


distpack:
	$(PYTHON) setup.py sdist


## Maintenance target
##


migrate: $(BUILDDIR)/.build
	$(ALEMBIC) upgrade head $(ARGS)


clean:
	rm -rf \
		$(BUILDDIR) \
		fanboi2.egg-info \
		fanboi2/__pycache__ \
		fanboi2/static \
		node_modules \
		$(VENVDIR)


$(VERBOSE).SILENT:


.PHONY: all prod serve worker shell beat assets
.PHONY: deploy dist distclean distpack
.PHONY: dev devserve devassets
.PHONY: test migrate clean

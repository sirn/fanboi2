LDFLAGS     ?= -L/usr/local/lib
CFLAGS      ?= -I/usr/local/include
YARN        ?= yarn
VIRTUALENV  ?= virtualenv

HOSTNAME    != hostname
CURDIR      != pwd

SETENV       = env LDFLAGS="$(LDFLAGS)" CFLAGS="$(CFLAGS)"
VENVDIR      = $(HOSTNAME).venv
PIP          = $(VENVDIR)/bin/pip3
PYTHON       = $(VENVDIR)/bin/python3


all:

$(VERBOSE).SILENT:

$(VENVDIR):
	$(VIRTUALENV) -p python3.6 $(VENVDIR)


## -----------------------------------------------------------------------------
## Build targets
## -----------------------------------------------------------------------------

PHONY: build build-assets

build: $(VENVDIR)
	$(SETENV) $(PIP) install -e $(CURDIR)

build-assets:
	$(YARN) install
	$(YARN) run gulp

## -----------------------------------------------------------------------------
## Production targets
## -----------------------------------------------------------------------------

PHONY: prod

prod: build build-assets


## -----------------------------------------------------------------------------
## Development targets
## -----------------------------------------------------------------------------

PHONY: develop

develop: build build-assets

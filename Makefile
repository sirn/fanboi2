LDFLAGS     ?= -L/usr/local/lib
CFLAGS      ?= -I/usr/local/include
SETENV      := env LDFLAGS="$(LDFLAGS)" CFLAGS="$(CFLAGS)"

YARN        ?= yarn

all:

$(VERBOSE).SILENT:

# ----------------------------------------------------------------------
# Assets
# ----------------------------------------------------------------------

.PHONY: assets

assets:
	$(YARN) install
	$(YARN) run gulp

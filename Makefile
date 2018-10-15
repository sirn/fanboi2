LDFLAGS     ?= -L/usr/local/lib
CFLAGS      ?= -I/usr/local/include

PIPENV      ?= pipenv
SETENV      := env LDFLAGS="$(LDFLAGS)" CFLAGS="$(CFLAGS)"

all: prod

$(VERBOSE).SILENT:

# ----------------------------------------------------------------------
# Prod
# ----------------------------------------------------------------------

.PHONY: prod init

prod: init assets

init:
	$(SETENV) $(PIPENV) install

# ----------------------------------------------------------------------
# Development
# ----------------------------------------------------------------------

.PHONY: develop devinit devhook devserver

develop: devinit assets

devinit:
	$(SETENV) $(PIPENV) install --dev $(ARGS)

devhook:
	$(PIPENV) run pre-commit install $(ARGS)

devserver:
	$(PIPENV) run honcho start -f Procfile.dev $(ARGS)

# ----------------------------------------------------------------------
# Assets
# ----------------------------------------------------------------------

.PHONY: assets

assets:
	cd assets && make

# ----------------------------------------------------------------------
# Testing
# ----------------------------------------------------------------------

.PHONY: test

test:
	$(PIPENV) run nosetests $(ARGS)

# ----------------------------------------------------------------------
# Misc
# ----------------------------------------------------------------------

.PHONY: migrate

migrate:
	$(PIPENV) run alembic upgrade head $(ARGS)

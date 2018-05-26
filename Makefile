LDFLAGS := "-L/usr/local/lib"
CFLAGS  := "-I/usr/local/include"

# ----------------------------------------------------------------------
# Prod
# ----------------------------------------------------------------------

.PHONY: prod init

prod: init assets

init:
	pip install pipenv --upgrade
	env \
		LDFLAGS=$(LDFLAGS) \
		CFLAGS=$(CFLAGS) \
	pipenv install

# ----------------------------------------------------------------------
# Development
# ----------------------------------------------------------------------

.PHONY: develop devinit devhook devserver

develop: devinit assets

devinit:
	pip install pipenv --upgrade
	env \
		LDFLAGS=$(LDFLAGS) \
		CFLAGS=$(CFLAGS) \
	pipenv install --dev

devhook:
	pipenv run pre-commit install

devserver:
	pipenv run honcho start -f Procfile.dev

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
	pipenv run nosetests

# ----------------------------------------------------------------------
# Misc
# ----------------------------------------------------------------------

.PHONY: migrate

migrate:
	pipenv run alembic upgrade head

.PHONY: prod init

prod: init assets

init:
	pip install pipenv --upgrade
	pipenv install

# ----------------------------------------------------------------------
# Development
# ----------------------------------------------------------------------

.PHONY: develop devinit devhook

develop: devinit assets

devinit:
	pip install pipenv --upgrade
	pipenv install --dev

devhook:
	pipenv run pre-commit install

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
# Misc commands
# ----------------------------------------------------------------------

.PHONY: migrate

migrate:
	pipenv run alembic upgrade head

# Fanboi2

[![python 3.7](https://img.shields.io/badge/python-3.7-blue.svg)](https://docs.python.org/3/whatsnew/3.7.html) [![builds.sr.ht status](https://builds.sr.ht/~sirn/fanboi2/freebsd.yml.svg)](https://builds.sr.ht/~sirn/fanboi2/freebsd.yml?)

Board engine behind [Fanboi Channel](https://fanboi.ch/) written in Python.

## Installation

For production environment, Fanboi2 has the following runtime requirements:

-   [Python 3.7](https://www.python.org/downloads/) with [Poetry](https://poetry.eustace.io)
-   [PostgreSQL 10](https://www.postgresql.org/)
-   [Redis](https://redis.io/)

Additionally, the following packages are build-time requirements for compiling assets:

-   [Node LTS](https://nodejs.org/)
-   [NPM](https://www.npmjs.com)

### Installing with Vagrant

If you're looking to develop or test Fanboi2, simply install [Vagrant](https://www.vagrantup.com/) and run:

```shellsession
$ vagrant up
```

Then `vagrant ssh` and follow the _Setting up applications_ section below.

### Installing on FreeBSD systems

On FreeBSD systems, these packages can be installed with:

```shellsession
$ sudo pkg install ca_root_nss python36 py36-sqlite3 py36-pip postgresql11-server postgresql11-client redis node12 npm-node12
$ pip install --user poetry
```

Setup PostgreSQL:

```shellsession
$ sudo sysrc postgresql_enable=YES
$ sudo service postgresql initdb
$ sudo service postgresql start
$ sudo -u postgres createuser $USER
$ sudo -u postgres createdb -O $USER fanboi2
$ sudo -u postgres createdb -O $USER fanboi2_dev
$ sudo -u postgres createdb -O $USER fanboi2_test
```

Setup Redis:

```shellsession
$ sudo sysrc redis_enable=YES
$ sudo service redis start
```

### Configuring environment variables

For convenient during development, configure these environment variables in `.profile`:

```shellsession
$ cat <<EOF >> ~/.profile
PATH=\$PATH:\$HOME/.local/bin; export PATH
CELERY_BROKER_URL=redis://127.0.0.1:6379/1; export CELERY_BROKER_URL
DATABASE_URL=postgresql://127.0.0.1:5432/fanboi2_dev; export DATABASE_URL
POSTGRESQL_TEST_DATABASE=postgresql://127.0.0.1:5432/fanboi2_test; export POSTGRESQL_TEST_DATABASE
REDIS_URL=redis://127.0.0.1:6379/0; export REDIS_URL
SERVER_DEV=true; export SERVER_DEV
SERVER_HOST=0.0.0.0; export SERVER_HOST
SERVER_PORT=6543; export SERVER_PORT
SESSION_SECRET=\$(openssl rand -hex 32); export SESSION_SECRET
AUTH_SECRET=\$(openssl rand -hex 32); export AUTH_SECRET
EOF
```

### Setting up application

After all packages are installed, setup the application with:

```shellsession
$ git clone https://git.sr.ht/~sirn/fanboi2 fanboi2
$ cd fanboi2/
$ poetry install --no-dev
$ npm install && npm run gulp
```

Then configure environment variables and run:

```shellsession
$ poetry run alembic upgrade head
$ poetry run fbctl serve
```

You also need to run the worker (each in its own terminal window) with:

```shellsession
$ poetry run fbcelery worker
$ poetry run fbcelery beat
```

And you're done! Please visit <http://localhost:6543/admin/> to perform initial configuration.

## Configuring

Fanboi2 uses environment variable to configure the application. You may want to use something like [Direnv](https://github.com/direnv/direnv) to manage these environment variables.

-   `AUTH_SECRET` -- **Required**. Secret for authentication/authorization cookie.
-   `CELERY_BROKER_URL` -- **Required**. Redis URL for Celery broker, e.g. redis://127.0.0.1/1
-   `DATABASE_URL` -- **Required**. Database URL, e.g. postgres://127.0.0.1/fanboi2
-   `REDIS_URL` -- **Required**. Redis URL, e.g. redis://127.0.0.1/0
-   `SESSION_SECRET` -- **Required**. Secret for session cookie. Must not reuse `AUTH_SECRET`.
-   `GEOIP_PATH` -- Path to GeoIP database, e.g. /usr/share/geoip/GeoLite2-Country.mmdb
-   `SERVER_DEV` -- Boolean flag whether to enable dev console, default False
-   `SERVER_SECURE` -- Boolean flag whether to only authenticate via HTTPS, default False.

## Development

To setup Fanboi2 in development mode, run the following commands after performing production setup steps:

```shellsession
$ poetry install
```

And run the server with:

```shellsession
$ poetry run honcho start
```

### Submitting changes

To submit patches to mailing list:

1.  Clone the repository: `git clone https://git.sr.ht/~sirn/fanboi2`
2.  Make the necessary changes.
3.  Configure Git sendmail address: `git config sendemail.to ~sirn/fanboi2-dev@lists.sr.ht`
4.  Create a patch: `git format-patch -1 HEAD` (refer to `git-format-patch(1)` for more info)
5.  Send a patch: `git send-email -1` (refer to `git-send-email(1)` for more info)

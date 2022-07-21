# Fanboi2

[![python 3.9](https://img.shields.io/badge/python-3.9-blue.svg)](https://docs.python.org/3/whatsnew/3.9.html)
[![builds.sr.ht status](https://builds.sr.ht/~sirn/fanboi2/commits/freebsd.yml.svg)](https://builds.sr.ht/~sirn/fanboi2/commits/freebsd.yml?)

Board engine behind [Fanboi Channel](https://fanboi.ch/) written in Python.

## Installation

For production environment, Fanboi2 has the following runtime requirements:

-   [Python 3.9](https://www.python.org/downloads/)
-   [PostgreSQL 13](https://www.postgresql.org/)
-   [Redis](https://redis.io/)

Additionally, the following packages are build-time requirements for compiling assets:

-   [Node LTS](https://nodejs.org/)
-   [PNPM](https://github.com/pnpm/pnpm)

On a non-FreeBSD, you will also need to install **BSD Make** (usually called `bmake` in GNU systems.)

### Installing on FreeBSD systems

On FreeBSD systems, these packages can be installed with:

```shellsession
$ sudo pkg install ca_root_nss python39 py39-pip py39-sqlite3 postgresql13-server postgresql13-client redis node16 npm-node16
```

Install PNPM:

```shellsession
$ npm set prefix="$HOME/.local"
$ npm install -g pnpm
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

After all packages are installed, setup the application with:

```shellsession
$ git clone https://git.sr.ht/~sirn/fanboi2
$ cd fanboi2/
$ make
```

### Configuring environment variables

For convenient during development, configure these environment variables in `.env`:

```shellsession
$ cat <<EOF > .env
CELERY_BROKER_URL=redis://127.0.0.1:6379/1
DATABASE_URL=postgresql://127.0.0.1:5432/fanboi2_dev
POSTGRESQL_TEST_DATABASE=postgresql://127.0.0.1:5432/fanboi2_test
REDIS_URL=redis://127.0.0.1:6379/0
SERVER_DEV=true
SERVER_HOST=0.0.0.0
SERVER_PORT=6543
SESSION_SECRET=\$(openssl rand -hex 32)
AUTH_SECRET=\$(openssl rand -hex 32)
EOF
```

Load environment by sourcing it:

```shellsession
$ . fanboi2-env.sh
```

### Setting up application

Migrate the database:

```shellsession
$ make db-migrate
```

Start the application:

```shellsession
$ make prod-run
```

And you're done. Visit <http://localhost:6543/admin/> to perform initial configuration.

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

To setup Fanboi2 in development mode, run the following commands:

```shellsession
$ make dev
```

And run the server with:

```shellsession
$ make dev-run
```

### Submitting changes

To submit patches to mailing list:

1.  Clone the repository: `git clone https://git.sr.ht/~sirn/fanboi2`
2.  Make the necessary changes.
3.  Configure Git sendmail address: `git config sendemail.to ~sirn/fanboi2-dev@lists.sr.ht`
4.  Create a patch: `git format-patch -1 HEAD` (refer to `git-format-patch(1)` for more info)
5.  Send a patch: `git send-email -1` (refer to `git-send-email(1)` for more info)

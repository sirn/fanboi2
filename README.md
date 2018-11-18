# Fanboi2

[![python 3.6](https://img.shields.io/badge/python-3.6-blue.svg)](https://docs.python.org/3/whatsnew/3.6.html)
[![builds.sr.ht status](https://builds.sr.ht/~sirn/fanboi2/freebsd.yml.svg)](https://builds.sr.ht/~sirn/fanboi2/freebsd.yml?)

Board engine behind [Fanboi Channel](https://fanboi.ch/) written in Python.

## Installation

Fanboi2 has the following runtime requirements:

-   [Python 3.6](https://www.python.org/downloads/) with [Virtualenv](https://virtualenv.pypa.io/en/stable/)
-   [PostgreSQL 10](https://www.postgresql.org/)
-   [Redis](https://redis.io/)

Additionally, the following packages are build-time requirements for compiling assets:

-   [Node 8](https://nodejs.org/) (Node 10 will NOT work)
-   [Yarn](https://yarnpkg.com/)

After all packages are installed, you may now setup the application:

    $ git clone https://git.sr.ht/~sirn/fanboi2 fanboi2
    $ cd fanboi2/
    $ make all -j2

Then configure `.env` according to the configuring section below, then run:

    $ make migrate
    $ make serve

You also need to run the worker (in another terminal) with:

    $ make worker

And you're done! Please visit <http://localhost:6543/admin/> to perform initial configuration.

## Configuring

Fanboi2 uses environment variable to configure the application. In case `make` is used, you can create a file named `.env` in the root directory of the project and our make configuration will happily use it up on `make serve` or `make devserve`. Otherwise you may want to use something like [Direnv](https://github.com/direnv/direnv).

| Key                 | Description                                                            |
| ------------------- | ---------------------------------------------------------------------- |
| `AUTH_SECRET`       | **Required**. Secret for authentication/authorization cookie.          |
| `CELERY_BROKER_URL` | **Required**. Redis URL for Celery broker, e.g. redis://127.0.0.1/1    |
| `DATABASE_URL`      | **Required**. Database URL, e.g. postgres://127.0.0.1/fanboi2          |
| `REDIS_URL`         | **Required**. Redis URL, e.g. redis://127.0.0.1/0                      |
| `SESSION_SECRET`    | **Required**. Secret for session cookie. Must not reuse `AUTH_SECRET`. |
| `GEOIP_PATH`        | Path to GeoIP database, e.g. /usr/share/geoip/GeoLite2-Country.mmdb    |
| `SERVER_DEV`        | Boolean flag whether to enable dev console, default False              |
| `SERVER_SECURE`     | Boolean flag whether to only authenticate via HTTPS, default False.    |

## Contributing

Fanboi2 is open to any contributors, whether you are learning Python or an expert. To contribute to Fanboi2, it is highly recommended to use [Vagrant](https://www.vagrantup.com/) as it is currently replicating the production environment of [Fanboi Channel](https://fanboi.ch/) and perform all the necessary setup steps for you. Alternatively, if containers are your thing, you can find experimental, unsupported Docker Compose scripts in `vendor/docker/`.

### Vagrant

1.  Install [Vagrant](https://www.vagrantup.com/) of your preferred platform.
2.  Install [VirtualBox](https://www.virtualbox.org/) or other providers supported by Vagrant.
3.  Run vagrant up and read Getting Started while waiting.
4.  Run vagrant ssh to SSH into the development machine (remember to `cd /vagrant`).

In case you do not want to use Vagrant, you can install the dependencies from the installation section and run:

    $ make dev
    $ make devhook

You can then configure the application (see configuration section) and run the server:

    $ make migrate
    $ make devrun

### Docker

1.  Install `Docker` and `Docker Compose`
2.  Copy Compose configuration files to the application's parent directory (`cp vendor/docker/docker-compose.* ../`)
3.  Modify the content of `docker-compose.yml`
    1.  Generate both `AUTH_SECRET` and `SESSION_SECRET` tokens with `openssl rand -hex 32`
    2.  Set a sensible PostgreSQL password
    3.  This config assumes fanboi2 was cloned to `fanboi2`; update the build and mount paths if untrue
4.  Start the contraption with `docker-compose up` from the same directory as the config files.

Images are published to [sirn/fanboi2](https://hub.docker.com/r/sirn/fanboi2/) on GitHub for every commit in master. By default, using Fanboi2 with the default `docker-compose.yml` will start server in development mode which aids debugging. To disable development server capabilities, remove or rename the file `docker-compose.override.yml`.

### Submitting changes

To submit patches to mailing list:

1.  Clone the repository: `git clone https://git.sr.ht/~sirn/fanboi2`
2.  Make the necessary changes.
3.  Configure Git sendmail address: `git config sendemail.to ~sirn/fanboi2-dev@lists.sr.ht`
4.  Create a patch: `git format-patch -1 HEAD` (refer to `git-format-patch(1)` for more info)
5.  Send a patch: `git send-email -1` (refer to `git-send-email(1)` for more info)

To submit patches via [GitHub Pull Request](https://github.com/sirn/fanboi2):

1.  Fork the repository using "Fork" button on the top right of the [GitHub project page](https://github.com/sirn/fanboi2).
2.  Make the necessary changes.
3.  Submit pull request against the **master** branch.

Submitting patches via mailing list is recommended in case you wish to remain anonymous (e.g. using thrown-away email address). GitHub, on the other hand, require you to create account with them and [GitHub terms of service explicitly forbids having more than one account](https://help.github.com/articles/github-terms-of-service/#b-account-terms). Whether method you choose, our reviewer will review and merge the patch as soon as possible. It would be much appreciated if you could follow the following guidelines:

-   When making a non-trivial changes, please first discuss in the [mailing list](https://lists.sr.ht/~sirn/fanboi2-dev) or in the [development thread](https://fanboi.ch/meta/).
-   Make sure new features has enough tests and no regressions.
-   Fix any offenses as reported by pre-commit hooks.

## Workflow

Fanboi2 uses a `Makefile`-based workflow in its development and production cycle. You are encourage to use `make` rather than directly invoking underlying commands. The provided `Makefile` can be customized to certain extent using environment variable, such as:

| Key                     | Description                                                        |
| ----------------------- | ------------------------------------------------------------------ |
| `VERBOSE=1`             | Prints the underlying command when running `make`.                 |
| `VIRTUALENV=virtualenv` | Specifies the `virtualenv` binary (e.g. `virtualenv-3.6` for BSDs) |
| `YARN=yarn`             | Specifies the `yarn` binary.                                       |
| `VENVDIR=.venv`         | Specifies the virtualenv directory.                                |
| `ENVFILE=.env`          | Specifies the file containing environment variable to load from.   |

The following make targets are available for use in production:

-   `make all` build the application and assets using production configurations.
-   `make prod` build the application using production configuration.
-   `make serve` run the application server.
-   `make worker` run the application worker.
-   `make assets` build assets.
-   `make migrate` migrate daabase.
-   `make clean` remove everything.

The following make targets are available for use in development:

-   `make dev` builds the application using development configuration.
-   `make devrun` run the development application server, application worker and assets watcher.
-   `make devhook` install development pre-commit hook to the repository.
-   `make devserve` run the development application server.
-   `make devassets` run the development assets watcher.

The following make targets are available for use in test environment:

-   `make test` run tests.

Most of these commands make use of VENVDIR and ENVFILE.

### The Adventurous Way

If using `make` is not your thing, you can set everything up manually, for example on macOS:

    $ brew install python@3 node@8 yarn

Create the deploy environment:

    $ mkdir -p $HOME/dev/fanboi2/venv
    $ virtualenv new -p python3 $HOME/dev/fanboi2/venv
    $ git clone https://git.sr.ht/~sirn/fanboi2 $HOME/dev/fanboi2/src

Setup the application:

    $ cd $HOME/dev/fanboi2/src
    $ $HOME/dev/fanboi2/venv/bin/pip3 install -e .[dev,test]
    $ yarn install
    $ yarn run gulp
    $ vi $HOME/dev/fanboi2/envfile

Configure `envfile` then:

    $ $HOME/dev/fanboi2/venv/bin/alembic upgrade head
    $ $HOME/dev/fanboi2/venv/bin/fbctl serve --reload

In another terminal, run the worker:

    $ $HOME/dev/fanboi2/venv/bin/fbcelery worker

Also install `pre-commit-hook` if you want to contribute to the project:

    $ $HOME/dev/fanboi2/venv/bin/pre-commit install

## License

Copyright © 2013-2018, Kridsada Thanabulpong. All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

-   Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
-   Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
-   Neither the name of the author nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# Fanboi2

[![python 3.6](https://img.shields.io/badge/python-3.6-blue.svg)](https://docs.python.org/3/whatsnew/3.6.html) [![builds.sr.ht status](https://builds.sr.ht/~sirn/fanboi2/freebsd.yml.svg)](https://builds.sr.ht/~sirn/fanboi2/freebsd.yml?)

Board engine behind [Fanboi Channel](https://fanboi.ch/) written in Python.

## Installation

For production environment, Fanboi2 has the following runtime requirements:

-   [Python 3.6](https://www.python.org/downloads/) with [Poetry](https://poetry.eustace.io)
-   [PostgreSQL 10](https://www.postgresql.org/)
-   [Redis](https://redis.io/)

Additionally, the following packages are build-time requirements for compiling assets:

-   [Node 8](https://nodejs.org/) (Node 10 will NOT work)
-   [Yarn](https://yarnpkg.com/)

After all packages are installed, setup the application with:

    $ git clone https://git.sr.ht/~sirn/fanboi2 fanboi2
    $ cd fanboi2/
    $ poetry install --no-dev
    $ yarn install && yarn run gulp

Then configure environment variables according to the configuring section below, and run:

    $ poetry run alembic upgrade head
    $ poetry run fbctl serve

You also need to run the worker (each in its own terminal window) with:

    $ poetry run fbcelery worker
    $ poetry run fbcelery beat

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

    $ poetry install

And run the server with (each in its own terminal window):

    $ poetry run fbctl serve --reload --workers=1 --threads=4
    $ yarn run gulp watch

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

## License

Copyright © 2013-2019, Kridsada Thanabulpong. All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

-   Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
-   Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
-   Neither the name of the author nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

=======
Fanboi2
=======

|py| |ci|

Board engine behind `Fanboi Channel`_ written in Python.

.. |py| image::
        https://img.shields.io/badge/python-3.6-blue.svg
        :target: https://docs.python.org/3/whatsnew/3.6.html

.. |ci| image::
        https://img.shields.io/travis/forloopend/fanboi2.svg
        :target: https://travis-ci.org/forloopend/fanboi2

Installation
------------

Fanboi2 requires the following packages to be installed.

- `Python 3.6 <https://www.python.org/downloads/>`_ with `Pipenv <https://pipenv.readthedocs.io>`_
- `PostgreSQL 10 <http://www.postgresql.org/>`_
- `Redis <http://redis.io/>`_
- `NodeJS <http://nodejs.org/>`_ with `Yarn <https://yarnpkg.com/>`_

After all packages are installed and started, you may now clone the application::

  $ git clone https://github.com/forloopend/fanboi2.git fanboi2

Then setup the application::

  $ cd fanboi2/
  $ make prod

Configure ``.env`` (see the configuring section) and run::

  $ make migrate
  $ pipenv run fbctl serve

And you're done! Please visit `http://localhost:6543/admin/ <http://localhost:6543/admin/>`_ to perform initial configuration.

Configuring
-----------

Fanboi2 uses environment variable to configure the application. In case `Pipenv <https://docs.pipenv.org/>`_ is used, you can create a file name ``.env`` in the root directory of the project and Pipenv will happily read the file on ``pipenv run``. Otherwise you may want to use something like `Direnv <https://github.com/direnv/direnv>`_.

========================= =========================================================================
Key                       Description
========================= =========================================================================
``AUTH_SECRET``           **Required**. Secret for authentication/authorization cookie.
``CELERY_BROKER_URL``     **Required**. Redis URL for Celery broker, e.g. `redis://127.0.0.1/1`
``DATABASE_URL``          **Required**. Database URL, e.g. `postgres://127.0.0.1/fanboi2`
``MEMCACHED_URL``         **Required**. Memcached URL, e.g. `127.0.0.1:11211`
``REDIS_URL``             **Required**. Redis URL, e.g. `redis://127.0.0.1/0`
``SESSION_SECRET``        **Required**. Secret for session cookie. Must not reuse ``AUTH_SECRET``.
``GEOIP_PATH``            Path to GeoIP database, e.g. `/usr/share/geoip/GeoLite2-Country.mmdb`
``SERVER_DEV``            Boolean flag whether to enable dev console, default `False`
``SERVER_SECURE``         Boolean flag whether to only authenticate via HTTPS, default `False`.
========================= =========================================================================

Contributing
------------

Fanboi2 is open to any contributors, whether you are learning Python or an expert. To contribute to Fanboi2, it is highly recommended to use `Vagrant`_ as it is currently replicating the production environment of `Fanboi Channel`_ and perform all the necessary setup steps for you. You can follow these steps to get the app running:

1. Install `Vagrant`_ of your preferred platform.
2. Install `VirtualBox`_ or other providers supported by Vagrant.
3. Run `vagrant up` and read Getting Started while waiting.
4. Run `vagrant ssh` to SSH into the development machine (remember to ``cd /vagrant``).

In case you do not want to use Vagrant, you can install the dependencies from the installation section and run::

  $ make develop
  $ make devhook

You can then configure the application (see configuration section) and run the server::

  $ make migrate
  $ pipenv run honcho start -f Procfile.dev

Once you've made your changes, simply open a `pull request <https://github.com/forloopend/fanboi2/pulls>`_ against the **master** branch. Our reviewer will review and merge the pull request as soon as possible. It would be much appreciated if you could follow the following guidelines:

- When making a non-trivial changes, please create `an issue <https://github.com/forloopend/fanboi2/issues>`_ prior to starting.
- Make sure new features has enough tests and no regressions.
- Fix any offenses as reported by pre-commit hooks.

License
-------

Copyright (c) 2013-2018, Kridsada Thanabulpong. All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

- Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
- Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
- Neither the name of the author nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

.. _Fanboi Channel: https://fanboi.ch/
.. _Waitress: https://docs.pylonsproject.org/projects/waitress/en/latest/
.. _Vagrant: https://www.vagrantup.com/
.. _VirtualBox: https://www.virtualbox.org/
.. _Yarn: https://yarnpkg.com/
.. _Gulp: http://gulpjs.com/
.. _Typings: https://github.com/typings/typings

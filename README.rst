Fanboi2 |ci|
============

Board engine behind `Fanboi Channel <https://fanboi.ch/>`_ written in Python.

.. |ci| image:: https://img.shields.io/travis/pxfs/fanboi2.svg?style=flat-square
        :target: https://travis-ci.org/pxfs/fanboi2

Getting Started
---------------

There are two ways of getting the app up and running for development. Using `Vagrant`_ (*The Better Way*) or installing everything manually (*The Adventurous Way*). The recommened method is to use Vagrant as it closely replicates the production environment.

The Better Way
~~~~~~~~~~~~~~

The easiest way to get the app running is to run `Vagrant`_. You can follow these steps to get the app running:

1. Install `Vagrant`_ of your preferred platform.
2. Install `VirtualBox <https://www.virtualbox.org/>`_ or other `providers <http://docs.vagrantup.com/v2/providers/index.html>`_ supported by Vagrant.
3. Run ``vagrant up`` and read `Getting Started <http://docs.vagrantup.com/v2/getting-started/index.html>`_ while waiting.
4. Run ``vagrant ssh`` to SSH into the development machine.

Once the development box is up and running, you may now run the server::

    $ vagrant ssh
    $ cd /vagrant
    $ pserve development.ini

Now you're done! You can now proceed to the Management Scripts section below.

The Adventurous Way
~~~~~~~~~~~~~~~~~~~

If you don't really want to use Vagrant, you can also install everything using your preferred methods:

1. `Python 3.5 <https://www.python.org/downloads/>`_.
2. `PostgreSQL 9.5 <http://www.postgresql.org/>`_.
3. `Redis 3.0 <http://redis.io/>`_.
4. `Memcached 1.4 <http://www.memcached.org/>`_.
5. `Node.js 6.2 <http://nodejs.org/>`_ with `Gulp`_ and `Typings`_.

After the package above are up and running, you may now setup the application::

    $ cp examples/development.ini.sample development.ini
    $ cp examples/alembic.ini.sample alembic.ini
    $ python3.5 setup.py develop
    $ alembic upgrade head
    $ pserve development.ini

And you're done! You can now proceed to the Management Scripts section below.

Assets
------

The application doesn't come with assets compiled by default and are done externally via `Gulp`_ and `Typings`_. Once you've setup the environment, you can use these two commands to build assets:

1. ``typings install`` to download `TypeScript <http://www.typescriptlang.org/>`_ definition for dependencies.
2. ``gulp`` to build assets with `Gulp`_ (or use ``gulp watch`` to auto-reload).

Once these two commands are run, assets will be compiled to ``fanboi2/static`` in which you should point the web server to it. You should do this on every deploy.

Management Scripts
------------------

After you've setup the environment, the first thing you want to do is to create a new board::

    $ fb2_create_board development.ini --title Lounge --slug lounge
    $ fb2_create_board development.ini --title Demo --slug demo

Above commands will create a board named "Lounge" and "Demo" at ``/lounge`` and ``/demo`` respectively. Now if you want to update something such as description, you can now do::

    $ fb2_update_board development.ini -s lounge -f description

Slug is used here to identify which board to edit. All database fields in board are editable this way. Some field, such as ``settings`` must be a **valid JSON**. Both commands also accepts ``--help`` which will display some available options. Apart from the above two scripts, there are many other commands you might be interested in, such as:

1. ``pserve development.ini`` to run the development server with `Waitress <http://waitress.readthedocs.org/en/latest/>`_.
2. ``pshell development.ini`` to get into Python console with the app loaded.
3. ``fb2_celery development.ini worker`` to start a `Celery <http://www.celeryproject.org/>`_ worker.
4. ``alembic upgrade head`` to update the database to latest version with `Alembic <http://alembic.readthedocs.org/en/latest/>`_.

Celery worker is required to be run if you want to enable posting features.

Contributing
------------

We use `git-flow <https://github.com/nvie/gitflow>`_ as primary branching model. All developments are done in the **develop** branch; **master** branch is the most stable and will be deployed immediately to the live site. You can install ``git-flow`` by following `git-flow installation instructions <https://github.com/nvie/gitflow/wiki/Installation>`_ (use the default values). Although using `git-flow` is not a requirement for pull request, it is recommended to do so:

1. Fork this repo.
2. Start a new feature with ``git flow feature start feature-name``.
3. After you've done, open a pull request against **develop** branch of this repo.

Please make sure that test coverage is 100% and everything passed. It's also a good idea to open a bug ticket for feature you want to implement before starting. We have development IRC channel at `irc.fanboi.ch#fanboi <irc://irc.fanboi.ch/#fanboi>`_. Although if you want to submit patch anonymously you can also create git patch and post it to `support board <https://fanboi.ch/meta/>`_ as well.

License
-------

Copyright (c) 2013-2016, Kridsada Thanabulpong. All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

- Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
- Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
- Neither the name of the author nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

.. _Vagrant: https://www.vagrantup.com/
.. _Gulp: https://github.com/gulpjs/gulp
.. _Typings: https://github.com/typings/typings

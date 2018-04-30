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

Fanboi2 requires that the following softwares are installed.

- `Python 3.6 <https://www.python.org/downloads/>`_
- `PostgreSQL 9.6 <http://www.postgresql.org/>`_
- `Redis 4.0 <http://redis.io/>`_
- `NodeJS 9.10 <http://nodejs.org/>`_ with `Yarn 1.5 <https://yarnpkg.com/>`_

After package mentioned are installed or started, you may now clone the application::

  $ git clone https://github.com/forloopend/fanboi2.git fanboi2

Then setup the application::

  $ cd fanboi2/
  $ pip3 install -e .
  $ alembic upgrade head

  $ cd assets/
  $ yarn
  $ yarn run typings install
  $ yarn run gulp

  $ fbctl serve

And you're done! Please visit `http://localhost:6543/panel <http://localhost:6543/panel>`_ to perform initial configuration.

Development
-----------

To develop Fanboi2, it is highly recommended to use `Vagrant`_ as it is currently replicating the production environment of `Fanboi Channel`_. You can follow these steps to get the app running:

- Install `Vagrant`_ of your preferred platform.
- Install `VirtualBox`_ or other providers supported by Vagrant.
- Run `vagrant up` and read Getting Started while waiting.
- Run `vagrant ssh` to SSH into the development machine.

Once the development box is up and running, you can now run the server (inside the development machine)::

    $ cd /vagrant
    $ fbctl serve

Contributing
------------

Fanboi2 is open to any contributors, whether you're learning Python or an expert. Simply open a `pull request <https://github.com/forloopend/fanboi2/pulls>`_ against the **master** branch. Our reviewer will review and merge the pull request as soon as possible. It would be much appreciated if you could follow the following guidelines:

- It's always a good idea to open `an issue <https://github.com/forloopend/fanboi2/issues>`_ prior to starting.
- No need for 100% coverage but please make sure new features has bare minimum tests.
- Remember to run `flake8 <https://pypi.python.org/pypi/flake8>`_ and fix any styling issues.
- After done, simply open a `pull request <https://github.com/forloopend/fanboi2/pulls>`_ against **master** branch.

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

Fanboi2
=======

Board engine behind `Fanboi Channel <http://fanboi.ch/>`_ written in Python.

Getting Started
---------------

The Better Way
~~~~~~~~~~~~~~

We use `Vagrant <http://www.vagrantup.com/>`_ for development environment provisioning. You must first `install Vagrant <http://docs.vagrantup.com/v2/installation/>`_ (and `VirtualBox <https://www.virtualbox.org/>`_ or any other available `providers <http://docs.vagrantup.com/v2/providers/index.html>`_) and run the following commands::

    $ git submodule update --init
    $ vagrant init precise64 http://files.vagrantup.com/precise64.box
    $ vagrant up

That's it! You can now visit http://localhost:6543/ and proceed on development. After you've done, you can now run either ``vagrant destroy`` to completely remove the VM or ``vagrant halt`` to shutdown the VM. See also `Teardown <http://docs.vagrantup.com/v2/getting-started/teardown.html>`_ section of Vagrant documentation.

The Adventurous Way
~~~~~~~~~~~~~~~~~~~

If you don't want to use Vagrant (oh you sadistic), you can manually install everything, including:

- `Python 3.2 <http://www.python.org/>`_
- `PostgreSQL 9.1 <http://www.postgresql.org/>`_
- `Redis <http://redis.io>`_
- `node.js <http://nodejs.org>`_ with `brunch <http://brunch.io/>`_

After all prerequisites are installed, you can now create the database, run setup and seed the database::

    $ createuser -P fanboi2  # Set "dev" as password.
    $ createdb -O fanboi2 fanboi2_dev
    $ python setup.py develop
    $ alembic upgrade head

It is recommended to run tests and see if all tests passed. Before doing so, you must first create the ``fanboi2_test`` database::

    $ createdb -O fanboi2 fanboi2_test
    $ pip install nose
    $ nosetests

If all tests passed, you can now run the application. You must first setup assets compilation and do an initial compile before running::

    $ npm install
    $ brunch build
    $ pserve development.ini --reload

You may also found ``brunch watch`` useful for automatic assets compilation::

    $ brunch watch

Management Scripts
------------------

We currently uses CLI to manage board settings. If you use Vagrant, you will need to SSH into the development box and run the following commands before begin::

    $ vagrant ssh
    $ cd /vagrant
    $ source /usr/local/venv/fanboi2/bin/activate

After you've setup the environment, the first thing you want to do is to create a new board::

    $ fb2_create_board development.ini --title Lounge --slug lounge
    $ fb2_create_board development.ini --title Demo --slug demo

Above commands will create a board named "Lounge" and "Demo" at ``/lounge`` and ``/demo`` respectively. Now if you want to update something such as description, you can now do::

    $ fb2_update_board development.ini -s lounge -f description

Slug is used here to identify which board to edit. All database fields in board are editable this way. Some field, such as ``settings`` must be a **valid JSON**. Both commands also accepts ``--help`` which will display some available options.

Troubleshooting
---------------

For Vagrant user, if for some reason the URL isn't accessible, you can try visiting http://localhost:9001/ to visit Supervisor web interface and restart all processes.

Contributing
------------

We use `git-flow <https://github.com/nvie/gitflow>`_ as primary branching model. All developments are done in the **develop** branch; **master** branch is the most stable and will be deployed immediately to the live site. You can install ``git-flow`` by following `git-flow installation instructions <https://github.com/nvie/gitflow/wiki/Installation>`_ (use the default values). To contribute, you must:

1. Fork this repo.
2. Start a new feature with ``git flow feature start feature-name``.
3. After you've done, open a pull request against **develop** branch of this repo.

Please make sure that test coverage is 100% and everything passed. It's also a good idea to open a bug ticket for feature you want to implement before starting.

License
-------

| Copyright (c) 2013, Kridsada Thanabulpong
| All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

- Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
- Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
- Neither the name of the author nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

Icons License
~~~~~~~~~~~~~

Icons included with this software package are part of Glyphicons and are **not covered by the open-source license**. You must purchase a separate license for use outside the project at `Glyphicons <http://glyphicons.com/>`_ website.

Fanboi2 |ci|
============

Board engine behind `Fanboi Channel <http://fanboi.ch/>`_ written in Python.

.. |ci| image:: https://api.travis-ci.org/pxfs/fanboi2.png?branch=develop
        :target: https://travis-ci.org/pxfs/fanboi2

Getting Started
---------------

TODO.

Management Scripts
------------------

We currently uses CLI to manage board settings. If you use Vagrant, you will need to SSH into the development box and run the following commands before begin::

    $ vagrant ssh
    $ cd /vagrant
    $ source /srv/http/fanboi2/env/bin/activate

After you've setup the environment, the first thing you want to do is to create a new board::

    $ fb2_create_board development.ini --title Lounge --slug lounge
    $ fb2_create_board development.ini --title Demo --slug demo

Above commands will create a board named "Lounge" and "Demo" at ``/lounge`` and ``/demo`` respectively. Now if you want to update something such as description, you can now do::

    $ fb2_update_board development.ini -s lounge -f description

Slug is used here to identify which board to edit. All database fields in board are editable this way. Some field, such as ``settings`` must be a **valid JSON**. Both commands also accepts ``--help`` which will display some available options.

Contributing
------------

We use `git-flow <https://github.com/nvie/gitflow>`_ as primary branching model. All developments are done in the **develop** branch; **master** branch is the most stable and will be deployed immediately to the live site. You can install ``git-flow`` by following `git-flow installation instructions <https://github.com/nvie/gitflow/wiki/Installation>`_ (use the default values). Although using `git-flow` is not a requirement for pull request, it is recommended to do so:

1. Fork this repo.
2. Start a new feature with ``git flow feature start feature-name``.
3. After you've done, open a pull request against **develop** branch of this repo.

Please make sure that test coverage is 100% and everything passed. It's also a good idea to open a bug ticket for feature you want to implement before starting.

We have development IRC channel at `irc.freenode.net#fanboi <irc://irc.freenode.net/#fanboi>`_. Although if you want to submit patch anonymously you can also create git patch and post it to `support thread <https://fanboi.ch/lounge/1/>`_ as well.

License
-------

| Copyright (c) 2013, Kridsada Thanabulpong
| All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

- Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
- Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
- Neither the name of the author nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

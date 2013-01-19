Fanboi2
===============

Board engine behind `Fanboi Channel <http://fanboi.ch/>`_ written in Python.

Getting Started
---------------

In order to get the app running, you must first installed the following prerequisites. These instruction will assume you're running Mac OS X with `Homebrew <http://mxcl.github.com/homebrew/>`_ as package manager and setting up a development environment.

- `Python 2.7 <http://www.python.org/>`_ (only 2.x series is supported). Using `virtualenv <http://pypi.python.org/pypi/virtualenv>`_ is recommended but not required.::

    $ brew install python

- `Stylus <http://learnboost.github.com/stylus/>`_ and `nib <https://github.com/visionmedia/nib/>`_. You may also need to install `node.js <http://nodejs.org/>`_ and add ``/usr/local/share/npm/bin/`` to your ``$PATH``. These dependencies are required for assets compiling:::

    $ brew install nodejs
    $ npm install -g stylus
    $ npm install -g nib

- `YUI Compressor <http://developer.yahoo.com/yui/compressor/css.html>`_, `requirejs <http://requirejs.org/>`_. and `UglifyJS <https://github.com/mishoo/UglifyJS>`_. These are required for packing assets into one file in production. You don't need these in development (although it's a good idea to install it.)::

    $ brew install yuicompressor
    $ npm install -g uglify-js
    $ npm install -g requirejs

After all prerequisites are installed, you can now run setup and seed the database.::

    $ python setup.py develop
    $ alembic upgrade head

It is recommended to run tests and see if all tests passed.::

    $ nosetests

If all tests passed, you can now run the application. You should also run ``make`` to compile all assets before running.::

    $ make
    $ pserve development.ini --reload

You may also found ``make watch`` useful for automatic assets compilation.::

    $ brew install watch
    $ make watch

License
---------------

Copyright (c) 2013, Kridsada Thanabulpong
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
Neither the name of the <ORGANIZATION> nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
0.10.0
======

- Changed from `CPython 3.2 <https://www.python.org/download/releases/3.2.5/>`_ to `PyPy 2.3 <http://pypy.org/download.html>`_.
- Changed from `Jinja2 <http://jinja.pocoo.org/>`_ templates with `Mako <http://www.makotemplates.org/>`_ template.
- Changed the board design and rewrite all templates.
- Refactored Pyramid views into modules.
- Refactored views to use function dispatching instead of class-based one.
- Removed all usage of ``pyramid.threadlocal``.
- Removed production provisioning from main repo.
- Added type annotation in methods as a hint for IDE.
- Added basic API views.

0.8.3
-----

- Changed how post processing failures are handle to no longer rely on `Celery <http://www.celeryproject.org>`_'s exceptions.
- Added cross-board reference syntax with the syntax of ">>>/board/topic/anchor" (e.g. ">>>/demo/123/10-11").

0.8.2
-----

- Fixed Akismet never timed out causing post to hang forever.

0.8.1
-----

- Fixed broken debug toolbar in development mode due to Python 3.2.3 bug.
- Removed pyramid_zcml and webtest from application requirements.
- Changed Celery process runner to no longer load Pyramid environment.

0.8.0
-----

- Changed post processing to use `Celery <http://www.celeryproject.org>`_ instead.

0.7.2
-----

- Added posting via AJAX in both quick reply and normal reply.
- Changed "New since visit" button to "Reload posts" via AJAX.

0.7.1
-----

- Changed existing pure-JavaScript to `jQuery <http://jquery.com>`_ and `CoffeeScript <http://coffeescript.org>`_.
- Changed styling for post number to indicate bump status.
- Added bump status remembering per topic.

0.7.0
-----

- Added reply number autofill when clicking on post number in reply page.
- Added inline reply when clicking on post number in listing page.
- Added a flag to bump or not bump post when replying.

0.6.2
-----

- Changed the way `Redis-py <https://redis-py.readthedocs.org>`_ is initialized by using late binding.
- Changed implementation of user ident generator and avoid accessing `Pyramid registry <http://docs.pylonsproject.org/projects/pyramid/en/latest/glossary.html#term-application-registry>`_.
- Added `dogpile.cache <http://dogpilecache.readthedocs.org>`_ support for caching.
- Added template caching for posts using `Memcached <http://memcached.org>`_.

0.6.1
-----

- Changed from `Puppet <http://puppetlabs.com>`_ provisioning to `Ansible <http://www.ansibleworks.com>`_ provisioning.
- Fixed slow navigation bar animation in iOS 7 and Mavericks.
- Fixed display error when thumbnail and read more posts are displayed together.

0.6.0
-----

- Changed stylings in all topic list page and reduce font size for 11th posts and on.
- Added posts abbreviation for post exceeding 500 characters in topic list page.
- Added per-board posting rate limit.
- Added temporary favicon.

0.5.1
-----

- Fixed error when board description does not exists.
- Fixed installation error due to import within setup.py.
- Fixed post count not in sync with post number issue.
- Fixed post display issue when post count is not equal to latest post number.

0.5.0
-----

- Changed from `traversal <http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/traversal.html>`_ to URL dispatching for reduced complexity.
- Added `Akismet <http://akismet.com>`_ integration for SPAM detection in comments.

0.4.0
-----

- Changed redirect path after reply to last 5 posts instead of full topic.
- Changed link target for topic title to recent posts instead of full topic.
- Changed header design to be no longer dependent to number of boards.
- Changed popover for post anchor to support ranged posts.
- Changed popover to no longer dismiss if user try to mouse over it.
- Changed assets path timestamp to file hash for smarter cache expiration.
- Fixed stylings for error page when post wasn't successful.
- Fixed character count in form is incorrectly counted due to DOS newline.
- Added top-right and bottom-right buttons for jumping to header and footer.
- Added auto-link functionality.

0.3.0
-----

- Changed from fluid layout to fixed 980px layout for widescreen responsive level.
- Changed all posts page to be mobile-optimized similar to board list page.
- Added timestamp to all assets path for cache expiration.
- Added thumbnail preview support for `Imgur <https://imgur.com>`_ links.
- Added popover for post anchor (single post only).
- Added proper page title to all user visible pages.

0.2.0
-----

- Added `CSRF token <http://wtforms.simplecodes.com/docs/1.0.3/ext.html#module-wtforms.ext.csrf>`_ support in forms.
- Added support for `Beaker <https://github.com/Pylons/pyramid_beaker/>`_ as session factory.
- Changed from `Bootstrap <http://twitter.github.com/bootstrap/>`_-based templates to a custom-made one.
- Changed from Makefile-based assets compilation to `Brunch <http://brunch.io/>`_.
- Changed minimum support Python version to 3.2 (was Python 3.3).
- Changed to use `Vagrant <http://www.vagrantup.com/>`_ for environment provisioning.

0.1.0
-----

-  Initial version

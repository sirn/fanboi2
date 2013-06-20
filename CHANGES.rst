0.5.1
=====

- Fixed error when board description does not exists.
- Fixed installation error due to import within setup.py.
- Fixed post count not in sync with post number issue.
- Fixed post display issue when post count is not equal to latest post number.

0.5.0
-----

- Changed from traversal to URL dispatching for reduced complexity.
- Added Akismet integration for SPAM detection in comments.

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
- Added thumbnail preview support for Imgur links.
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

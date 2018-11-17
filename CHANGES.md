# 2018.11

-   [Change] Memcached cache backend has been replaced with Redis cache backend.
-   [Change] Banning rules is now part of base rules system.

## 0.30.0

-   [Add] Admin panel at /admin.
-   [Add] Topic view now has canonical link.
-   [Change] Major refactoring to utilizes [pyramid_services](https://github.com/mmerickel/pyramid_services).
-   [Change] Application now uses environment variable as a primary means for configuration.
-   [Change] Switch to use [Pyramid's native CSRF checking](https://docs.pylonsproject.org/projects/pyramid/en/latest/api/csrf.html).
-   [Change] Switch to use [PyNaCl](https://github.com/Pylons/pyramid_nacl_session/) for session factory.
-   [Remove] Override rules are now removed as it add unnecessary complexity.
-   [Remove] Country configuration for post filter is now removed in favor for recently seen.

## 0.10.2

-   [Add] Allow post filter to be configured per country.
-   [Add] A `fb2_topic_sync` script for syncing topic's bumped timestamp.
-   [Fix] CSRF check now use constant-time comparison to prevent timing attack.
-   [Change] Requires minimum of 5 characters for post body.
-   [Change] Codebase now uses [Python 3.6](https://docs.python.org/3.6/whatsnew/changelog.html#python-3-6-4-final).

## 0.10.1

-   [Add] A `board` query string for expanding board from topic API.
-   [Add] A `topic` query string for expanding post from post API.
-   [Change] Switch to [Yarn](https://yarnpkg.com/) for assets package management.
-   [Change] Stylings of appendix section is now consistent with the footer.

## 0.10.0

-   [Add] Basic API for board, topic and post operations.
-   [Add] Dark theme ("Obsidian").
-   [Add] Banning rules allowing an IP address to be blocked.
-   [Add] Proxy detection allowing open proxies and public VPNs to be blocked.
-   [Add] Overriding rules allowing board status to be overridden per IP address.
-   [Add] Board can now be locked or archived.
-   [Add] Board, topic and post will now create a history copy on change.
-   [Add] Custom pages for guidelines or site customization ("internal pages").
-   [Add] YouTube videos now display a thumbnail.
-   [Add] More random quotes.
-   [Fix] Imgur album and gallery now no longer matched in thumbnail extractor.
-   [Change] Rewrite all board templates.
-   [Change] Application settings can now be override via environment variables.
-   [Change] Codebase now comes with type annotation for IDE.
-   [Change] Codebase now uses [Python 3.5](https://docs.python.org/3.5/whatsnew/changelog.html#python-3-5-2).
-   [Change] Replaced [Jinja2](http://jinja.pocoo.org/) templates with [Mako](http://www.makotemplates.org/) templates.
-   [Change] Views, models, utils and formatters are now organized into modules.
-   [Change] Views now use function dispatching instead of class-based dispatching.
-   [Change] Celery worker now load full Pyramid environment again to simplify initialization.
-   [Change] Vagrant now use [FreeBSD 10.3](https://www.freebsd.org/) instead of [Ubuntu 12.04](http://releases.ubuntu.com/precise/) to match the new production stack.
-   [Remove] Get rid of all usage of `pyramid.threadlocal`.
-   [Remove] Production provisioning is now private.

## 0.8.3

-   [Add] Referencing post cross-board is now possible with ">>>/board/topic/anchor" syntax (e.g. ">>>/demo/123/10-11").
-   [Change] Post errors reporting now no longer rely on [Celery](http://www.celeryproject.org)'s exceptions.

## 0.8.2

-   [Fix] Akismet now properly timed out and will no longer cause posting to hang forever.

## 0.8.1

-   [Fix] Debug toolbar is now working development mode again (caused by Python 3.2.3 bug).
-   [Change] Celery worker no longer load full Pyramid environment.
-   [Remove] No longer use pyramid_zcml and webtest.

## 0.8.0

-   [Change] Posts are now processed in a separate worker (using [Celery](http://www.celeryproject.org).

## 0.7.2

-   [Change] Posting is now done via AJAX in both inline reply and normal reply.
-   [Change] "New since visit" button is now "Reload posts" using AJAX.

## 0.7.1

-   [Change] Bump status is now remembered per topic.
-   [Change] Use [jQuery](http://jquery.com) and [CoffeeScript](http://coffeescript.org).
-   [Change] Update the post number styling to indicate bump status.

## 0.7.0

-   [Add] When replying, user can now choose to bump topic or to not bump.
-   [Add] Clicking on post number in reply page will now auto-fill the reply textarea.
-   [Add] Clicking on post number in listing page will now display inline reply box.

## 0.6.2

-   [Add] Caching support with [dogpile.cache](http://dogpilecache.readthedocs.org).
-   [Add] Templates could now be cached using [Memcached](http://memcached.org).
-   [Change] Initialize [Redis-py](https://redis-py.readthedocs.org) with late-binding to remove [Pyramid registry](http://docs.pylonsproject.org/projects/pyramid/en/latest/glossary.html#term-application-registry) access.
-   [Change] Ident generator now no longer accessing Pyramid registry.

## 0.6.1

-   [Fix] The layout no longer collapse when read more posts and thumbnails are displayed together.
-   [Change] Use [Ansible](http://www.ansibleworks.com) for provisioning instead of [Puppet](http://puppetlabs.com).
-   [Change] Navigation bar now overlay content to workaround slow DOM update in iOS 7 and Mavericks.

## 0.6.0

-   [Add] Temporary favicon.
-   [Change] Posts exceeding 500 characters in topic list will now be abbreviated.
-   [Change] Rate limit could now be set per-board.
-   [Change] stylings in all topic list page and reduce font size for 11th posts and on.

## 0.5.1

-   [Fix] Site will no longer error when board description does not exists.
-   [Fix] Fix an installation error due to import within setup.py.
-   [Fix] Post count now takes deleted posts into consideration.
-   [Fix] Posts are now properly displayed regardless of post count.

## 0.5.0

-   [Add] Integration with [Akismet](http://akismet.com) for SPAM detection in comments.
-   [Change] Use URL dispatching instead of [traversal](http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/traversal.html) to reduce complexity.

## 0.4.0

-   [Add] Add top-right and bottom-right buttons for jumping to header and footer.
-   [Add] Automatically turning text into links.
-   [Add] Post anchor popover now support ranged posts.
-   [Fix] Adjust stylings for error page when post wasn't successful.
-   [Fix] Character count in form now correctly take DOS newline into consideration.
-   [Fix] popover to no longer dismiss if user try to mouse over it.
-   [Change] Move redirect path after reply to last 5 posts instead of full topic.
-   [Change] Change link target for topic title to recent posts instead of full topic.
-   [Change] Update header design to be no longer dependent to number of boards.
-   [Change] Use file hash instead of timestamp for smarter cache expiration.

## 0.3.0

-   [Add] All assets path now has timestamp appended to it for cache expiration.
-   [Add] Image links from [Imgur](https://imgur.com) now show thumbnail preview.
-   [Add] Mouseover post anchor now display a post popover (single post only).
-   [Add] All use-facing pages now has proper page title.
-   [Change] Use a fixed 980px layout for widescreen responsive level instead of fluid layout.
-   [Change] Use the same mobile-optimized layout similar to board listing page in all posts page.

## 0.2.0

-   [Add] Forms now require [CSRF token](http://wtforms.simplecodes.com/docs/1.0.3/ext.html#module-wtforms.ext.csrf) to be present.
-   [Change] Switch to use [Beaker](https://github.com/Pylons/pyramid_beaker/) for session factory.
-   [Change] Use a custom-made template instead of [Bootstrap](http://twitter.github.com/bootstrap/).
-   [Change] Replaced Makefile-based assets compilation with [Brunch](http://brunch.io/).
-   [Change] Support Python 3.2 as minimal version (was Python 3.3).
-   [Change] Use [Vagrant](http://www.vagrantup.com/) for environment provisioning.

## 0.1.0

-   Initial version

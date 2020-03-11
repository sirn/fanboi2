import binascii
import hashlib
import logging
import os
from functools import lru_cache

from dotenv import load_dotenv, find_dotenv
from pyramid.config import Configurator
from pyramid.csrf import SessionCSRFStoragePolicy
from pyramid.path import AssetResolver
from pyramid.settings import asbool
from pyramid_nacl_session import EncryptedCookieSessionFactory


class NoValue(object):  # pragma: no cover
    """Base class for representing ``NO_VALUE`` to differentiate from
    absent of value and :type:`None`, e.g. in settings, where :type:`None`
    might be an acceptable value, but absent of value may not.
    """

    def __repr__(self):
        return "NO_VALUE"


NO_VALUE = NoValue()


ENV_SETTINGS_MAP = (
    ("AUTH_SECRET", "auth.secret", NO_VALUE, None),
    ("CELERY_BROKER_URL", "celery.broker", NO_VALUE, None),
    ("DATABASE_URL", "sqlalchemy.url", NO_VALUE, None),
    ("GEOIP_PATH", "geoip.path", None, None),
    ("REDIS_URL", "redis.url", NO_VALUE, None),
    ("SERVER_DEV", "server.development", False, asbool),
    ("SERVER_SECURE", "server.secure", False, asbool),
    ("SESSION_SECRET", "session.secret", NO_VALUE, None),
)

LOGGING_FMT = "%(asctime)s %(levelname)s %(name)s[%(process)d] %(message)s"
LOGGING_DATEFMT = "%H:%M:%S"


def route_name(request):
    """Returns :attr:`name` of current :attr:`request.matched_route`.

    :param request: A :class:`pyramid.request.Request` object.
    """
    if request.matched_route:
        return request.matched_route.name


@lru_cache(maxsize=10)
def _get_asset_hash(path):
    """Returns an MD5 hash of the given assets path.

    :param path: An asset specification to the asset file.
    """
    if ":" in path:
        package, path = path.split(":")
        resolver = AssetResolver(package)
    else:
        resolver = AssetResolver()
    fullpath = resolver.resolve(path).abspath()
    md5 = hashlib.md5()
    with open(fullpath, "rb") as f:
        for chunk in iter(lambda: f.read(128 * md5.block_size), b""):
            md5.update(chunk)
    return md5.hexdigest()


def tagged_static_path(request, path, **kwargs):
    """Similar to Pyramid's :meth:`request.static_path` but append first 8
    characters of file hash as query string ``h`` to it forcing proxy server
    and browsers to expire cache immediately after the file is modified.

    :param request: A :class:`pyramid.request.Request` object.
    :param path: An asset specification to the asset file.
    :param kwargs: Arguments to pass to :meth:`request.static_path`.
    """
    kwargs["_query"] = {"h": _get_asset_hash(path)[:8]}
    return request.static_path(path, **kwargs)


def settings_from_env(settings_map=ENV_SETTINGS_MAP, environ=os.environ):
    """Reads environment variable into Pyramid-style settings."""
    settings = {}

    load_dotenv(find_dotenv())

    for env, rkey, default, fn in settings_map:
        value = environ.get(env, default)
        if value is NO_VALUE:
            raise RuntimeError("{} is not set".format(env))
        if fn is not None:
            value = fn(value)
        settings[rkey] = value
    return settings


def tm_maybe_activate(request):
    """Returns whether should the transaction manager be activated."""
    return not request.path_info.startswith("/static/")


def setup_logger(settings):  # pragma: no cover
    """Setup logger per configured in settings."""
    log_level = logging.WARN
    if settings["server.development"]:
        log_level = logging.DEBUG
    logging.basicConfig(level=log_level, format=LOGGING_FMT, datefmt=LOGGING_DATEFMT)


def make_config(settings):  # pragma: no cover
    """Returns a Pyramid configurator."""
    config = Configurator(settings=settings)
    config.add_settings(
        {
            "mako.directories": "fanboi2:templates",
            "dogpile.backend": "dogpile.cache.redis",
            "dogpile.arguments.url": config.registry.settings["redis.url"],
            "dogpile.redis_expiration_time": 60 * 60 * 1,  # 1 hour
            "dogpile.arguments.distributed_lock": True,
            "tm.activate_hook": tm_maybe_activate,
        }
    )

    if config.registry.settings["server.development"]:
        config.add_settings(
            {
                "pyramid.reload_templates": True,
                "pyramid.debug_authorization": True,
                "pyramid.debug_notfound": True,
                "pyramid.default_locale_name": "en",
                "debugtoolbar.hosts": "0.0.0.0/0",
            }
        )
        config.include("pyramid_debugtoolbar")

    config.include("pyramid_mako")
    config.include("pyramid_services")

    session_secret_hex = config.registry.settings["session.secret"].strip()
    session_secret = binascii.unhexlify(session_secret_hex)
    session_factory = EncryptedCookieSessionFactory(
        session_secret, cookie_name="_session", timeout=3600, httponly=True
    )

    config.set_session_factory(session_factory)
    config.set_csrf_storage_policy(SessionCSRFStoragePolicy(key="_csrf"))
    config.add_request_method(route_name, property=True)
    config.add_request_method(tagged_static_path)
    config.add_route("robots", "/robots.txt")

    config.include("fanboi2.auth")
    config.include("fanboi2.cache")
    config.include("fanboi2.filters")
    config.include("fanboi2.geoip")
    config.include("fanboi2.models")
    config.include("fanboi2.redis")
    config.include("fanboi2.serializers")
    config.include("fanboi2.services")
    config.include("fanboi2.tasks")

    config.include("fanboi2.views.admin", route_prefix="/admin")
    config.include("fanboi2.views.api", route_prefix="/api")
    config.include("fanboi2.views.pages", route_prefix="/pages")
    config.include("fanboi2.views.boards", route_prefix="/")
    config.add_static_view("static", "static", cache_max_age=3600)

    return config

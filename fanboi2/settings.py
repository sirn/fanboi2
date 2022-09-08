import os
from typing import Dict, Union

from dotenv import find_dotenv, load_dotenv
from pyramid.settings import asbool  # type: ignore


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
    ("SERVER_ESI", "server.esi", False, asbool),
    ("SESSION_SECRET", "session.secret", NO_VALUE, None),
)


def settings_from_env(
    settings_map=ENV_SETTINGS_MAP,
    environ=os.environ,
) -> Dict[str, Union[int, str, bool]]:
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

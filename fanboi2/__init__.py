import os
import pyramid_jinja2
import redis
from functools import lru_cache
from IPy import IP
from pyramid.config import Configurator
from pyramid.events import NewRequest
from pyramid.path import AssetResolver
from pyramid_beaker import session_factory_from_settings
from sqlalchemy import engine_from_config
from .formatters import *
from .models import DBSession, Base
from .resources import RootFactory


def remote_addr(request):
    """Similar to built-in ``request.remote_addr`` but will fallback to
    ``HTTP_X_FORWARDED_FOR`` if defined and ``REMOTE_ADDR`` is private or
    loopback address.
    """
    ipaddr = IP(request.environ.get('REMOTE_ADDR', '255.255.255.255'))
    if ipaddr.iptype() == "PRIVATE":
        return request.environ.get('HTTP_X_FORWARDED_FOR', str(ipaddr))
    return str(ipaddr)


@lru_cache(maxsize=10)
def _get_asset_mtime(path):
    if ':' in path:
        package, path = path.split(':')
        resolver = AssetResolver(package)
    else:
        resolver = AssetResolver()
    fullpath = resolver.resolve(path).abspath()
    return int(os.path.getmtime(fullpath))


def tagged_static_path(request, path, **kwargs):
    """Similar to built-in :meth:`request.static_path` but appends last
    modified time of asset as query string ``t`` to it forcing proxy server
    and browsers to expire cache immediately after the file is modified.
    """
    kwargs['_query'] = {'t': _get_asset_mtime(path)}
    return request.static_path(path, **kwargs)


def main(global_config, **settings):  # pragma: no cover
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    session_factory = session_factory_from_settings(settings)
    config = Configurator(settings=settings)
    config.set_session_factory(session_factory)
    config.set_root_factory(RootFactory)
    config.set_request_property(remote_addr)
    config.add_request_method(tagged_static_path)
    config.include(pyramid_jinja2)

    # Redis setup.
    redis_conn = redis.StrictRedis.from_url(settings['redis.url'])
    config.registry.settings['redis_conn'] = redis_conn
    def _add_redis(event):
        settings = event.request.registry.settings
        event.request.redis = settings['redis_conn']
    config.add_subscriber(_add_redis, NewRequest)

    jinja2_env = config.get_jinja2_environment()
    jinja2_env.filters['datetime'] = format_datetime
    jinja2_env.filters['formatpost'] = format_post
    jinja2_env.filters['isotime'] = format_isotime
    jinja2_env.filters['markdown'] = format_markdown
    jinja2_env.filters['markup'] = format_text

    config.add_static_view('static', path='static', cache_max_age=3600)
    config.scan()
    return config.make_wsgi_app()

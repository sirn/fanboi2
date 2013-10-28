import hashlib
import pkg_resources
import pyramid_jinja2
import pyramid_zcml
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
from .cache import cache_region, Jinja2CacheExtension


__VERSION__ = pkg_resources.require('fanboi2')[0].version


def remote_addr(request):
    """Similar to built-in ``request.remote_addr`` but will fallback to
    ``HTTP_X_FORWARDED_FOR`` if defined and ``REMOTE_ADDR`` is private or
    loopback address.
    """
    ipaddr = IP(request.environ.get('REMOTE_ADDR', '255.255.255.255'))
    if ipaddr.iptype() == "PRIVATE":
        return request.environ.get('HTTP_X_FORWARDED_FOR', str(ipaddr))
    return str(ipaddr)


def route_name(request):
    """Returns :attr:`name` of current :attr:`request.matched_route`."""
    return request.matched_route.name


@lru_cache(maxsize=10)
def _get_asset_hash(path):
    if ':' in path:
        package, path = path.split(':')
        resolver = AssetResolver(package)
    else:
        resolver = AssetResolver()
    fullpath = resolver.resolve(path).abspath()
    md5 = hashlib.md5()
    with open(fullpath, 'rb') as f:
        for chunk in iter(lambda: f.read(128 * md5.block_size), b''):
            md5.update(chunk)
    return md5.hexdigest()


def tagged_static_path(request, path, **kwargs):
    """Similar to built-in :meth:`request.static_path` but append first 8
    characters of file hash as query string ``h`` to it forcing proxy server
    and browsers to expire cache immediately after the file is modified.
    """
    kwargs['_query'] = {'h': _get_asset_hash(path)[:8]}
    return request.static_path(path, **kwargs)


def main(global_config, **settings):  # pragma: no cover
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.',
                                client_encoding='utf8')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    session_factory = session_factory_from_settings(settings)
    cache_region.configure_from_config(settings, 'dogpile.')
    cache_region.invalidate()

    config = Configurator(settings=settings)
    config.set_session_factory(session_factory)
    config.set_request_property(remote_addr)
    config.set_request_property(route_name)
    config.add_request_method(tagged_static_path)

    config.include(pyramid_jinja2)
    config.include(pyramid_zcml)

    redis_conn = redis.StrictRedis.from_url(settings['redis.url'])
    config.registry.settings['redis_conn'] = redis_conn
    def _add_redis(event):
        settings = event.request.registry.settings
        event.request.redis = settings['redis_conn']
    config.add_subscriber(_add_redis, NewRequest)

    config.add_jinja2_extension(Jinja2CacheExtension)
    jinja2_env = config.get_jinja2_environment()
    jinja2_env.cache_region = cache_region
    jinja2_env.cache_expire = 3600

    jinja2_env.filters['datetime'] = format_datetime
    jinja2_env.filters['formatpost'] = format_post
    jinja2_env.filters['isotime'] = format_isotime
    jinja2_env.filters['markdown'] = format_markdown
    jinja2_env.filters['markup'] = format_text

    config.load_zcml('routes.zcml')
    config.scan()
    return config.make_wsgi_app()

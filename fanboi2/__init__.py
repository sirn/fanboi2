import hashlib
import pyramid_jinja2
from functools import lru_cache
from IPy import IP
from pyramid.config import Configurator
from pyramid.exceptions import NotFound
from pyramid.path import AssetResolver
from pyramid.view import append_slash_notfound_view
from pyramid_beaker import session_factory_from_settings
from sqlalchemy import engine_from_config
from .cache import cache_region, Jinja2CacheExtension
from .formatters import *
from .models import DBSession, Base, redis_conn, identity
from .utils import akismet, dnsbl


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


def configure_components(cfg):  # pragma: no cover
    """Configure the application components e.g. database connection."""
    # BUG: configure_components should be called after pyramid.Configurator
    # in order to prevent an importlib bug to cause pkg_resources to fail.
    # Tasks are imported here because of the same reason (Celery uses
    # importlib internally.)
    #
    # This bug only applies to Python 3.2.3 only.
    from .tasks import celery, configure_celery
    engine = engine_from_config(cfg, 'sqlalchemy.', client_encoding='utf8')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    redis_conn.from_url(cfg['redis.url'])
    celery.config_from_object(configure_celery(cfg))
    identity.configure_tz(cfg['app.timezone'])
    akismet.configure_key(cfg['akismet.key'])
    dnsbl.configure_providers(cfg['dnsbl.providers'])
    cache_region.configure_from_config(cfg, 'dogpile.')
    cache_region.invalidate()


def main(global_config, **settings):  # pragma: no cover
    """This function returns a Pyramid WSGI application."""
    session_factory = session_factory_from_settings(settings)
    config = Configurator(settings=settings)
    configure_components(settings)

    config.set_session_factory(session_factory)
    config.set_request_property(remote_addr)
    config.set_request_property(route_name)
    config.add_request_method(tagged_static_path)

    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('root', '/')
    config.add_route('board', '/{board:\w+}/')
    config.add_route('board_all', '/{board:\w+}/all/')
    config.add_route('board_new', '/{board:\w+}/new/')
    config.add_route('topic', '/{board:\w+}/{topic:\d+}/')
    config.add_route('topic_scoped', '/{board:\w+}/{topic:\d+}/{query}/')
    config.add_view(append_slash_notfound_view, context=NotFound)

    config.include(pyramid_jinja2)
    config.add_jinja2_extension(Jinja2CacheExtension)
    jinja2_env = config.get_jinja2_environment()
    jinja2_env.cache_region = cache_region

    jinja2_env.filters['datetime'] = format_datetime
    jinja2_env.filters['formatpost'] = format_post
    jinja2_env.filters['isotime'] = format_isotime
    jinja2_env.filters['markdown'] = format_markdown
    jinja2_env.filters['markup'] = format_text
    config.scan()

    return config.make_wsgi_app()

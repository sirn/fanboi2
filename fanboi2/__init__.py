import hashlib
from functools import lru_cache
from IPy import IP
from pyramid.config import Configurator
from pyramid.exceptions import NotFound
from pyramid.path import AssetResolver
from pyramid.view import append_slash_notfound_view
from pyramid_beaker import session_factory_from_settings
from sqlalchemy.engine import engine_from_config
from .cache import cache_region
from .models import DBSession, Base, redis_conn, identity
from .serializers import json_renderer
from .utils import akismet, dnsbl


def remote_addr(request):
    """Similar to Pyramid's :attr:`request.remote_addr` but will fallback
    to ``HTTP_X_FORWARDED_FOR`` when ``REMOTE_ADDR`` is either a private
    address or a loopback address.

    :param request: A :class:`pyramid.request.Request` object.

    :type request: pyramid.request.Request
    :rtype: str
    """
    ipaddr = IP(request.environ.get('REMOTE_ADDR', '255.255.255.255'))
    if ipaddr.iptype() == "PRIVATE":
        return request.environ.get('HTTP_X_FORWARDED_FOR', str(ipaddr))
    return str(ipaddr)


def route_name(request):
    """Returns :attr:`name` of current :attr:`request.matched_route`.

    :param request: A :class:`pyramid.request.Request` object.

    :type request: pyramid.request.Request
    :rtype: str
    """
    return request.matched_route.name


@lru_cache(maxsize=10)
def _get_asset_hash(path):
    """Returns an MD5 hash of the given assets path.

    :param path: An asset specification to the asset file.

    :type param: str
    :rtype: str
    """
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
    """Similar to Pyramid's :meth:`request.static_path` but append first 8
    characters of file hash as query string ``h`` to it forcing proxy server
    and browsers to expire cache immediately after the file is modified.

    :param request: A :class:`pyramid.request.Request` object.
    :param path: An asset specification to the asset file.
    :param kwargs: Arguments to pass to :meth:`request.static_path`.

    :type request: pyramid.request.Request
    :type path: str
    :type kwargs: dict
    :rtype: str
    """
    kwargs['_query'] = {'h': _get_asset_hash(path)[:8]}
    return request.static_path(path, **kwargs)


def configure_components(cfg):  # pragma: no cover
    """Configure the application components e.g. database connection.

    :param cfg: A configuration :type:`dict`.

    :type cfg: dict
    :rtype: None
    """
    # BUG: configure_components should be called after pyramid.Configurator
    # in order to prevent an importlib bug to cause pkg_resources to fail.
    # Tasks are imported here because of the same reason (Celery uses
    # importlib internally.)
    #
    # This bug only applies to Python 3.2.3 only.
    from .tasks import celery, configure_celery
    engine = engine_from_config(cfg, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    redis_conn.from_url(cfg['redis.url'])
    celery.config_from_object(configure_celery(cfg))
    identity.configure_tz(cfg['app.timezone'])
    akismet.configure_key(cfg['app.akismet_key'])
    dnsbl.configure_providers(cfg['app.dnsbl_providers'])
    cache_region.configure_from_config(cfg, 'dogpile.')
    cache_region.invalidate()


def configure_views(config):  # pragma: no cover
    """Add views and routes to Pyramid configuration.

    :param config: A configuration :class:`pyramid.config.Configurator`.

    :type config: pyramid.config.Configurator
    :rtype: None
    """
    config.add_static_view('static', 'static', cache_max_age=3600)

    # views.api
    config.add_route('api_root',         '/api/')
    config.add_route('api_boards',       '/api/1.0/boards/')
    config.add_route('api_board',        '/api/1.0/boards/{board:\w+}/')
    config.add_route('api_board_topics', '/api/1.0/boards/{board:\w+}/topics/')
    config.add_route('api_topic',        '/api/1.0/topics/{topic:\d+}/')
    config.add_route('api_topic_posts',  '/api/1.0/topics/{topic:\d+}/posts/')
    config.add_route('api_topic_posts_scoped',
                     '/api/1.0/topics/{topic:\d+}/posts/{query}/')

    # views.pages
    config.add_route('root',         '/')
    config.add_route('board',        '/{board:\w+}/')
    config.add_route('board_all',    '/{board:\w+}/all/')
    config.add_route('board_new',    '/{board:\w+}/new/')
    config.add_route('topic',        '/{board:\w+}/{topic:\d+}/')
    config.add_route('topic_scoped', '/{board:\w+}/{topic:\d+}/{query}/')

    # Fallback
    config.add_view(append_slash_notfound_view, context=NotFound)
    config.scan()


def main(global_config, **settings):  # pragma: no cover
    """This function returns a Pyramid WSGI application.

    :param global_config: A :type:`dict` containing global config.
    :param settings: A :type:`dict` containing values from INI.

    :type global_config: dict
    :type settings: dict
    :rtype: pyramid.router.Router
    """
    session_factory = session_factory_from_settings(settings)
    config = Configurator(settings=settings)
    config.include('pyramid_mako')
    configure_components(settings)

    config.set_session_factory(session_factory)
    config.set_request_property(remote_addr)
    config.set_request_property(route_name)
    config.add_request_method(tagged_static_path)

    config.add_renderer('json', json_renderer)
    configure_views(config)

    return config.make_wsgi_app()

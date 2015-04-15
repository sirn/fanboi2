import hashlib
from functools import lru_cache
from IPy import IP
from pyramid.config import Configurator
from pyramid.path import AssetResolver
from pyramid_beaker import session_factory_from_settings
from sqlalchemy.engine import engine_from_config
from fanboi2.cache import cache_region
from fanboi2.models import DBSession, Base, redis_conn, identity
from fanboi2.utils import akismet, dnsbl


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
    if request.matched_route:
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


def configure_components(settings):  # pragma: no cover
    """Configure the application components e.g. database connection.

    :param settings: A configuration :type:`dict`.

    :type settings: dict
    :rtype: None
    """
    # Note: fanboi2.tasks is imported here since importlib used in celery
    # is causing pkg_resources to fail. This bug applies to Python 3.2.3.
    from fanboi2.tasks import celery, configure_celery
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    redis_conn.from_url(settings['redis.url'])
    celery.config_from_object(configure_celery(settings))
    identity.configure_tz(settings['app.timezone'])
    akismet.configure_key(settings['app.akismet_key'])
    dnsbl.configure_providers(settings['app.dnsbl_providers'])
    cache_region.configure_from_config(settings, 'dogpile.')
    cache_region.invalidate()


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
    configure_components(settings)
    config.include('pyramid_mako')

    config.set_session_factory(session_factory)
    config.set_request_property(remote_addr)
    config.set_request_property(route_name)
    config.add_request_method(tagged_static_path)

    config.include('fanboi2.serializers')
    config.include('fanboi2.views.api', route_prefix='/api')
    config.include('fanboi2.views.pages', route_prefix='/')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.scan()

    return config.make_wsgi_app()

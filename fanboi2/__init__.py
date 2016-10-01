import copy
import hashlib
import os
from functools import lru_cache
from ipaddress import ip_address
from pyramid.config import Configurator
from pyramid.path import AssetResolver
from pyramid.settings import aslist
from sqlalchemy.engine import engine_from_config
from fanboi2.cache import cache_region
from fanboi2.models import DBSession, Base, redis_conn, identity
from fanboi2.tasks import celery, configure_celery
from fanboi2.utils import akismet, dnsbl


def remote_addr(request):
    """Similar to Pyramid's :attr:`request.remote_addr` but will fallback
    to ``HTTP_X_FORWARDED_FOR`` when ``REMOTE_ADDR`` is either a private
    address or a loopback address.

    :param request: A :class:`pyramid.request.Request` object.

    :type request: pyramid.request.Request
    :rtype: str
    """
    ipaddr = ip_address(request.environ.get('REMOTE_ADDR', '255.255.255.255'))
    if ipaddr.is_private:
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


def normalize_settings(settings, _environ=os.environ):
    """Normalize settings to the correct format and merge it with environment
    equivalent if relevant key exists.

    :param settings: A settings :type:`dict`.

    :type settings: dict
    :rtype: dict
    """
    def _cget(env_key, settings_key):
        settings_val = settings.get(settings_key, '')
        return _environ.get(env_key, settings_val)

    sqlalchemy_url = _cget('SQLALCHEMY_URL', 'sqlalchemy.url')
    redis_url = _cget('REDIS_URL', 'redis.url')
    celery_broker_url = _cget('CELERY_BROKER_URL', 'celery.broker')
    dogpile_url = _cget('DOGPILE_URL', 'dogpile.arguments.url')
    session_url = _cget('SESSION_URL', 'session.url')
    session_secret = _cget('SESSION_SECRET', 'session.secret')

    app_timezone = _cget('APP_TIMEZONE', 'app.timezone')
    app_secret = _cget('APP_SECRET', 'app.secret')
    app_akismet_key = _cget('APP_AKISMET_KEY', 'app.akismet_key')
    app_dnsbl_providers = _cget('APP_DNSBL_PROVIDERS', 'app.dnsbl_providers')

    if app_dnsbl_providers is not None:
        app_dnsbl_providers = aslist(app_dnsbl_providers)

    _settings = copy.deepcopy(settings)
    _settings.update({
        'sqlalchemy.url': sqlalchemy_url,
        'redis.url': redis_url,
        'celery.broker': celery_broker_url,
        'dogpile.arguments.url': dogpile_url,
        'session.url': session_url,
        'session.secret': session_secret,
        'app.timezone': app_timezone,
        'app.secret': app_secret,
        'app.akismet_key': app_akismet_key,
        'app.dnsbl_providers': app_dnsbl_providers,
    })

    return _settings


def configure_components(settings):  # pragma: no cover
    """Configure the application components e.g. database connection.

    :param settings: A configuration :type:`dict`.

    :type settings: dict
    :rtype: None
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine

    cache_region.configure_from_config(settings, 'dogpile.')
    cache_region.invalidate()

    redis_conn.from_url(settings['redis.url'])
    celery.config_from_object(configure_celery(settings))
    identity.configure_tz(settings['app.timezone'])
    akismet.configure_key(settings['app.akismet_key'])
    dnsbl.configure_providers(settings['app.dnsbl_providers'])


def main(global_config, **settings):  # pragma: no cover
    """This function returns a Pyramid WSGI application.

    :param global_config: A :type:`dict` containing global config.
    :param settings: A :type:`dict` containing values from INI.

    :type global_config: dict
    :type settings: dict
    :rtype: pyramid.router.Router
    """
    settings = normalize_settings(settings)
    config = Configurator(settings=settings)
    configure_components(settings)
    config.include('pyramid_mako')
    config.include('pyramid_beaker')

    config.set_request_property(remote_addr)
    config.set_request_property(route_name)
    config.add_request_method(tagged_static_path)

    config.include('fanboi2.serializers')
    config.include('fanboi2.views.api', route_prefix='/api')
    config.include('fanboi2.views.pages', route_prefix='/')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.scan()

    return config.make_wsgi_app()

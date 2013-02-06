import pyramid_jinja2
import redis
from ipaddress import ip_address
from pyramid.config import Configurator
from pyramid.events import NewRequest
from sqlalchemy import engine_from_config
from .formatters import *
from .models import DBSession, Base
from .resources import RootFactory


def remote_addr(request):
    """Similar to built-in ``request.remote_addr`` but will fallback to
    ``HTTP_X_FORWARDED_FOR`` if defined and ``REMOTE_ADDR`` is private or
    loopback address.
    """
    ipaddr = ip_address(request.environ.get('REMOTE_ADDR', '255.255.255.255'))
    if ipaddr.is_private or ipaddr.is_loopback:
        return request.environ.get('HTTP_X_FORWARDED_FOR', str(ipaddr))
    return str(ipaddr)


def main(global_config, **settings):  # pragma: no cover
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    config = Configurator(settings=settings, root_factory=RootFactory)
    config.set_request_property(remote_addr)
    config.include(pyramid_jinja2)

    # TODO: Remove Redis usage (we only use it for ID generation)
    # Use some kind of hashing algorithm instead?
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

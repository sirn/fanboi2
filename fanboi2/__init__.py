import pyramid_jinja2
import pyramid_zcml
from ipaddr import IPAddress
from pyramid.config import Configurator
from sqlalchemy import engine_from_config
from .models import DBSession, Base
from .resources import RootFactory


def remote_addr(request):
    """Similar to built-in ``request.remote_addr`` but will fallback to
    ``HTTP_X_FORWARDED_FOR`` if defined and ``REMOTE_ADDR`` is private or
    loopback address.
    """
    ipaddr = IPAddress(request.environ.get('REMOTE_ADDR', '255.255.255.255'))
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
    config.include(pyramid_zcml)
    config.load_zcml('routes.zcml')
    config.scan()
    return config.make_wsgi_app()

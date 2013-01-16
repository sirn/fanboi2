import pyramid_jinja2
import pyramid_zcml
from pyramid.config import Configurator
from sqlalchemy import engine_from_config
from .models import DBSession, Base
from .resources import RootFactory


def main(global_config, **settings):  # pragma: no cover
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    config = Configurator(settings=settings, root_factory=RootFactory)
    config.include(pyramid_jinja2)
    config.include(pyramid_zcml)
    config.load_zcml('routes.zcml')
    config.scan()
    return config.make_wsgi_app()

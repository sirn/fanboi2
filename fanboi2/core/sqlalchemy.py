import logging

import transaction  # type: ignore
import zope.sqlalchemy  # type: ignore
from pyramid.config import Configurator  # type: ignore
from pyramid.request import Request  # type: ignore
from sqlalchemy.engine import engine_from_config
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

from ..models import Base, make_history_event


def tm_maybe_activate(request: Request) -> bool:
    """Returns whether should the transaction manager be activated."""
    return not request.path_info.startswith("/static/")


def init_dbsession(
    dbsession: Session,
    tm: transaction.manager = None,
):  # pragma: no cover
    """Initialize SQLAlchemy ``dbsession`` with application defaults."""
    zope.sqlalchemy.register(dbsession, transaction_manager=tm)


def includeme(config: Configurator):  # pragma: no cover
    config.include("pyramid_tm")
    config.add_settings({"tm.activate_hook": tm_maybe_activate})

    engine = engine_from_config(config.registry.settings, "sqlalchemy.")
    Base.metadata.bind = engine
    dbmaker = sessionmaker()
    dbmaker.configure(bind=engine)
    make_history_event(dbmaker)

    log_level = logging.WARN
    if config.registry.settings["server.development"]:
        log_level = logging.INFO

    logger = logging.getLogger("sqlalchemy.engine.base.Engine")
    logger.setLevel(log_level)

    def dbsession_factory(context, request):
        dbsession = dbmaker()
        init_dbsession(dbsession, tm=request.tm)
        return dbsession

    config.register_service_factory(dbsession_factory, name="db")

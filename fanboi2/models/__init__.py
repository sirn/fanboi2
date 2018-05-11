import logging

from sqlalchemy.engine import engine_from_config
from sqlalchemy.orm import sessionmaker
import zope.sqlalchemy

from ._base import Base
from ._versioned import make_history_event, setup_versioned
from .board import Board
from .group import Group
from .page import Page
from .post import Post
from .rule import Rule
from .rule_ban import RuleBan
from .setting import Setting
from .topic import Topic
from .topic_meta import TopicMeta
from .user import User
from .user_session import UserSession


__all__ = [
    'Base',
    'Board',
    'Group',
    'Page',
    'Post',
    'Rule',
    'RuleBan',
    'Setting',
    'Topic',
    'TopicMeta',
    'User',
    'UserSession',
]


_MODELS = {
    'board': Board,
    'group': Group,
    'page': Page,
    'post': Post,
    'rule': Rule,
    'rule_ban': RuleBan,
    'setting': Setting,
    'topic': Topic,
    'topic_meta': TopicMeta,
    'user': User,
    'user_session': UserSession,
}


# Versioned need to be setup after all models are initialized otherwise
# SQLAlchemy won't be able to locate relation tables due to import order.
setup_versioned()


def deserialize_model(type_):
    """Deserialize the given model type string into a model class."""
    return _MODELS.get(type_)


def init_dbsession(dbsession, tm=None):  # pragma: no cover
    """Initialize SQLAlchemy ``dbsession`` with application defaults.

    :param dbsession: A :class:`sqlalchemy.orm.session.Session` object.
    :param tm: A Zope transaction manager.
    """
    zope.sqlalchemy.register(dbsession, transaction_manager=tm)


def configure_sqlalchemy(settings):  # pragma: no cover
    """Configure SQLAlchemy with the given settings."""
    engine = engine_from_config(settings, 'sqlalchemy.')
    Base.metadata.bind = engine
    dbmaker = sessionmaker()
    dbmaker.configure(bind=engine)
    return dbmaker


def includeme(config):  # pragma: no cover
    config.include('pyramid_tm')
    dbmaker = configure_sqlalchemy(config.registry.settings)
    make_history_event(dbmaker)

    log_level = logging.WARN
    if config.registry.settings['server.development']:
        log_level = logging.INFO

    logger = logging.getLogger('sqlalchemy.engine.base.Engine')
    logger.setLevel(log_level)

    def dbsession_factory(context, request):
        dbsession = dbmaker()
        init_dbsession(dbsession, tm=request.tm)
        return dbsession

    config.register_service_factory(dbsession_factory, name='db')

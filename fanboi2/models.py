import datetime
import string
import hashlib
import json
import pytz
import random
import re
from pyramid.threadlocal import get_current_request
from sqlalchemy import Column, Integer, String, DateTime, Unicode, Text,\
    Enum, ForeignKey, TypeDecorator, UniqueConstraint, func, select,\
    desc, event
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import scoped_session, sessionmaker, relationship,\
    backref, column_property, synonym
from zope.interface import implementer
from zope.sqlalchemy import ZopeTransactionExtension
from .interfaces import IBoard, ITopic, IPost

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


RE_FIRST_CAP = re.compile('(.)([A-Z][a-z]+)')
RE_ALL_CAP = re.compile('([a-z0-9])([A-Z])')

DEFAULT_BOARD_CONFIG = {
    'name': 'Nameless Fanboi',
    'use_ident': True,
    'max_posts': 1000,
}


class JsonType(TypeDecorator):
    """Serializible field for storing data as JSON text. If the field is
    ``NULL`` in the database, a default value of empty :type:`dict` is
    returned on retrieval.
    """
    impl = Text

    def process_bind_param(self, value, dialect):
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        if not value:
            return {}
        return json.loads(value)


class BaseModel(object):
    """Primary mixin that provides common fields for SQLAlchemy models."""

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    @declared_attr
    def __tablename__(self):
        name = RE_FIRST_CAP.sub(r'\1_\2', self.__name__)
        return RE_ALL_CAP.sub(r'\1_\2', name).lower()

    def __init__(self, **kwargs):
        for key, value in list(kwargs.items()):
            setattr(self, key, value)


@implementer(IBoard)
class Board(BaseModel, Base):
    """Model class for board. This model serve as a category to topic and
    also holds settings regarding how posts are created and displayed. It
    should always be accessed using :attr:`slug`.
    """

    slug = Column(String(64), unique=True, nullable=False)
    title = Column(Unicode(255), nullable=False)
    _settings = Column('settings', JsonType, nullable=False, default={})
    agreements = Column(Text, nullable=True)
    description = Column(Text, nullable=True)

    def get_settings(self):
        settings = DEFAULT_BOARD_CONFIG.copy()
        settings.update(self._settings)
        return settings

    def set_settings(self, value):
        self._settings = value

    @declared_attr
    def settings(cls):
        return synonym('_settings', descriptor=property(cls.get_settings,
                                                        cls.set_settings))


@implementer(ITopic)
class Topic(BaseModel, Base):
    """Model class for topic. This model only holds topic metadata such as
    title or its associated board. The actual content of a topic belongs
    to :class:`Post`.
    """

    board_id = Column(Integer, ForeignKey('board.id'), nullable=False)
    title = Column(Unicode(255), nullable=False)
    status = Column(Enum('open', 'locked', 'archived', name='topic_status'),
                    default='open',
                    nullable=False)
    board = relationship('Board',
                         backref=backref('topics',
                                         lazy='dynamic',
                                         order_by='desc(Topic.posted_at)'))


@implementer(IPost)
class Post(BaseModel, Base):
    """Model class for posts. Each content in a :class:`Topic` and metadata
    regarding its poster are stored here. It has :attr:`number` which is a
    sequential number specifying its position within :class:`Topic`.
    """

    __table_args__ = (UniqueConstraint('topic_id', 'number'),)

    topic_id = Column(Integer, ForeignKey('topic.id'), nullable=False)
    ip_address = Column(String, nullable=False)
    ident = Column(String(32), nullable=True)
    number = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    body = Column(Text, nullable=False)
    topic = relationship('Topic',
                         backref=backref('posts',
                                         lazy='dynamic',
                                         order_by='Post.number'))


@event.listens_for(DBSession, 'before_flush')
def update_topic_status(session, context, instance):
    for model in filter(lambda m: isinstance(m, Post), session.new):
        topic = model.topic
        if topic.post_count is not None and \
                topic.status == 'open' and \
                topic.post_count >= (topic.board.settings['max_posts'] - 1):
            topic.status = 'archived'
            session.add(topic)


@event.listens_for(Post.__mapper__, 'before_insert')
def populate_post_number(mapper, connection, target):
    """Populate sequential :attr:`Post.number` in each topic."""
    # This will issue a subquery on every INSERT which may cause race
    # condition problem. Our UNIQUE CONSTRAINT will detect that, so the
    # calling code should retry accordingly.
    target.number = select([func.coalesce(func.max(Post.number), 0) + 1]).\
                    where(Post.topic_id == target.topic_id)


@event.listens_for(Post.__mapper__, 'before_insert')
def populate_post_name(mapper, connection, target):
    """Populate :attr:`Post.name` using name set within :attr:`Post.settings`
    if name is empty otherwise use user input.
    """
    if target.name is None:
        target.name = target.topic.board.settings['name']


def _generate_ident(ip_address):
    """Retrieve user ident from Redis or generate a new one if it does not
    already exists. Date is used as an ident key to ensure a new key is
    generated every day.
    """
    request = get_current_request()

    # Use timezone to generate date for ident key so it is reset at the same
    # time as displayed in the board.
    timezone = pytz.timezone(request.registry.settings['app.timezone'])
    today = datetime.datetime.now(timezone).strftime("%Y%m%d")
    key = "ident:%s:%s" % (today, hashlib.md5(ip_address.encode('utf8')).\
                                          hexdigest())

    # Generate ident if not exists and store it. Use SETNX to ensure we don't
    # overwrite the key if it somehow gets stored while code is running.
    ident = request.redis.get(key)
    if ident is None:
        strings = string.ascii_letters + string.digits + "+/."
        ident = ''.join(random.choice(strings) for x in range(9))
        request.redis.setnx(key, ident)
        request.redis.expire(key, 86400)
    else:
        ident = ident.decode('utf-8')
    return ident


@event.listens_for(Post.__mapper__, 'before_insert')
def populate_post_ident(mapper, connection, target):
    if target.topic.board.settings['use_ident']:
        target.ident = _generate_ident(target.ip_address)


Topic.post_count = column_property(
    select([func.count(Post.id)]).where(Post.topic_id == Topic.id),
    deferred=True,
)

Topic.posted_at = column_property(
    select([Post.created_at]).
        where(Post.topic_id == Topic.id).
        order_by(desc(Post.created_at)).
        limit(1),
    deferred=True,
)

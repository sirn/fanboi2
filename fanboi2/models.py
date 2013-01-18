import json
import re
from sqlalchemy import func, Column, Integer, String, DateTime, Unicode,\
    ForeignKey, select, desc, TypeDecorator, Binary
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import scoped_session, sessionmaker, relationship,\
    backref, column_property
from zope.interface import implementer
from zope.sqlalchemy import ZopeTransactionExtension
from .interfaces import IBoard, ITopic, IPost

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


RE_FIRST_CAP = re.compile('(.)([A-Z][a-z]+)')
RE_ALL_CAP = re.compile('([a-z0-9])([A-Z])')


class JsonType(TypeDecorator):
    impl = Binary

    def process_bind_param(self, value, dialect):
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        if not value:
            return {}
        return json.loads(value)


class BaseModel(object):
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    @declared_attr
    def __tablename__(self):
        name = RE_FIRST_CAP.sub(r'\1_\2', self.__name__)
        return RE_ALL_CAP.sub(r'\1_\2', name).lower()

    def __init__(self, **kwargs):
        for key, value in kwargs.iteritems():
            setattr(self, key, value)


@implementer(IBoard)
class Board(BaseModel, Base):
    slug = Column(String(64), unique=True, nullable=False)
    title = Column(Unicode(255), nullable=False)
    settings = Column(JsonType, nullable=False, default={})


@implementer(ITopic)
class Topic(BaseModel, Base):
    board_id = Column(Integer, ForeignKey('board.id'), nullable=False)
    title = Column(Unicode(255), nullable=False)
    board = relationship('Board',
                         backref=backref('topics',
                                         lazy='dynamic',
                                         order_by='desc(Topic.posted_at)'))


@implementer(IPost)
class Post(BaseModel, Base):
    topic_id = Column(Integer, ForeignKey('topic.id'), nullable=False)
    ip_address = Column(String, nullable=False)
    ident = Column(String(32), nullable=True)
    body = Column(Unicode, nullable=False)
    topic = relationship('Topic',
                         backref=backref('posts',
                                         order_by='Post.id'))

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

import re
from sqlalchemy import func, Column, Integer, String, DateTime, Unicode,\
    ForeignKey
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import scoped_session, sessionmaker, relationship, backref
from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


RE_FIRST_CAP = re.compile('(.)([A-Z][a-z]+)')
RE_ALL_CAP = re.compile('([a-z0-9])([A-Z])')


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


class Board(BaseModel, Base):
    slug = Column(String(64), unique=True, nullable=False)
    title = Column(Unicode(255), nullable=False)


class Topic(BaseModel, Base):
    board_id = Column(Integer, ForeignKey('board.id'), nullable=False)
    topic = Column(Unicode(255), nullable=False)
    board = relationship('Board', backref=backref('topics'))


class Post(BaseModel, Base):
    topic_id = Column(Integer, ForeignKey('topic.id'), nullable=False)
    body = Column(Unicode, nullable=False)
    topic = relationship('Topic', backref=backref('posts',
                                                  order_by='Post.id'))

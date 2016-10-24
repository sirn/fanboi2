from sqlalchemy import event
from sqlalchemy.orm import backref, relationship
from sqlalchemy.sql import func, select
from sqlalchemy.sql.schema import Column, ForeignKey, UniqueConstraint
from sqlalchemy.sql.sqltypes import Integer, DateTime, String, Text, Boolean
from ._base import Base, Versioned


class Post(Versioned, Base):
    """Model class for posts. Each content in a :class:`Topic` and metadata
    regarding its poster are stored here. It has :attr:`number` which is a
    sequential number specifying its position within :class:`Topic`.
    """

    __tablename__ = 'post'
    __table_args__ = (UniqueConstraint('topic_id', 'number'),)

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    topic_id = Column(Integer, ForeignKey('topic.id'), nullable=False)
    ip_address = Column(String, nullable=False)
    ident = Column(String(32), nullable=True)
    number = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    body = Column(Text, nullable=False)
    bumped = Column(Boolean, nullable=False, index=True, default=True)
    topic = relationship('Topic',
                         backref=backref('posts',
                                         lazy='dynamic',
                                         cascade='all,delete',
                                         order_by='Post.number'))


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


@event.listens_for(Post.__mapper__, 'before_insert')
def populate_post_ident(mapper, connection, target):
    from . import identity
    board = target.topic.board
    if board.settings['use_ident']:
        target.ident = identity.get(target.ip_address, board.slug)

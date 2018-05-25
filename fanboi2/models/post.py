from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.orm import backref, relationship
from sqlalchemy.sql import func
from sqlalchemy.sql.schema import Column, ForeignKey, UniqueConstraint
from sqlalchemy.sql.sqltypes import Integer, DateTime, String, Text, Boolean

from ._base import Base, Versioned
from ._type import IdentTypeEnum


class Post(Versioned, Base):
    """Model class for posts. Each content in a :class:`Topic` and metadata
    regarding its poster are stored here. It has :attr:`number` which is a
    sequential number specifying its position within :class:`Topic`.
    """

    __tablename__ = "post"
    __table_args__ = (UniqueConstraint("topic_id", "number"),)

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    topic_id = Column(Integer, ForeignKey("topic.id"), nullable=False)
    ip_address = Column(INET, nullable=False)
    ident = Column(String(32), nullable=True)
    ident_type = Column(IdentTypeEnum, default="none", nullable=False)
    number = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    body = Column(Text, nullable=False)
    bumped = Column(Boolean, nullable=False, index=True, default=True)

    topic = relationship(
        "Topic",
        backref=backref(
            "posts", lazy="dynamic", cascade="all,delete", order_by="Post.number"
        ),
    )

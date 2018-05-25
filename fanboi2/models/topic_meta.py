from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import Integer, DateTime
from ._base import Base


class TopicMeta(Base):
    """Model class that provides topic metadata. This model holds data that
    are related to internal workings of the topic model that are not part of
    the versionable records.
    """

    __tablename__ = "topic_meta"

    topic_id = Column(
        Integer,
        ForeignKey("topic.id"),
        nullable=False,
        primary_key=True,
        autoincrement=False,
    )

    post_count = Column(Integer, nullable=False)
    posted_at = Column(DateTime(timezone=True))
    bumped_at = Column(DateTime(timezone=True))

    topic = relationship(
        "Topic", backref=backref("meta", uselist=False, cascade="all,delete", lazy=True)
    )
